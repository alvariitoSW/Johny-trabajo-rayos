"""Pruebas del resumen para el móvil (src/07_resumen_movil.py) con DATOS SINTÉTICOS."""
from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
for ruta in (RAIZ, RAIZ / 'src', RAIZ / 'tests'):
    sys.path.insert(0, str(ruta))

import generar_sinteticos  # noqa: E402
import run_pipeline  # noqa: E402

_espec = importlib.util.spec_from_file_location('resumen_movil', RAIZ / 'src' / '07_resumen_movil.py')
resumen = importlib.util.module_from_spec(_espec)
_espec.loader.exec_module(resumen)


@pytest.fixture(scope='module')
def corrida(tmp_path_factory):
    base = tmp_path_factory.mktemp('resumen')
    data, outputs = base / 'data', base / 'outputs'
    generar_sinteticos.generar(data, 10, 42)
    assert run_pipeline.main(['--input', str(data), '--output', str(outputs)]) == 0
    assert resumen.main(['--entrada', str(data), '--salida', str(outputs)]) == 0
    return data, outputs, (outputs / 'resumen_movil.html').read_text(encoding='utf-8')


def test_html_existe_y_es_autocontenido(corrida):
    _, outputs, texto = corrida
    assert (outputs / 'resumen_movil.html').exists()
    assert '<script' not in texto and 'http' not in texto
    assert 'Dice' in texto and 'DATOS SINTÉTICOS' in texto
    assert 'delegado de protección de datos' in texto


def test_sin_codigos_de_caso(corrida):
    assert 'SINT-0' not in corrida[2]


def test_recuentos_pequenos_ocultos(corrida):
    _, outputs, texto = corrida
    qc = pd.read_csv(outputs / 'qc_report.csv')
    assert 0 < (qc['alertas'] != 'ninguna').sum() < 5  # en el sintético hay 2 alertas
    assert '<td>Con alguna alerta</td><td>&lt; 5</td>' in texto


def test_recuento_funcion():
    assert [resumen.recuento(n) for n in (0, 1, 4, 5, 12)] == ['0', '< 5', '< 5', '5', '12']


def test_tres_casos_no_se_resume(corrida, tmp_path):
    data, outputs, _ = corrida
    chico = tmp_path / 'outputs'
    chico.mkdir()
    for f in outputs.glob('*.csv'):
        pd.read_csv(f).head(3).to_csv(chico / f.name, index=False)
    shutil.copy(outputs / 'extraccion_meta.json', chico)
    assert resumen.main(['--entrada', str(data), '--salida', str(chico)]) == 0
    texto = (chico / 'resumen_movil.html').read_text(encoding='utf-8')
    assert 'demasiado pequeña' in texto and 'SINT-0' not in texto
    assert 'Mediana' not in texto
