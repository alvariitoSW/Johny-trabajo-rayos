"""Paso 4 · Reproducibilidad interobservador (protocolo §8 y §11.3).

Para cada caso con dos segmentaciones (<entrada>/casos/<ID>/mascara_obs1.nii.gz y mascara_obs2.nii.gz):
  · Dice = 2·|A∩B| / (|A| + |B|). 1 = idénticas, 0 = sin solapamiento.
  · Hausdorff 95 (mm): distancias desde cada vóxel del borde de una máscara al borde más próximo de la otra, en
    los dos sentidos; se toma el percentil 95 de cada sentido y se informa el mayor de los dos. 0 = idénticas.
  · Se extraen las características con cada máscara (misma imagen, mismo params.yaml y mismo binWidth).
Por característica: ICC(2,1) de Shrout y Fleiss = modelo de dos factores de efectos aleatorios, acuerdo absoluto,
medida única (ICC(A,1) de McGraw y Wong), con su IC 95 %, calculado con pingouin («ICC2»). Se informan TODAS las
características, sin filtrar por ningún umbral de ICC.

Salida:  <salida>/reproducibilidad_segmentacion.csv   Dice y HD95 por caso
         <salida>/reproducibilidad_icc.csv            ICC e IC 95 % por característica
         <salida>/reproducibilidad_features.csv       características de cada observador (para auditar)
         <salida>/reproducibilidad_resumen.json       n de casos, aviso si hay menos de 15, Dice y HD95 (medianas)

Columnas añadidas al ICC (etiquetas, nunca filtros; no se quita ninguna fila):
  · fiabilidad_koo_li: etiqueta de Koo y Li 2016 según el IC 95 % entero (comun.fiabilidad_koo_li).
  · cautela: True si el límite inferior del IC 95 % es < 0,5. Texto: «interpretar con cautela: no se descarta
    una fiabilidad pobre».
Aviso: con menos de 15 casos con dos observadores (mínimo orientativo del protocolo §8) se avisa y se anota en el
resumen; el paso no se detiene.

Uso:  python src/04_reproducibilidad.py --entrada data --salida outputs [--binwidth 10]
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pingouin as pg
import SimpleITK as sitk
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402


def dice(a: np.ndarray, b: np.ndarray) -> float:
    total = int(a.sum()) + int(b.sum())
    return float('nan') if total == 0 else 2.0 * int((a & b).sum()) / total


def hd95(a: np.ndarray, b: np.ndarray, espaciado_zyx) -> float:
    """Hausdorff 95 simétrico (mm): el mayor de los dos percentiles 95 dirigidos entre bordes."""
    if not a.any() or not b.any():
        return float('nan')
    borde_a = a & ~ndimage.binary_erosion(a)
    borde_b = b & ~ndimage.binary_erosion(b)
    dist_a_b = ndimage.distance_transform_edt(~borde_b, sampling=espaciado_zyx)[borde_a]
    dist_b_a = ndimage.distance_transform_edt(~borde_a, sampling=espaciado_zyx)[borde_b]
    return float(max(np.percentile(dist_a_b, 95), np.percentile(dist_b_a, 95)))


def segmentacion(caso: Path) -> dict:
    m1 = sitk.ReadImage(str(caso / 'mascara_obs1.nii.gz'))
    m2 = sitk.ReadImage(str(caso / 'mascara_obs2.nii.gz'))
    igual, motivo = comun.misma_geometria(m1, m2)
    if not igual:
        raise ValueError(f'{caso.name}: las dos máscaras no tienen la misma geometría ({motivo})')
    a = sitk.GetArrayFromImage(m1) > 0
    b = sitk.GetArrayFromImage(m2) > 0
    return {'id': caso.name, 'voxeles_obs1': int(a.sum()), 'voxeles_obs2': int(b.sum()),
            'dice': round(dice(a, b), 4), 'hd95_mm': round(hd95(a, b, m1.GetSpacing()[::-1]), 3)}


def icc_por_caracteristica(largo: pd.DataFrame, prioritarias: set[str]) -> pd.DataFrame:
    filas = []
    for nombre, datos in largo.groupby('caracteristica', sort=True):
        completos = datos.dropna(subset=['valor']).groupby('id').filter(lambda g: len(g) == 2)
        fila = {'caracteristica': nombre, 'prioritaria': nombre in prioritarias,
                'n_casos': completos['id'].nunique(),
                'media_obs1': completos.loc[completos.observador == 'obs1', 'valor'].mean(),
                'media_obs2': completos.loc[completos.observador == 'obs2', 'valor'].mean(),
                'icc': np.nan, 'ic95_inf': np.nan, 'ic95_sup': np.nan, 'nota': ''}
        if completos['valor'].nunique() <= 1:
            fila['nota'] = 'sin variabilidad entre casos: ICC no calculable'
        else:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    tabla = pg.intraclass_corr(data=completos, targets='id', raters='observador', ratings='valor')
                icc2 = tabla.set_index('Type').loc['ICC2']
                fila.update({'icc': icc2['ICC'], 'ic95_inf': icc2['CI95%'][0], 'ic95_sup': icc2['CI95%'][1]})
            except Exception as e:  # p. ej. menos de 5 casos completos
                fila['nota'] = f'ICC no calculable: {e}'
        filas.append(fila)
    tabla = pd.DataFrame(filas)
    tabla['fiabilidad_koo_li'] = [comun.fiabilidad_koo_li(i, u) for i, u in zip(tabla['ic95_inf'], tabla['ic95_sup'])]
    tabla['cautela'] = tabla['ic95_inf'] < 0.5  # NaN → False
    return tabla.sort_values(['prioritaria', 'caracteristica'], ascending=[False, True]).round(4)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--entrada', type=Path, default=Path('data'))
    p.add_argument('--salida', type=Path, default=Path('outputs'))
    p.add_argument('--params', type=Path, default=comun.CONFIG / 'params.yaml')
    p.add_argument('--prioritarias', type=Path, default=comun.CONFIG / 'features_prioritarias.yaml')
    p.add_argument('--binwidth', type=float, default=None)
    a = p.parse_args(argv)

    casos = [c for c in comun.casos(a.entrada / 'casos')
             if (c / 'mascara_obs1.nii.gz').exists() and (c / 'mascara_obs2.nii.gz').exists()]
    a.salida.mkdir(parents=True, exist_ok=True)
    if not casos:
        print('Paso 4: ningún caso con dos observadores; se omite.')
        return 0

    extractor = comun.crear_extractor(a.params, a.binwidth)
    seg, filas = [], []
    for caso in casos:
        seg.append(segmentacion(caso))
        for obs in ('obs1', 'obs2'):
            valores = comun.extraer(extractor, caso / 'imagen.nii.gz', caso / f'mascara_{obs}.nii.gz')
            filas.append({'id': caso.name, 'observador': obs, **valores})
        print(f'  {caso.name}: Dice {seg[-1]["dice"]}, HD95 {seg[-1]["hd95_mm"]} mm')

    ancho = pd.DataFrame(filas)
    largo = ancho.melt(id_vars=['id', 'observador'], var_name='caracteristica', value_name='valor')
    prioritarias = {c['columna'] for c in comun.cargar_yaml(a.prioritarias)['caracteristicas']}
    icc = icc_por_caracteristica(largo, prioritarias)

    pd.DataFrame(seg).to_csv(a.salida / 'reproducibilidad_segmentacion.csv', index=False, encoding='utf-8')
    icc.to_csv(a.salida / 'reproducibilidad_icc.csv', index=False, encoding='utf-8')
    ancho.to_csv(a.salida / 'reproducibilidad_features.csv', index=False, encoding='utf-8')
    minimo = 15
    aviso = ''
    if len(casos) < minimo:
        aviso = (f'Solo hay {len(casos)} casos con dos observadores; el protocolo (§8) orienta a un mínimo de '
                 f'{minimo}. Los ICC tendrán intervalos muy anchos: interprétalos con cautela.')
        print('AVISO: ' + aviso)
    segdf = pd.DataFrame(seg)

    def mediana(c):
        v = segdf[c].dropna()
        return None if v.empty else float(v.median())

    (a.salida / 'reproducibilidad_resumen.json').write_text(json.dumps(
        {'n_casos': len(casos), 'minimo_protocolo': minimo, 'aviso': aviso,
         'dice_mediana': mediana('dice'), 'hd95_mediana_mm': mediana('hd95_mm')},
        ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Paso 4: {len(casos)} casos con dos observadores; ICC de {len(icc)} características '
          f'→ {a.salida / "reproducibilidad_icc.csv"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
