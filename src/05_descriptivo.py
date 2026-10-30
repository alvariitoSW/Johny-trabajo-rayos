"""Paso 5 · Perfil radiómico descriptivo (protocolo §11.2) del subconjunto prioritario.

Para cada característica de config/features_prioritarias.yaml: n válidos, ausentes, media, DE, mediana, P25, P75,
RIC, mínimo, máximo y coeficiente de variación (CV = DE / |media| × 100). El CV se omite si el archivo lo marca como
no apropiado (escalas de intervalo como las UH, o valores que pueden ser ≤ 0) o si la media es casi 0.
Figuras: histograma + diagrama de caja por característica y matriz de correlación de Spearman entre ellas
(exploratoria: sirve para ver redundancia entre características, no es evidencia de asociación clínica).

Entrada:  <salida>/features.csv (paso 2)
Salida:   <salida>/descriptivo.csv, <salida>/spearman.csv y <salida>/figuras/*.png

Solo se describen los casos con decision == incluir de <salida>/qc_report.csv (paso 3), si existe.

Uso:  python src/05_descriptivo.py --salida outputs [--prioritarias config/features_prioritarias.yaml]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402


def describir(valores: pd.Series, cv_apropiado: bool, media_minima: float) -> dict:
    v = pd.to_numeric(valores, errors='coerce')
    validos = v.dropna()
    fila = {'n': int(validos.size), 'ausentes': int(v.isna().sum())}
    if validos.empty:
        return {**fila, 'nota': 'sin valores'}
    media, de = validos.mean(), validos.std(ddof=1) if validos.size > 1 else np.nan
    p25, p75 = validos.quantile([0.25, 0.75])
    fila.update({'media': media, 'de': de, 'mediana': validos.median(), 'p25': p25, 'p75': p75,
                 'ric': p75 - p25, 'minimo': validos.min(), 'maximo': validos.max(), 'cv_pct': np.nan, 'nota': ''})
    if not cv_apropiado:
        fila['nota'] = 'CV no apropiado para esta escala'
    elif abs(media) < media_minima:
        fila['nota'] = 'CV omitido: media cercana a 0'
    elif validos.min() <= 0:
        fila['nota'] = 'CV omitido: hay valores ≤ 0'
    elif not np.isnan(de):
        fila['cv_pct'] = 100 * de / abs(media)
    return fila


def figura_distribucion(valores: pd.Series, titulo: str, unidad: str, ruta: Path) -> None:
    v = pd.to_numeric(valores, errors='coerce').dropna()
    fig, (arriba, abajo) = plt.subplots(2, 1, figsize=(4.2, 3.6), height_ratios=[3, 1], sharex=True)
    arriba.hist(v, bins='auto', color='#3b6ea5', edgecolor='white')
    arriba.set_ylabel('Lesiones')
    arriba.set_title(titulo, fontsize=11)
    abajo.boxplot(v, orientation='horizontal', widths=0.6, patch_artist=True,
                  boxprops={'facecolor': '#dbe7f3'}, medianprops={'color': '#c0392b'})
    abajo.set_yticks([])
    abajo.set_xlabel(unidad if unidad != '—' else 'sin unidad')
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, bbox_inches='tight')
    plt.close(fig)


def figura_spearman(corr: pd.DataFrame, ruta: Path) -> None:
    n = len(corr)
    # Solo números en los ejes (la leyenda «1. Media…» va en el informe), así la matriz ocupa todo el ancho.
    fig, ax = plt.subplots(figsize=(4.2, 4.9))
    im = ax.imshow(corr.values, cmap='RdBu_r', vmin=-1, vmax=1)
    ax.set_xticks(range(n), range(1, n + 1), fontsize=6.5)
    ax.set_yticks(range(n), range(1, n + 1), fontsize=6.5)
    ax.set_title('Correlación de Spearman (ρ)', fontsize=10)
    barra = fig.colorbar(im, ax=ax, orientation='horizontal', fraction=0.05, pad=0.06)
    barra.ax.tick_params(labelsize=7)
    fig.tight_layout()
    fig.savefig(ruta, dpi=200, bbox_inches='tight')
    plt.close(fig)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--salida', type=Path, default=Path('outputs'))
    p.add_argument('--prioritarias', type=Path, default=comun.CONFIG / 'features_prioritarias.yaml')
    a = p.parse_args(argv)

    config = comun.cargar_yaml(a.prioritarias)
    datos = pd.read_csv(a.salida / 'features.csv')
    if 'error' in datos:
        datos = datos[datos['error'].isna() | (datos['error'] == '')]
    analizados = comun.ids_analizados(a.salida, 'paso 5')  # solo decision == incluir (None: sin paso 3)
    if analizados is not None:
        datos = datos[datos['id'].isin(analizados)]
    figuras = a.salida / 'figuras'
    figuras.mkdir(parents=True, exist_ok=True)

    filas, columnas = [], {}
    for i, c in enumerate(config['caracteristicas'], 1):
        base = {'orden': i, 'caracteristica': c['nombre'], 'columna': c['columna'], 'unidad': c['unidad']}
        if c['columna'] not in datos:
            filas.append({**base, 'n': 0, 'ausentes': len(datos), 'nota': 'no está en features.csv'})
            continue
        filas.append({**base, **describir(datos[c['columna']], c['cv'], config.get('cv_media_minima', 1e-6))})
        figura_distribucion(datos[c['columna']], c['nombre'], c['unidad'], figuras / f'distribucion_{i:02d}.png')
        columnas[c['nombre']] = pd.to_numeric(datos[c['columna']], errors='coerce')

    tabla = pd.DataFrame(filas)
    tabla.to_csv(a.salida / 'descriptivo.csv', index=False, encoding='utf-8')
    corr = pd.DataFrame(columnas).corr(method='spearman')
    corr.to_csv(a.salida / 'spearman.csv', encoding='utf-8')
    figura_spearman(corr, figuras / 'spearman.png')
    print(f'Paso 5: {len(columnas)} características descritas en {len(datos)} lesiones → {a.salida / "descriptivo.csv"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
