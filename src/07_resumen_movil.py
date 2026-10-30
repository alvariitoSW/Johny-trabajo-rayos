"""Paso 7 · Resumen agregado para el móvil (acta 30/10/2026, asunto 7c).

Escribe UNA página HTML (<salida>/resumen_movil.html) con cifras de grupo, pensada para leerse en el móvil:
cuántos casos se evaluaron, cuántos tienen alertas, cuántos tienen dos observadores, el Dice y el HD95 (distancia
entre dos contornos), y la mediana con su rango intercuartílico (RIC) y el ICC con su IC 95 % de las
características prioritarias.

Reglas de protección (protocolo §13; REGLAS §2):
  · No lleva ningún código de caso ni ninguna fila individual.
  · Un recuento de 1 a 4 se escribe «< 5».
  · Con menos de 5 casos no se dan medianas.
  · La página no usa scripts ni recursos externos.
  · Antes de sacarla del PC del hospital hay que pedir permiso al delegado de protección de datos.

Lee los CSV de los pasos 3 a 5 en <salida>; los que no existan, se omiten.

Uso:  python src/07_resumen_movil.py --entrada data --salida outputs
"""
from __future__ import annotations

import argparse
import html
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

MINIMO = 5
AVISO = ('Resumen agregado. Antes de sacarlo de este PC, pide permiso al delegado de protección de datos '
         '(protocolo §13).')
DEMASIADO_PEQUENA = 'muestra demasiado pequeña para resumir'
# Tipos de alerta del paso 3 (03_qc.py): prefijo del texto → nombre en llano.
TIPOS_ALERTA = [('máscara vacía', 'máscara vacía'), ('valores de máscara', 'valores de máscara no válidos'),
                ('geometría', 'geometría distinta'), ('componentes', 'varios componentes'),
                ('diámetro axial <', 'lesión menor de 10 mm')]


def recuento(n: int) -> str:
    """Un recuento de 1 a 4 se oculta como «< 5»; el 0 y los de 5 o más se escriben tal cual."""
    return '< 5' if 0 < n < MINIMO else str(int(n))


def numero(x: float, dec: int = 2) -> str:
    return f'{x:.{dec}f}'.replace('.', ',')


def leer(ruta: Path) -> pd.DataFrame | None:
    return pd.read_csv(ruta) if ruta.exists() else None


def tabla(filas: list[list[str]], cabecera: list[str]) -> str:
    c = ''.join(f'<th>{html.escape(x)}</th>' for x in cabecera)
    f = ''.join('<tr>' + ''.join(f'<td>{html.escape(x)}</td>' for x in fila) + '</tr>' for fila in filas)
    return f'<table><tr>{c}</tr>{f}</table>'


def seccion_casos(qc: pd.DataFrame) -> tuple[str, int]:
    n = len(qc)
    con = qc[qc['alertas'] != 'ninguna']
    filas = [['Casos evaluados', recuento(n)], ['Con alguna alerta', recuento(len(con))]]
    for prefijo, nombre in TIPOS_ALERTA:
        k = int(con['alertas'].str.contains(prefijo, regex=False).sum())
        if k:
            filas.append([f'· {nombre}', recuento(k)])
    if 'dos_observadores' in qc:
        filas.append(['Con dos observadores', recuento(int(qc['dos_observadores'].astype(bool).sum()))])
    return '<h2>Casos</h2>' + tabla(filas, ['Qué', 'Casos']), n


def seccion_segmentacion(seg: pd.DataFrame) -> str:
    n = len(seg)
    if n < MINIMO:
        return f'<h2>Dos observadores</h2><p>Casos: {recuento(n)}. {DEMASIADO_PEQUENA.capitalize()}.</p>'
    dice = pd.to_numeric(seg['dice'], errors='coerce').dropna()
    hd = pd.to_numeric(seg['hd95_mm'], errors='coerce').dropna()
    filas = [['Dice (1 = contornos iguales)', numero(dice.median()), f'{numero(dice.min())} a {numero(dice.max())}'],
             ['HD95 (mm; 0 = iguales)', numero(hd.median(), 1), f'{numero(hd.min(), 1)} a {numero(hd.max(), 1)}']]
    return (f'<h2>Dos observadores</h2><p>Casos: {recuento(n)}. Mediana y rango.</p>'
            + tabla(filas, ['Medida', 'Mediana', 'Rango']))


