"""Pruebas de las decisiones sobre los casos (asunto 2 del Consejo del 30/10/2026), del flujo de casos y de la
lectura del ICC en el PDF. Solo datos sintéticos: SINT-005 (lesión de 8 mm) y SINT-008 (dos componentes)."""
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

qc3 = run_pipeline.cargar('03_qc')
informe = run_pipeline.cargar('06_informe')


@pytest.fixture(scope='module')
def sin_csv(tmp_path_factory):
    base = tmp_path_factory.mktemp('decisiones')
    data, outputs = base / 'data', base / 'outputs'
    generar_sinteticos.generar(data, 10, 42)
    assert run_pipeline.main(['--input', str(data), '--output', str(outputs)]) == 0
    return data, outputs


@pytest.fixture(scope='module')
def con_csv(sin_csv, tmp_path_factory):
    """Mismos datos, con el radiólogo decidiendo: SINT-008 se incluye. Se repite desde el paso 3."""
    data, outputs0 = sin_csv
    outputs = tmp_path_factory.mktemp('decisiones_csv') / 'outputs'
    shutil.copytree(outputs0, outputs)
    (data / 'decisiones_casos.csv').write_text(
        'id,decision,motivo\nSINT-008,incluir,un solo nódulo tras mirar la imagen\n', encoding='utf-8')
    try:
        assert run_pipeline.main(['--input', str(data), '--output', str(outputs), '--desde', '3']) == 0
    finally:
        (data / 'decisiones_casos.csv').unlink()
    return outputs


def test_sin_csv_propuestas_y_decisiones(sin_csv):
    _, outputs = sin_csv
    qc = pd.read_csv(outputs / 'qc_report.csv').set_index('id')
    assert qc.loc['SINT-005', 'decision_propuesta'] == 'excluir' and qc.loc['SINT-005', 'decision'] == 'excluir'
    assert qc.loc['SINT-008', 'decision_propuesta'] == 'revisar' and qc.loc['SINT-008', 'decision'] == 'revisar'
    limpios = qc.drop(index=['SINT-005', 'SINT-008'])
    assert (limpios['decision'] == 'incluir').all() and (limpios['decision_propuesta'] == 'incluir').all()
    assert qc.loc['SINT-005', 'motivo'] != '' and (qc.loc[limpios.index, 'motivo'].fillna('') == '').all()


def test_sin_csv_no_se_analizan_en_4_y_5(sin_csv):
    _, outputs = sin_csv
    seg = pd.read_csv(outputs / 'reproducibilidad_segmentacion.csv')
    assert not {'SINT-005', 'SINT-008'} & set(seg['id'])
    desc = pd.read_csv(outputs / 'descriptivo.csv')
    assert (desc['n'] == 8).all()                       # 10 extraídos − 2 sin incluir
    assert len(pd.read_csv(outputs / 'features.csv')) == 10   # la extracción sigue siendo de los 10


def test_flujo_cuenta_todo(sin_csv):
    _, outputs = sin_csv
    f = dict(pd.read_csv(outputs / 'flujo_casos.csv').values)
    qc = pd.read_csv(outputs / 'qc_report.csv')
    assert f['Casos evaluados'] == 10 and f['Con alguna alerta'] == 2 and f['Excluidos'] == 1
    assert f['· motivo: lesión menor de 10 mm'] == 1
    assert f['Pendientes de revisar'] == 1 and f['Analizados'] == 8
    assert f['Con dos observadores analizados'] == len(pd.read_csv(outputs / 'reproducibilidad_segmentacion.csv'))
    assert f['Analizados'] == (qc['decision'] == 'incluir').sum()


