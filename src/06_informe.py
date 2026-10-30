"""Paso 6 · Informe PDF autocontenido (tablas y figuras de los pasos 3, 4 y 5), pensado para leerse en el móvil:
páginas estrechas y altas, letra grande y tablas de pocas columnas que se parten entre páginas.

Entrada:  <salida>/qc_report.csv, qc_heterogeneidad_tecnica.csv, reproducibilidad_*.csv, descriptivo.csv,
          spearman.csv, figuras/*.png y extraccion_meta.json
Salida:   <salida>/informe.pdf

Si <entrada>/DATOS_SINTETICOS.txt existe (lo crea el generador de pruebas), cada página lo avisa.

Uso:  python src/06_informe.py --entrada data --salida outputs
"""
from __future__ import annotations

import argparse
import sys
import textwrap
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

ANCHO, ALTO = 4.0, 8.4          # pulgadas: proporción de la pantalla de un móvil
LINEAS_POR_PAGINA = 44
AZUL = '#1f4e79'


def num(x, decimales=None) -> str:
    """Número en formato español (coma decimal); «—» si falta. Sin decimales fijos, los ajusta al tamaño
    del número (3-4 cifras significativas) para que las columnas quepan en el móvil."""
    if x is None or (isinstance(x, float) and pd.isna(x)) or x == '':
        return '—'
    try:
        x = float(x)
    except (TypeError, ValueError):
        return str(x)
    if decimales is None:
        a = abs(x)
        if a >= 1e6 or (0 < a < 1e-3):
            return f'{x:.2e}'.replace('.', ',')
        decimales = 0 if a >= 1000 else 1 if a >= 100 else 2 if a >= 1 else 3
    return f'{x:,.{decimales}f}'.replace(',', ' ').replace('.', ',').replace(' ', '.')


