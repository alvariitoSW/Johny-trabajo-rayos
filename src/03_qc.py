"""Paso 3 · Control de calidad de las máscaras y de la homogeneidad técnica.

Por caso (<salida>/qc_report.csv):
  · máscara vacía, valores distintos de 0/1, misma geometría que la imagen
  · nº de componentes conexos (26-vecindad): más de uno = revisar (una lesión índice por paciente, §6)
  · volumen (mL)
  · diámetro máximo AXIAL (mm): el mayor diámetro en un corte axial, como mide RECIST 1.1. Si es < 10 mm, la
    lesión no cumple el criterio de inclusión de lesión medible (§5) → alerta
  · diámetro máximo 3D (mm), entre centros de vóxel del borde (puede quedar ~1 vóxel por debajo del de pyRadiomics,
    que lo mide sobre la malla)
  · kVp, kernel y grosor de corte del caso
Entre casos (<salida>/qc_heterogeneidad_tecnica.csv): cuántos casos hay de cada fabricante, modelo, kVp, kernel,
grosor de corte y pixel spacing, y el mA (mediana y rango).

Uso:  python src/03_qc.py --entrada data --salida outputs [--diametro-minimo 10]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import SimpleITK as sitk
from scipy import ndimage
from scipy.spatial import ConvexHull, QhullError
from scipy.spatial.distance import pdist

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

CATEGORICAS = ['fabricante', 'modelo', 'kvp', 'kernel', 'grosor_corte_mm', 'pixel_spacing_mm']


def coordenadas_fisicas(img: sitk.Image, indices_zyx: np.ndarray) -> np.ndarray:
    """Índices de numpy (z, y, x) → puntos en mm (x, y, z), con la orientación real de la imagen."""
    ijk = indices_zyx[:, ::-1].astype(float) * np.array(img.GetSpacing())
    direccion = np.array(img.GetDirection()).reshape(3, 3)
    return np.array(img.GetOrigin()) + ijk @ direccion.T


def diametro_maximo(puntos: np.ndarray) -> float:
    """Mayor distancia entre dos puntos (sobre su envolvente convexa para no comparar todos con todos)."""
    if len(puntos) < 2:
        return 0.0
    try:
        puntos = puntos[ConvexHull(puntos).vertices]
    except (QhullError, ValueError):  # puntos coplanares o casi: se comparan todos
        pass
    return float(pdist(puntos).max())


def borde(arr: np.ndarray) -> np.ndarray:
    return arr & ~ndimage.binary_erosion(arr)


def diametros(mascara: sitk.Image) -> tuple[float, float]:
    """(diámetro máximo axial, diámetro máximo 3D) en mm."""
    arr = sitk.GetArrayFromImage(mascara).astype(bool)
    d3 = diametro_maximo(coordenadas_fisicas(mascara, np.argwhere(borde(arr))))
    d_axial = 0.0
    for z in np.unique(np.argwhere(arr)[:, 0]):
        corte = arr[z]
        idx = np.argwhere(corte & ~ndimage.binary_erosion(corte))
        # Envolvente 2D en índices del corte (sus vértices no cambian al pasar a mm: es una transformación
        # afín) y distancias en mm sobre el plano del corte, aunque el gantry esté inclinado.
        try:
            idx = idx[ConvexHull(idx).vertices] if len(idx) >= 3 else idx
        except (QhullError, ValueError):
            pass
        puntos = coordenadas_fisicas(mascara, np.column_stack([np.full(len(idx), z), idx]))
        if len(puntos) >= 2:
            d_axial = max(d_axial, float(pdist(puntos).max()))
    return d_axial, d3


def qc_caso(caso: Path, minimo_mm: float) -> dict:
    imagen = sitk.ReadImage(str(caso / 'imagen.nii.gz'))
    mascara_cruda = sitk.ReadImage(str(caso / 'mascara.nii.gz'))
    valores = np.unique(sitk.GetArrayViewFromImage(mascara_cruda))
    mascara = comun.mascara_binaria(mascara_cruda)
    arr = sitk.GetArrayViewFromImage(mascara)
    n_voxeles = int(arr.sum())
    geometria, motivo = comun.misma_geometria(imagen, mascara)
    componentes = sitk.ConnectedComponent(mascara, True)  # True = 26-vecindad
    n_comp = int(sitk.GetArrayViewFromImage(componentes).max())
    tecnicas = comun.leer_json(caso / 'tecnicas.json')

    alertas = []
    if n_voxeles == 0:
        alertas.append('máscara vacía')
    if not set(valores.tolist()) <= {0, 1}:
        alertas.append(f'valores de máscara {valores.tolist()}')
    if not geometria:
        alertas.append(f'geometría imagen≠máscara ({motivo})')
    if n_comp > 1:
        alertas.append(f'{n_comp} componentes')
    d_axial, d3 = diametros(mascara) if n_voxeles else (0.0, 0.0)
    if n_voxeles and d_axial < minimo_mm:
        alertas.append(f'diámetro axial < {minimo_mm:g} mm')
    obs = (caso / 'mascara_obs1.nii.gz').exists() and (caso / 'mascara_obs2.nii.gz').exists()
    return {
        'id': caso.name,
        'voxeles': n_voxeles,
        'volumen_ml': round(n_voxeles * float(np.prod(mascara.GetSpacing())) / 1000, 3),
        'diametro_axial_max_mm': round(d_axial, 1),
        'diametro_3d_max_mm': round(d3, 1),
        f'menor_{minimo_mm:g}mm': bool(n_voxeles and d_axial < minimo_mm),
        'componentes': n_comp,
        'mascara_vacia': n_voxeles == 0,
        'geometria_igual': geometria,
        'dos_observadores': obs,
        'kvp': tecnicas.get('kvp'),
        'kernel': tecnicas.get('kernel'),
        'grosor_corte_mm': tecnicas.get('grosor_corte_mm'),
        'alertas': '; '.join(alertas) or 'ninguna',
    }


def heterogeneidad(casos: list[Path]) -> pd.DataFrame:
    tecnicas = pd.DataFrame([{**comun.leer_json(c / 'tecnicas.json'), 'id': c.name} for c in casos])
    filas = []
    for var in CATEGORICAS:
        if var not in tecnicas:
            continue
        cuenta = tecnicas[var].fillna('desconocido').astype(str).value_counts()
        for valor, n in cuenta.items():
            filas.append({'variable': var, 'valor': valor, 'n': int(n), 'porcentaje': round(100 * n / len(tecnicas), 1)})
    if 'ma' in tecnicas and tecnicas['ma'].notna().any():
        ma = pd.to_numeric(tecnicas['ma'], errors='coerce').dropna()
        filas.append({'variable': 'ma', 'valor': f'mediana {ma.median():g} (rango {ma.min():g}–{ma.max():g})',
                      'n': int(len(ma)), 'porcentaje': round(100 * len(ma) / len(tecnicas), 1)})
    return pd.DataFrame(filas, columns=['variable', 'valor', 'n', 'porcentaje'])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--entrada', type=Path, default=Path('data'))
    p.add_argument('--salida', type=Path, default=Path('outputs'))
    p.add_argument('--diametro-minimo', type=float, default=10.0, help='mm (RECIST 1.1: lesión medible ≥ 10 mm)')
    a = p.parse_args(argv)

    casos = comun.casos(a.entrada / 'casos')
    informe = pd.DataFrame([qc_caso(c, a.diametro_minimo) for c in casos])
    a.salida.mkdir(parents=True, exist_ok=True)
    informe.to_csv(a.salida / 'qc_report.csv', index=False, encoding='utf-8')
    heterogeneidad(casos).to_csv(a.salida / 'qc_heterogeneidad_tecnica.csv', index=False, encoding='utf-8')
    con_alerta = informe[informe['alertas'] != 'ninguna']
    print(f'Paso 3: {len(informe)} casos revisados, {len(con_alerta)} con alertas → {a.salida / "qc_report.csv"}')
    for _, f in con_alerta.iterrows():
        print(f'  {f["id"]}: {f["alertas"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