def test_con_csv_el_caso_decidido_se_analiza(con_csv):
    qc = pd.read_csv(con_csv / 'qc_report.csv').set_index('id')
    assert qc.loc['SINT-008', 'decision'] == 'incluir' and qc.loc['SINT-008', 'decision_origen'] == 'archivo'
    assert qc.loc['SINT-008', 'decision_propuesta'] == 'revisar'      # la propuesta no cambia
    assert 'un solo nódulo' in qc.loc['SINT-008', 'motivo']
    assert (pd.read_csv(con_csv / 'descriptivo.csv')['n'] == 9).all()
    f = dict(pd.read_csv(con_csv / 'flujo_casos.csv').values)
    assert f['Analizados'] == 9 and f['Pendientes de revisar'] == 0 and f['Excluidos'] == 1


def test_csv_malo_da_error(tmp_path):
    ruta = tmp_path / 'decisiones_casos.csv'
    ruta.write_text('id,decision,motivo\nSINT-001,quizá,\n', encoding='utf-8')
    with pytest.raises(ValueError):
        comun.leer_decisiones(ruta)
    ruta.write_text('codigo,decision,motivo\nSINT-001,incluir,\n', encoding='utf-8')
    with pytest.raises(ValueError):
        comun.leer_decisiones(ruta)
    assert comun.leer_decisiones(tmp_path / 'no_existe.csv') == {}


def test_propuesta_solo_excluye_por_diametro():
    assert qc3.proponer('ninguna') == 'incluir'
    assert qc3.proponer('diámetro axial < 10 mm') == 'excluir'
    assert qc3.proponer('2 componentes') == 'revisar'
    assert qc3.proponer('2 componentes; diámetro axial < 10 mm') == 'revisar'
    assert qc3.proponer('máscara vacía') == 'revisar'


def test_ids_analizados_sin_qc_no_filtra(tmp_path):
    assert comun.ids_analizados(tmp_path) is None


def _texto_pdf(pdf: Path) -> str:
    if not shutil.which('pdftotext'):
        pytest.skip('sin pdftotext')
    t = subprocess.run(['pdftotext', str(pdf), '-'], capture_output=True, text=True, check=True).stdout
    return ' '.join(t.split())


def test_pdf_trae_flujo_icc_y_nombres_legibles(sin_csv):
    _, outputs = sin_csv
    t = _texto_pdf(outputs / 'informe.pdf')
    for frase in ('Flujo de casos', 'Qué dicen tus datos', 'Fiabilidad', 'Koo y Li', 'interpretar con cautela',
                  'Grosor de corte (mm)', 'Tamaño de píxel (mm)', 'tienen ICC calculable'):
        assert frase in t, frase
    assert 'grosor_corte_mm' not in t


def test_lectura_icc_cifras_conocidas():
    icc = pd.DataFrame({'caracteristica': ['a', 'b', 'c', 'd'], 'prioritaria': [True, True, True, False],
                        'icc': [0.95, 0.9, 0.99, 0.5], 'ic95_inf': [0.92, 0.3, 0.18, 0.0],
                        'ic95_sup': [0.98, 0.97, 1.0, 0.9]})
    f = informe.lectura_icc(icc, {'aviso': 'Solo hay 6 casos'}, {'c': 'Percentil 10'})
    texto = ' '.join(f)
    assert 'De 3 características prioritarias, 3 tienen ICC calculable' in texto
    assert 'En 1 el intervalo entero' in texto           # solo «a» (0,92 a 0,98) es buena/excelente
    assert 'En 2 el límite inferior' in texto            # b y c por debajo de 0,5
    assert 'Percentil 10: de 0,18 a 1,00' in texto and 'Aviso: Solo hay 6 casos' in texto


def test_resumen_movil_con_flujo_y_pipeline_lo_genera(sin_csv):
    _, outputs = sin_csv
    html = (outputs / 'resumen_movil.html').read_text(encoding='utf-8')
    assert 'Flujo de casos' in html and 'SINT-0' not in html
    assert '<td>Excluidos</td><td>&lt; 5</td>' in html and '<td>Analizados</td><td>8</td>' in html