def seccion_caracteristicas(desc: pd.DataFrame | None, icc: pd.DataFrame | None, prioritarias: list[dict]) -> str:
    filas = []
    for c in prioritarias:
        col = c['columna']
        mediana, ric = '—', '—'
        if desc is not None and (desc['columna'] == col).any():
            d = desc[desc['columna'] == col].iloc[0]
            if d['n'] >= MINIMO:
                mediana = f'{numero(d["mediana"])} {c.get("unidad", "")}'.strip()
                ric = f'{numero(d["p25"])} a {numero(d["p75"])}'
        texto_icc = '—'
        if icc is not None and (icc['caracteristica'] == col).any():
            i = icc[icc['caracteristica'] == col].iloc[0]
            if i['n_casos'] >= MINIMO and pd.notna(i['icc']):
                texto_icc = f'{numero(i["icc"])} ({numero(i["ic95_inf"])} a {numero(i["ic95_sup"])})'
        filas.append([c.get('nombre', col), mediana, ric, texto_icc])
    return ('<h2>Características prioritarias</h2><p>Mediana, RIC (P25 a P75) e ICC con IC 95 %. '
            '«—» = sin datos suficientes.</p>' + tabla(filas, ['Característica', 'Mediana', 'RIC', 'ICC (IC 95 %)']))


def construir(entrada: Path, salida: Path, prioritarias: Path) -> str:
    qc, seg = leer(salida / 'qc_report.csv'), leer(salida / 'reproducibilidad_segmentacion.csv')
    icc, desc = leer(salida / 'reproducibilidad_icc.csv'), leer(salida / 'descriptivo.csv')
    meta = comun.leer_json(salida / 'extraccion_meta.json') if (salida / 'extraccion_meta.json').exists() else {}
    partes, total = [], None
    if qc is not None:
        texto, total = seccion_casos(qc)
        partes.append(texto)
    if total is not None and total < MINIMO:
        partes.append(f'<p><b>{DEMASIADO_PEQUENA.capitalize()}.</b></p>')
    else:
        if seg is not None:
            partes.append(seccion_segmentacion(seg))
        if desc is not None or icc is not None:
            partes.append(seccion_caracteristicas(desc, icc, comun.cargar_yaml(prioritarias)['caracteristicas']))
    if not partes:
        partes.append('<p>Todavía no hay resultados en esta carpeta.</p>')
    version = meta.get('versiones', {}).get('pyradiomics', 'no consta')
    pie = (f'Generado: {datetime.now():%Y-%m-%d %H:%M} · pyRadiomics {version} · '
           f'binWidth {meta.get("binWidth", "no consta")}')
    banda = '<div class="sint">DATOS SINTÉTICOS</div>' if (entrada / 'DATOS_SINTETICOS.txt').exists() else ''
    estilo = ('body{font-family:sans-serif;margin:0;padding:12px;max-width:34em;line-height:1.4}'
              'table{border-collapse:collapse;width:100%;font-size:.9em}th,td{border:1px solid #bbb;padding:4px;'
              'text-align:left}.aviso{background:#fff3cd;border:1px solid #c9a400;padding:8px}'
              '.sint{background:#c0392b;color:#fff;text-align:center;font-weight:bold;padding:6px;margin-bottom:8px}'
              'h2{font-size:1.1em;margin-top:1.2em}small{color:#555}')
    return ('<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Resumen para el móvil</title><style>{estilo}</style></head><body>{banda}'
            f'<div class="aviso">{html.escape(AVISO)}</div><h1>Resumen del estudio</h1>'
            + ''.join(partes) + f'<p><small>{html.escape(pie)}</small></p></body></html>')


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--entrada', type=Path, default=Path('data'))
    p.add_argument('--salida', type=Path, default=Path('outputs'))
    p.add_argument('--prioritarias', type=Path, default=comun.CONFIG / 'features_prioritarias.yaml')
    a = p.parse_args(argv)
    a.salida.mkdir(parents=True, exist_ok=True)
    destino = a.salida / 'resumen_movil.html'
    destino.write_text(construir(a.entrada, a.salida, a.prioritarias), encoding='utf-8')
    print(f'Paso 7: resumen para el móvil → {destino}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
