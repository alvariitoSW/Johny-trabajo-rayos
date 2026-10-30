"""Pruebas de la etiqueta de fiabilidad, el aviso de pocos casos y el sorteo del segundo observador (datos sintéticos)."""
from __future__ import annotations

import json
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

sorteo = run_pipeline.cargar('seleccion_reproducibilidad')
NAN = float('nan')


@pytest.mark.parametrize('inf,sup,esperado', [
    (0.92, 0.98, 'excelente'), (0.18, 1.0, 'de pobre a excelente'), (0.6, 0.7, 'moderada'),
    (0.8, 0.85, 'buena'), (0.5, 0.75, 'de moderada a buena'), (0.75, 0.9, 'buena'),
    (NAN, 0.9, 'no calculable'), (0.4, NAN, 'no calculable')])
def test_fiabilidad_koo_li(inf, sup, esperado):
    assert comun.fiabilidad_koo_li(inf, sup) == esperado


def _correr(tmp_path, n, semilla=None, nombre='s'):
    carpeta = tmp_path / f'crudo{n}'
    if not carpeta.exists():
        for i in range(1, n + 1):
            (carpeta / f'RMH-{i:03d}').mkdir(parents=True)
    sal = tmp_path / f'{nombre}{n}_{semilla}'
    args = ['--casos', str(carpeta), '--salida', str(sal)]
    if semilla is not None:
        args += ['--semilla', str(semilla)]
    assert sorteo.main(args) == 0
    lista = pd.read_csv(sal / 'seleccion_reproducibilidad.csv')['id'].tolist()
    return lista, json.loads((sal / 'seleccion_reproducibilidad.json').read_text(encoding='utf-8'))


def test_sorteo_misma_semilla_misma_lista_y_otra_distinta(tmp_path):
    a, _ = _correr(tmp_path, 50, 1, 'a')
    b, _ = _correr(tmp_path, 50, 1, 'b')
    c, _ = _correr(tmp_path, 50, 2, 'c')
    assert a == b and a == sorted(a) and a != c


def test_sorteo_tamanos(tmp_path):
    l50, j50 = _correr(tmp_path, 50)
    assert len(l50) == 15 and j50['n'] == 15 and j50['aviso'] == '' and j50['semilla'] == 20261030
    l40, _ = _correr(tmp_path, 40)
    assert len(l40) == 15  # 30 % = 12 < 15
    l100, _ = _correr(tmp_path, 100)
    assert len(l100) == 30
    l10, j10 = _correr(tmp_path, 10)
    assert len(l10) == 10 and j10['aviso'] != ''


def test_sorteo_codigo_malo_da_error(tmp_path):
    txt = tmp_path / 'lista.txt'
    txt.write_text('RMH-001\nJuan Perez\n', encoding='utf-8')
    with pytest.raises(Exception):
        sorteo.main(['--casos', str(txt), '--salida', str(tmp_path / 'x')])


def test_resumen_con_aviso_menos_de_15_casos(tmp_path):
    data, outputs = tmp_path / 'data', tmp_path / 'outputs'
    generar_sinteticos.generar(data, 6, 42)
    assert run_pipeline.main(['--input', str(data), '--output', str(outputs)]) == 0
    r = json.loads((outputs / 'reproducibilidad_resumen.json').read_text(encoding='utf-8'))
    assert r['n_casos'] == len(pd.read_csv(outputs / 'reproducibilidad_segmentacion.csv')) < 15 and r['minimo_protocolo'] == 15 and r['aviso'] != ''
    assert r['dice_mediana'] is not None and r['hd95_mediana_mm'] is not None
    icc = pd.read_csv(outputs / 'reproducibilidad_icc.csv')
    assert {'fiabilidad_koo_li', 'cautela'} <= set(icc.columns)
