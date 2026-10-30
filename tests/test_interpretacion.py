"""Pruebas de la guía en llano: cada característica prioritaria tiene su explicación, la guía las nombra todas,
el informe trae las páginas «Cómo leer» y los párrafos «Qué dicen tus datos» dicen las cifras correctas.
Solo datos sintéticos o inventados aquí mismo, de resultado conocido."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
for ruta in (RAIZ, RAIZ / 'src', RAIZ / 'tests'):
    sys.path.insert(0, str(ruta))

import comun  # noqa: E402
import generar_sinteticos  # noqa: E402
import run_pipeline  # noqa: E402

informe = run_pipeline.cargar('06_informe')
CONFIG = comun.cargar_yaml(RAIZ / 'config' / 'features_prioritarias.yaml')
PRIORITARIAS = CONFIG['caracteristicas']


# ------------------------------------------------------------------------------------- yaml y guía
def test_yaml_tiene_las_19_con_explicacion():
    assert len(PRIORITARIAS) == 19
    for c in PRIORITARIAS:
        assert str(c.get('en_llano', '')).strip(), c['columna']
        assert str(c.get('valor_alto', '')).strip(), c['columna']
        assert 'aviso' in c, c['columna']            # puede ser "", pero tiene que estar


def test_avisos_obligatorios():
    """Los avisos que pide el Consejo: tamaño (GLN, SZN, superficie/volumen), curtosis +3, binWidth."""
    aviso = {c['columna']: c['aviso'] for c in PRIORITARIAS}
    for col in ('original_glrlm_GrayLevelNonUniformity', 'original_glszm_SizeZoneNonUniformity',
                'original_shape_SurfaceVolumeRatio'):
        assert 'tamaño' in aviso[col]
    assert '3' in aviso['original_firstorder_Kurtosis'] and 'IBSI' in aviso['original_firstorder_Kurtosis']
    for c in PRIORITARIAS:
        if c['columna'].split('_')[1] in ('glcm', 'glrlm', 'glszm') or c['columna'].endswith('Entropy'):
            assert 'binWidth' in c['aviso'], c['columna']


def test_guia_nombra_las_19_columnas():
    guia = (RAIZ / 'docs' / 'guia_interpretacion.md').read_text(encoding='utf-8')
    for c in PRIORITARIAS:
        assert c['columna'] in guia, c['columna']
    for termino in ('Dice', 'HD95', 'ICC', 'IC 95 %', 'Spearman', 'CV', 'Mediana', 'Ausentes', 'sin fuente'):
        assert termino in guia, termino


# ------------------------------------------------------------------------- «Qué dicen tus datos»
def test_atipicos_regla_del_diagrama_de_caja():
    # p25 = 2, p75 = 4 → RIC 2 → bigotes hasta −1 y 7: solo el 100 queda fuera.
    assert informe.atipicos(pd.Series([1, 2, 3, 4, 100]), 2, 4) == 1
    assert informe.atipicos(pd.Series([1, 2, 3, 4, 7]), 2, 4) == 0
    assert informe.atipicos(pd.Series([None, 3.0]), 2, 4) == 0       # el vacío no cuenta como 0


def test_lectura_descriptivo_cifras_conocidas():
    desc = pd.DataFrame([
        {'orden': 1, 'caracteristica': 'Media', 'columna': 'original_firstorder_Mean', 'unidad': 'UH', 'n': 5,
         'ausentes': 0, 'media': 15.0, 'mediana': 15.0, 'p25': 10.0, 'p75': 20.0, 'minimo': 5.0, 'maximo': 25.0,
         'cv_pct': None},
        {'orden': 2, 'caracteristica': 'GLRLM LRE', 'columna': 'original_glrlm_LongRunEmphasis', 'unidad': '—',
         'n': 3, 'ausentes': 2, 'media': 40.0, 'mediana': 3.0, 'p25': 2.0, 'p75': 4.0, 'minimo': 1.0,
         'maximo': 100.0, 'cv_pct': 150.0},
    ])
    datos = pd.DataFrame({'original_firstorder_Mean': [5, 10, 15, 20, 25],
                          'original_glrlm_LongRunEmphasis': [1, 3, 100, None, None]})
    texto = ' '.join(informe.lectura_descriptivo(desc, datos))
    assert 'entre 10,00 y 20,00 UH' in texto
    assert 'GLRLM LRE (CV 150 %)' in texto
    assert 'GLRLM LRE (media 40,00, mediana 3,00)' in texto        # media fuera del RIC
    assert 'GLRLM LRE (1)' in texto                                # un atípico: el 100
    assert 'GLRLM LRE (2)' in texto and 'nunca 0' in texto          # dos ausentes


def test_lectura_segmentacion_cifras_conocidas():
    seg = pd.DataFrame({'id': ['SINT-001', 'SINT-002', 'SINT-003'], 'dice': [1.0, 0.9, 0.6],
                        'hd95_mm': [0.0, 1.0, 3.0]})
    qc = pd.DataFrame({'id': ['SINT-003'], 'volumen_ml': [0.5]})
    texto = ' '.join(informe.lectura_segmentacion(seg, qc))
    assert '3 lesiones' in texto and 'Dice mediano fue 0,90' in texto and 'de 0,60 a 1,00' in texto
    assert 'SINT-003 (0,60, una lesión de 0,50 mL)' in texto
    assert 'HD95 mediano: 1,00 mm' in texto


def test_lectura_qc_cuenta_alertas():
    qc = pd.DataFrame({'id': ['A', 'B'], 'alertas': ['ninguna', 'diámetro axial < 10 mm'],
                       'diametro_axial_max_mm': [20.0, 8.0], 'volumen_ml': [4.0, 0.2]})
    texto = ' '.join(informe.lectura_qc(qc))
    assert '1 de 2 lesiones' in texto and 'B (diámetro axial < 10 mm)' in texto
    assert 'de 8,00 a 20,00 mm' in texto


def test_fichas_salen_del_yaml():
    fichas = informe.fichas_medidas(CONFIG)
    assert sum(f.startswith('## ') for f in fichas) == 19
    assert any('3 más alto' in f for f in fichas)


# ---------------------------------------------------------------------------- PDF del pipeline
@pytest.fixture(scope='module')
def pdf_sintetico(tmp_path_factory):
    base = tmp_path_factory.mktemp('interpretacion')
    data, outputs = base / 'data', base / 'outputs'
    generar_sinteticos.generar(data, 10, 42)
    assert run_pipeline.main(['--input', str(data), '--output', str(outputs)]) == 0
    return outputs / 'informe.pdf'


def test_pdf_trae_como_leer(pdf_sintetico):
    pdf = pdf_sintetico.read_bytes()
    assert pdf.startswith(b'%PDF')
    if not shutil.which('pdftotext'):
        pytest.skip('sin pdftotext: solo se comprueba que el PDF existe')
    texto = subprocess.run(['pdftotext', str(pdf_sintetico), '-'], capture_output=True, text=True,
                           check=True).stdout
    texto = " ".join(texto.split())               # une las líneas partidas
    for frase in ('Cómo leer este informe', 'Cómo leer cada estadístico', 'Cómo leer cada medida',
                  'Qué dicen tus datos', 'Dice mediano fue'):
        assert frase in texto, frase