class Informe:
    def __init__(self, ruta: Path, aviso: str):
        self.pdf = PdfPages(ruta)
        self.aviso = aviso
        self.n_pagina = 0

    def pagina(self):
        self.n_pagina += 1
        fig = plt.figure(figsize=(ANCHO, ALTO))
        if self.aviso:
            fig.text(0.5, 0.985, self.aviso, ha='center', va='top', fontsize=7, color='white', weight='bold',
                     bbox={'facecolor': '#c0392b', 'edgecolor': 'none', 'pad': 3})
        fig.text(0.5, 0.012, f'{self.n_pagina}', ha='center', fontsize=7, color='grey')
        return fig

    def cerrar_pagina(self, fig):
        self.pdf.savefig(fig)
        plt.close(fig)

    def texto(self, titulo: str, parrafos: list[str]):
        """Página de texto. Si no cabe, sigue en otra página con el mismo título. Un párrafo que empieza
        por «## » sale como subtítulo en negrita."""
        def nueva(sufijo=''):
            fig = self.pagina()
            y = 0.95
            for linea in textwrap.wrap(titulo + sufijo, 32):
                fig.text(0.07, y, linea, fontsize=13, weight='bold', color=AZUL, va='top')
                y -= 0.03
            return fig, y - 0.02

        fig, y = nueva()
        for parrafo in parrafos:
            subtitulo = parrafo.startswith('## ')
            lineas = textwrap.wrap(parrafo[3:] if subtitulo else parrafo, 40 if subtitulo else 46) or ['']
            reserva = 0.1 if subtitulo else 0      # que un subtítulo no quede solo al pie de la página
            if y - 0.021 * len(lineas) - reserva < 0.04:
                self.cerrar_pagina(fig)
                fig, y = nueva(' (sigue)')
            for linea in lineas:
                fig.text(0.07, y, linea, fontsize=9.6 if subtitulo else 8.6, va='top',
                         weight='bold' if subtitulo else 'normal', color=AZUL if subtitulo else 'black')
                y -= 0.021
            y -= 0.006 if subtitulo else 0.012
        self.cerrar_pagina(fig)

    def tabla(self, titulo: str, cabecera: list[str], filas: list[list[str]], anchos: list[int], nota: str = ''):
        """Tabla con ajuste de línea por celda; se parte en varias páginas si no cabe."""
        def partir(celdas):
            trozos = [textwrap.wrap(str(c), w) or [''] for c, w in zip(celdas, anchos)]
            return [['\n'.join(t) for t in trozos], max(len(t) for t in trozos)]

        alto_linea, espacio_fila = 0.0172, 0.6
        lineas_nota = textwrap.wrap(nota, 52)
        # Alto disponible para la tabla: de 0,92 hasta el pie, dejando sitio para la nota en cada página.
        disponible = 0.86 - 0.03 - 0.019 * len(lineas_nota)
        cab, lineas_cab = partir(cabecera)
        bloques, actual = [], []
        usado = alto_linea * (lineas_cab + espacio_fila)
        for fila in filas:
            celdas, n = partir(fila)
            alto_fila = alto_linea * (n + espacio_fila)
            if actual and usado + alto_fila > disponible:
                bloques.append(actual)
                actual, usado = [], alto_linea * (lineas_cab + espacio_fila)
            actual.append((celdas, n))
            usado += alto_fila
        bloques.append(actual)

        total = sum(anchos)
        for i, bloque in enumerate(bloques):
            fig = self.pagina()
            fig.text(0.05, 0.955, titulo + (f' ({i + 1}/{len(bloques)})' if len(bloques) > 1 else ''),
                     fontsize=11.5, weight='bold', color=AZUL, va='top')
            alturas = [lineas_cab] + [n for _, n in bloque]
            alto = alto_linea * (sum(alturas) + espacio_fila * len(alturas))
            ax = fig.add_axes([0.04, 0.92 - alto, 0.92, alto])
            ax.axis('off')
            t = ax.table(cellText=[c for c, _ in bloque] or [[''] * len(cab)], colLabels=cab,
                         colWidths=[w / total for w in anchos], cellLoc='left', loc='upper left')
            t.auto_set_font_size(False)
            t.set_fontsize(7.4)
            for (r, _c), celda in t.get_celld().items():
                celda.set_height((alturas[r] + 0.6) / (sum(alturas) + 0.6 * len(alturas)))
                celda.set_edgecolor('#cccccc')
                if r == 0:
                    celda.set_facecolor('#dbe7f3')
                    celda.set_text_props(weight='bold')
                elif r % 2 == 0:
                    celda.set_facecolor('#f6f8fa')
            if nota and i == len(bloques) - 1:
                for j, linea in enumerate(lineas_nota):
                    fig.text(0.05, 0.9 - alto - 0.03 - j * 0.019, linea, fontsize=7.6, va='top', color='#333333')
            self.cerrar_pagina(fig)

    def imagenes(self, titulo: str, rutas: list[Path], pies: list[str] | None = None, por_pagina: int = 2):
        for i in range(0, len(rutas), por_pagina):
            fig = self.pagina()
            fig.text(0.05, 0.955, titulo, fontsize=11.5, weight='bold', color=AZUL, va='top')
            grupo = rutas[i:i + por_pagina]
            alto = 0.86 / por_pagina
            for j, ruta in enumerate(grupo):
                ax = fig.add_axes([0.03, 0.92 - (j + 1) * alto, 0.94, alto - 0.015])
                ax.imshow(plt.imread(ruta))
                ax.axis('off')
            if pies:
                for k, linea in enumerate(pies[i // por_pagina] if i // por_pagina < len(pies) else []):
                    fig.text(0.05, 0.05 - k * 0.016, linea, fontsize=6.6, va='top')
            self.cerrar_pagina(fig)

    def imagen_con_leyenda(self, titulo: str, ruta: Path, lineas: list[str]):
        """Una imagen arriba, a todo lo ancho, y su leyenda debajo."""
        fig = self.pagina()
        fig.text(0.05, 0.955, titulo, fontsize=11.5, weight='bold', color=AZUL, va='top')
        ax = fig.add_axes([0.02, 0.42, 0.96, 0.51])
        ax.imshow(plt.imread(ruta))
        ax.set_anchor('N')
        ax.axis('off')
        y = 0.41
        for linea in lineas:
            for trozo in textwrap.wrap(linea, 56):
                fig.text(0.06, y, trozo, fontsize=7.6, va='top')
                y -= 0.0175
        self.cerrar_pagina(fig)

    def cerrar(self):
        self.pdf.close()


def leer(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta) if ruta.exists() else pd.DataFrame()


# ------------------------------------------------------------------------- explicaciones en llano
# Resumen del apartado 1 de docs/guia_interpretacion.md (fuentes allí).
COMO_LEER = [
    '## Qué es la radiómica',
    'Convierte la imagen en números con fórmulas. Dentro del contorno de la lesión mide tres cosas: cuántas UH '
    'tiene (primer orden), qué forma tiene (forma) y cómo se colocan los grises unos junto a otros (texturas).',
    'Cada número sale de una fórmula concreta del programa (pyRadiomics). Otro programa con un nombre parecido '
    'puede dar otro número.',
    '## Qué se puede concluir',
    'Cómo son, en cifras, las lesiones de esta muestra. Y si dos radiólogos que segmentan la misma lesión '
    'obtienen las mismas cifras.',
    '## Qué NO se puede concluir',
    'Nada sobre pronóstico, respuesta ni diagnóstico: el estudio es descriptivo (protocolo §11.4).',
    'Estas cifras no son biomarcadores validados. Que dos cifras vayan juntas no quiere decir que una cause la '
    'otra (van Timmeren 2020).',
    '## Tres niveles de explicación',
    '1) Qué mide: sale de la documentación del programa. 2) Qué se ve en la TC: solo si una fuente radiológica '
    'lo dice; si no, «sin fuente». 3) Qué significa para el paciente: no se da.',
    '## En qué orden leerlo',
    'Primero el control de calidad (¿hay casos raros?). Después la reproducibilidad (¿se mide igual con otro '
    'observador?). Por último el perfil de las lesiones. Una cifra que no se reproduce se lee con cautela. '
    'Tras cada bloque, «Qué dicen tus datos» lo resume en frases.',
]

COMO_LEER_ESTADISTICOS = [
    '## Media ± DE',
    'La media es el promedio de las lesiones; la DE (desviación estándar), cuánto se separan de él.',
    '## Mediana (RIC)',
    'La mediana es el valor del medio al ordenar las lesiones. El RIC (rango intercuartílico) va del percentil 25 '
    'al 75: ahí cae la mitad central. Si la media y la mediana se separan mucho, hay valores extremos.',
    '## Ausentes',
    'Un campo vacío es un dato ausente, nunca un 0 (protocolo §11.1).',
    '## CV (%)',
    'Coeficiente de variación: DE / media × 100. No se calcula en UH (el 0 es el agua, no «nada»), ni con '
    'valores negativos o medias cercanas a 0 (protocolo §11.2).',
    '## Diagrama de caja',
    'La caja va del percentil 25 al 75; la línea roja es la mediana; los bigotes llegan hasta el dato más lejano '
    'a menos de 1,5 RIC de la caja; los puntos sueltos son lesiones atípicas, para revisar en la imagen.',
    '## Spearman (ρ)',
    'De −1 a 1: si dos características suben juntas al ordenar las lesiones. Solo sirve para ver qué '
    'características dicen lo mismo (redundancia), nunca asociación clínica (protocolo §11.2).',
    '## Dice',
    'Cuánto se solapan los contornos de dos observadores: 0 = nada, 1 = idénticos.',
    '## HD95 (mm)',
    'Distancia por debajo de la cual queda el 95 % del borde de un contorno respecto al otro. Dato extra: el '
    'protocolo solo pide Dice.',
    '## ICC con IC 95 %',
    'Si dos observadores dan el mismo número en cada lesión. Mira el IC 95 % antes que el número: un ICC de 0,99 '
    'con IC de 0,18 a 1,00 no dice nada. Tramos de Koo y Li (2016), leídos sobre el IC: < 0,5 pobre; 0,5-0,75 '
    'moderada; 0,75-0,9 buena; > 0,9 excelente. El ICC depende también de lo distintas que sean las lesiones '
    'entre sí.',
]


def _minuscula(frase: str) -> str:
    """Primera letra en minúscula tras «Mide:», salvo siglas (GLCM, UH…)."""
    return frase[0].lower() + frase[1:] if len(frase) > 1 and frase[1].islower() else frase


def fichas_medidas(config: dict) -> list[str]:
    """Una ficha por característica prioritaria, con en_llano, valor_alto y aviso del yaml."""
    parrafos = []
    for i, c in enumerate(config.get('caracteristicas', []), 1):
        unidad = c.get('unidad', '—')
        parrafos.append(f'## {i}. {c["nombre"]}' + (f' ({unidad})' if unidad not in ('—', '') else ''))
        parrafos.append(f'Mide: {_minuscula(c.get("en_llano", "") or "sin explicación")}')
        parrafos.append(f'Valor alto: {_minuscula(c.get("valor_alto", "") or "sin explicación")}')
        if c.get('aviso'):
            parrafos.append(f'Aviso: {_minuscula(c["aviso"])}')
    parrafos.append('Qué significa para el paciente: no se da (estudio descriptivo, protocolo §11.4).')
    return parrafos


def lectura_qc(qc: pd.DataFrame) -> list[str]:
    """«Qué dicen tus datos» del control de calidad, con las cifras reales. Sin juicios clínicos."""
    if qc.empty:
        return []
    n = len(qc)
    alertas = qc[qc['alertas'] != 'ninguna']
    d = pd.to_numeric(qc['diametro_axial_max_mm'], errors='coerce').dropna()
    v = pd.to_numeric(qc['volumen_ml'], errors='coerce').dropna()
    frases = []
    if len(d):
        frases.append(f'El diámetro axial mayor va de {num(d.min())} a {num(d.max())} mm (mediana {num(d.median())} mm).'
                      f' El volumen, de {num(v.min(), 2)} a {num(v.max(), 2)} mL.')
    if len(alertas):
        frases.append(f'{len(alertas)} de {n} lesiones tienen alguna alerta: '
                      + '; '.join(f'{f["id"]} ({f["alertas"]})' for _, f in alertas.iterrows())
                      + '. Una alerta no excluye el caso: señala qué mirar en la imagen.')
    else:
        frases.append(f'Ninguna de las {n} lesiones tiene alertas de calidad.')
    return frases


def lectura_segmentacion(seg: pd.DataFrame, qc: pd.DataFrame | None = None) -> list[str]:
    """«Qué dicen tus datos» de Dice y HD95."""
    if seg.empty:
        return []
    dice = pd.to_numeric(seg['dice'], errors='coerce')
    hd = pd.to_numeric(seg['hd95_mm'], errors='coerce')
    frases = [f'{dice.notna().sum()} lesiones tienen dos observadores. El Dice mediano fue {num(dice.median(), 2)} '
              f'(de {num(dice.min(), 2)} a {num(dice.max(), 2)}). Un 1 sería un solapamiento perfecto; un 0, '
              'ninguno.']
    if dice.notna().any():
        peor = seg.loc[dice.idxmin()]
        extra = ''
        if qc is not None and not qc.empty and 'volumen_ml' in qc:
            vol = qc.loc[qc['id'] == peor['id'], 'volumen_ml']
            if len(vol):
                extra = f', una lesión de {num(vol.iloc[0], 2)} mL'
        frases.append(f'El Dice más bajo fue el de {peor["id"]} ({num(peor["dice"], 2)}{extra}).')
    if hd.notna().any():
        frases.append(f'HD95 mediano: {num(hd.median(), 2)} mm. En la mitad de los casos, el 95 % del borde de un '
                      f'observador queda a {num(hd.median(), 2)} mm o menos del otro.')
    frases.append('Ojo: que los contornos se solapen no asegura que las cifras de cada característica coincidan '
                  '(van Timmeren 2020). Eso lo mide el ICC.')
    return frases


def atipicos(valores: pd.Series, p25: float, p75: float) -> int:
    """Número de valores más allá de los bigotes del diagrama de caja (1,5 RIC desde la caja, como matplotlib)."""
    v = pd.to_numeric(valores, errors='coerce').dropna()
    ric = p75 - p25
    return int(((v < p25 - 1.5 * ric) | (v > p75 + 1.5 * ric)).sum())


def lectura_descriptivo(desc: pd.DataFrame, datos: pd.DataFrame | None = None) -> list[str]:
    """«Qué dicen tus datos» del perfil radiómico: rango central de la atenuación, mayor CV, asimetrías
    fuertes (media fuera del RIC), atípicos y ausentes."""
    if desc.empty:
        return []
    frases = []
    media = desc[desc['columna'] == 'original_firstorder_Mean']
    if len(media) and pd.notna(media.iloc[0]['p25']):
        f = media.iloc[0]
        frases.append(f'La mitad de las lesiones tiene una atenuación media entre {num(f["p25"])} y {num(f["p75"])} UH '
                      f'(mediana {num(f["mediana"])} UH; de {num(f["minimo"])} a {num(f["maximo"])}).')
    cv = pd.to_numeric(desc.get('cv_pct'), errors='coerce')
    if cv is not None and cv.notna().any():
        f = desc.loc[cv.idxmax()]
        frases.append(f'La que más varía de una lesión a otra, en proporción a su media, es {f["caracteristica"]} '
                      f'(CV {num(f["cv_pct"], 0)} %).')
    torcidas = [f for _, f in desc.iterrows() if pd.notna(f.get('media')) and pd.notna(f.get('p25'))
                and not (f['p25'] <= f['media'] <= f['p75'])]
    if torcidas:
        frases.append('Media fuera de la mitad central (entre los percentiles 25 y 75): unos pocos valores extremos '
                      'tiran de ella. El protocolo deja describir con media o mediana según la distribución (§11.1): '
                      + '; '.join(f'{f["caracteristica"]} (media {num(f["media"])}, mediana {num(f["mediana"])})'
                                  for f in torcidas) + '.')
    if datos is not None and not datos.empty:
        lista = []
        for _, f in desc.iterrows():
            if f['columna'] in datos and pd.notna(f.get('p25')):
                k = atipicos(datos[f['columna']], f['p25'], f['p75'])
                if k:
                    lista.append(f'{f["caracteristica"]} ({k})')
        frases.append('Lesiones con valor atípico (puntos sueltos del diagrama de caja), por característica: ' + '; '.join(lista)
                      + '. Conviene mirarlas en la imagen; no se quitan.' if lista
                      else 'Ninguna característica tiene lesiones atípicas en el diagrama de caja.')
    ausentes = pd.to_numeric(desc['ausentes'], errors='coerce').fillna(0)
    if ausentes.sum():
        frases.append('Faltan datos en: ' + '; '.join(f'{f["caracteristica"]} ({int(f["ausentes"])})'
                                                       for _, f in desc[ausentes > 0].iterrows())
                      + '. Un vacío es dato ausente, nunca 0.')
    else:
        frases.append('No falta ningún valor.')
    frases.append('Son cifras descriptivas de esta muestra: no indican pronóstico ni diagnóstico (protocolo §11.4).')
    return frases


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--entrada', type=Path, default=Path('data'))
    p.add_argument('--salida', type=Path, default=Path('outputs'))
    p.add_argument('--pdf', type=Path, default=None, help='ruta del PDF (por defecto <salida>/informe.pdf)')
    p.add_argument('--prioritarias', type=Path, default=comun.CONFIG / 'features_prioritarias.yaml')
    a = p.parse_args(argv)

    s = a.salida
    meta = comun.leer_json(s / 'extraccion_meta.json')
    qc, het = leer(s / 'qc_report.csv'), leer(s / 'qc_heterogeneidad_tecnica.csv')
    seg, icc = leer(s / 'reproducibilidad_segmentacion.csv'), leer(s / 'reproducibilidad_icc.csv')
    desc = leer(s / 'descriptivo.csv')
    datos = leer(s / 'features.csv')
    if 'error' in datos:
        datos = datos[datos['error'].isna() | (datos['error'] == '')]
    config = comun.cargar_yaml(a.prioritarias) if a.prioritarias.exists() else {}
    sintetico = (a.entrada / 'DATOS_SINTETICOS.txt').exists()
    aviso = 'DATOS SINTÉTICOS · SOLO PRUEBA DEL PIPELINE' if sintetico else ''
    ruta_pdf = a.pdf or s / 'informe.pdf'
    ruta_pdf.parent.mkdir(parents=True, exist_ok=True)
    inf = Informe(ruta_pdf, aviso)

    versiones = meta.get('versiones', {})
    alertas = qc[qc['alertas'] != 'ninguna'] if not qc.empty else qc
    inf.texto('Perfil radiómico de metástasis hepáticas colorrectales', [
        'Informe del pipeline de radiómica (TC con contraste en fase portal, una lesión índice por paciente).'
        + (' Generado con DATOS SINTÉTICOS: las cifras no describen a ningún paciente ni sirven para conclusiones.'
           if sintetico else ''),
        f'Fecha del informe: {date.today().isoformat()}.',
        f'Lesiones: {len(qc)} · con alertas de calidad: {len(alertas)} · con dos observadores: {len(seg)}.',
        f'Extracción: pyRadiomics {versiones.get("pyradiomics", "?")}, imagen original en UH, 3D, remuestreo a '
        f'1×1×1 mm, anchura de intervalo {num(meta.get("binWidth"), 0)} UH, sin filtros. '
        f'Huella de params.yaml: {str(meta.get("params_sha256", "?"))[:12]}…',
        'Contenido: cómo leer el informe y cada medida; 1) control de calidad; 2) homogeneidad técnica; 3) reproducibilidad interobservador '
        '(Dice, Hausdorff 95, ICC); 4) perfil radiómico descriptivo; 5) distribuciones; 6) correlación de '
        'Spearman; 7) cómo se calculó.',
        'Estudio descriptivo: no incluye modelos predictivos, curvas ROC ni contrastes entre subgrupos.',
    ])
    inf.texto('Cómo leer este informe', COMO_LEER)
    inf.texto('Cómo leer cada estadístico', COMO_LEER_ESTADISTICOS)
    if config.get('caracteristicas'):
        inf.texto('Cómo leer cada medida', fichas_medidas(config))

    if not qc.empty:
        col_menor = next((c for c in qc.columns if c.startswith('menor_')), None)
        inf.tabla('1 · Control de calidad', ['Caso', 'Vol. (mL)', 'Ø axial (mm)', 'Ø 3D (mm)', 'Alertas'],
                  [[f['id'], num(f['volumen_ml'], 2), num(f['diametro_axial_max_mm']), num(f['diametro_3d_max_mm']),
                    f['alertas']] for _, f in qc.iterrows()],
                  [9, 7, 7, 7, 16],
                  'Ø axial: mayor diámetro en un corte axial (criterio RECIST 1.1 de lesión medible, ≥ 10 mm). '
                  'Ø 3D: mayor distancia entre centros de vóxel del borde. '
                  f'Lesiones por debajo de 10 mm: {int(qc[col_menor].sum()) if col_menor else 0}.')
        inf.texto('1 · Qué dicen tus datos', lectura_qc(qc))
    if not het.empty:
        inf.tabla('2 · Homogeneidad técnica', ['Variable', 'Valor', 'n', '%'],
                  [[f['variable'], f['valor'], f['n'], num(f['porcentaje'])] for _, f in het.iterrows()],
                  [12, 20, 4, 6], 'Cuántas TC hay de cada equipo, tensión (kVp), filtro de reconstrucción (kernel), '
                  'grosor de corte y tamaño de píxel. Lo leído de la cabecera DICOM de cada serie.')

    if not seg.empty:
        inf.tabla('3 · Reproducibilidad: segmentación', ['Caso', 'Dice', 'HD95 (mm)', 'Vóx. obs1', 'Vóx. obs2'],
                  [[f['id'], num(f['dice'], 3), num(f['hd95_mm'], 2), f['voxeles_obs1'], f['voxeles_obs2']]
                   for _, f in seg.iterrows()], [9, 6, 7, 7, 7],
                  f'Dice: mediana {num(seg["dice"].median(), 3)} (rango {num(seg["dice"].min(), 3)}–'
                  f'{num(seg["dice"].max(), 3)}). HD95: mediana {num(seg["hd95_mm"].median(), 2)} mm. '
                  'Dice 1 = segmentaciones idénticas; HD95 = distancia (mm) por debajo de la cual queda el 95 % '
                  'del borde de una segmentación respecto a la otra.')
        inf.texto('3 · Qué dicen tus datos: contornos', lectura_segmentacion(seg, qc))
    if not icc.empty:
        # [HUECO b-009: lectura del ICC] Aquí irá «Qué dicen tus datos» del ICC, con la función de etiquetas
        # de fiabilidad (tramos de Koo y Li leídos sobre el IC 95 %).
        def tabla_icc(titulo, t):
            nombre = lambda c: c.replace('original_', '').replace('_', ' · ', 1)  # noqa: E731
            filas = [[nombre(f['caracteristica']), num(f['icc'], 3), f'{num(f["ic95_inf"], 2)} a {num(f["ic95_sup"], 2)}',
                      f['nota'] if isinstance(f['nota'], str) else ''] for _, f in t.iterrows()]
            notas = [f[3] for f in filas if f[3]]
            nota = ('ICC(2,1): dos factores, efectos aleatorios, acuerdo absoluto, medida única (pingouin, «ICC2»), '
                    'con IC 95 %. Se muestran todos los valores, sin umbral que declare «válida» una característica.')
            if notas:  # columna «Nota» solo si alguna fila la usa
                inf.tabla(titulo, ['Característica', 'ICC', 'IC 95 %', 'Nota'], filas, [22, 6, 11, 11], nota)
            else:
                inf.tabla(titulo, ['Característica', 'ICC', 'IC 95 %'], [f[:3] for f in filas], [28, 7, 13], nota)
        tabla_icc('3 · ICC de las prioritarias', icc[icc['prioritaria']])
        tabla_icc('3 · ICC de todas las características', icc)

    if not desc.empty:
        inf.tabla('4 · Perfil radiómico', ['Característica (unidad)', 'Media ± DE', 'Mediana (RIC)', 'Mín – máx'],
                  [[f'{f["orden"]}. {f["caracteristica"]} ({f["unidad"]})', f'{num(f.get("media"))} ± {num(f.get("de"))}',
                    f'{num(f.get("mediana"))} ({num(f.get("p25"))} – {num(f.get("p75"))})',
                    f'{num(f.get("minimo"))} – {num(f.get("maximo"))}'] for _, f in desc.iterrows()],
                  [15, 11, 13, 11], 'DE: desviación estándar de la muestra. RIC: percentiles 25 y 75.')
        inf.tabla('4 · Variabilidad y ausentes', ['Característica', 'n', 'Ausentes', 'CV (%)', 'Nota'],
                  [[f'{f["orden"]}. {f["caracteristica"]}', f['n'], f['ausentes'], num(f.get('cv_pct')),
                    f['nota'] if isinstance(f.get('nota'), str) else ''] for _, f in desc.iterrows()],
                  [16, 3, 6, 6, 16], 'CV = DE / |media| × 100. Se omite en escalas sin cero verdadero (UH) o con '
                  'valores ≤ 0 (protocolo §11.2).')
        inf.texto('4 · Qué dicen tus datos', lectura_descriptivo(desc, datos))

    figuras = sorted((s / 'figuras').glob('distribucion_*.png'))
    if figuras:
        inf.imagenes('5 · Distribuciones', figuras)
    if (s / 'figuras' / 'spearman.png').exists():
        leyenda = [f'{f["orden"]}. {f["caracteristica"]}' for _, f in desc.iterrows()] if not desc.empty else []
        inf.imagen_con_leyenda('6 · Correlación de Spearman', s / 'figuras' / 'spearman.png', [
            'Rojo: correlación positiva; azul: negativa. Exploratoria: muestra qué características son redundantes '
            'entre sí; no es evidencia de asociación clínica (protocolo §11.2).', ''] + leyenda)

    inf.texto('7 · Cómo se calculó', [
        'Conversión: DICOM → NIfTI sin metadatos; la segmentación (NRRD de 3D Slicer o DICOM-SEG) se coloca en la '
        'rejilla de la imagen sin interpolar. El informe de anonimización (anonimizacion.csv) solo nombra los '
        'atributos identificadores del origen, nunca sus valores.',
        'Extracción: pyRadiomics con config/params.yaml. Remuestreo a 1×1×1 mm (imagen: interpolación lineal; '
        'máscara: vecino más próximo). Discretización de anchura fija. Clases: primer orden, forma, GLCM, GLRLM y '
        'GLSZM. Definiciones y diferencias con IBSI en docs/diccionario_variables.md.',
        'Reproducibilidad: Dice; Hausdorff 95 = el mayor de los dos percentiles 95 dirigidos de la distancia entre '
        'bordes; ICC(2,1) de acuerdo absoluto con IC 95 % (pingouin).',
        'Descriptiva: media, DE (n−1), mediana, RIC, mínimo, máximo, ausentes y CV donde procede.',
        f'Software: {", ".join(f"{k} {v}" for k, v in versiones.items())}.',
    ])
    inf.cerrar()
    print(f'Paso 6: informe de {inf.n_pagina} páginas → {ruta_pdf}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
