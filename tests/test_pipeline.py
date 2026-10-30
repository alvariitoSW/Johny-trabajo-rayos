"""Pruebas del pipeline con DATOS SINTÉTICOS (tests/generar_sinteticos.py): el pipeline entero de principio a fin
con 10 casos, y cada cálculo frente a un resultado conocido.

Ejecutar desde la carpeta del proyecto:  python -m pytest tests -q
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import SimpleITK as sitk

RAIZ = Path(__file__).resolve().parents[1]
for ruta in (RAIZ, RAIZ / 'src', RAIZ / 'tests'):
    sys.path.insert(0, str(ruta))

import comun  # noqa: E402
import generar_sinteticos  # noqa: E402
import run_pipeline  # noqa: E402

convertir = run_pipeline.cargar('01_convertir')
reproducibilidad = run_pipeline.cargar('04_reproducibilidad')


@pytest.fixture(scope='session')
def ejecucion(tmp_path_factory):
    base = tmp_path_factory.mktemp('sintetico')
    data, outputs = base / 'data', base / 'outputs'
    verdad = generar_sinteticos.generar(data, 10, 42)
    codigo = run_pipeline.main(['--input', str(data), '--output', str(outputs)])
    return data, outputs, verdad, codigo


# ---------------------------------------------------------------------------------------- de principio a fin
def test_pipeline_completo_sin_errores(ejecucion):
    data, outputs, _, codigo = ejecucion
    assert codigo == 0
    for nombre in ['anonimizacion.csv', 'features.csv', 'extraccion_meta.json', 'qc_report.csv',
                   'qc_heterogeneidad_tecnica.csv', 'reproducibilidad_segmentacion.csv', 'reproducibilidad_icc.csv',
                   'descriptivo.csv', 'spearman.csv', 'informe.pdf', 'figuras/spearman.png']:
        assert (outputs / nombre).exists(), nombre
    assert len(list((data / 'casos').iterdir())) == 10


def test_ningun_identificador_llega_a_las_salidas(ejecucion):
    data, outputs, _, _ = ejecucion
    anon = pd.read_csv(outputs / 'anonimizacion.csv')
    assert (anon['resultado'] == 'OK').all()
    assert anon['identificadores_en_origen'].str.contains('PatientName').all()  # el origen sí los tenía
    falsos = [v.encode() for v in generar_sinteticos.FALSOS.values()]
    for nifti in (data / 'casos').glob('*/*.nii.gz'):
        cabecera = convertir.cabecera_nifti(nifti)
        assert not any(v in cabecera for v in falsos), nifti
    for texto in list((data / 'casos').glob('*/*.json')) + list(outputs.glob('*.csv')) + list(outputs.glob('*.json')):
        contenido = texto.read_bytes()
        assert not any(v in contenido for v in falsos), texto


def test_features_trazables(ejecucion):
    _, outputs, _, _ = ejecucion
    f = pd.read_csv(outputs / 'features.csv')
    assert len(f) == 10 and f['error'].isna().all()
    assert (f['params_sha256'] == comun.sha256(comun.CONFIG / 'params.yaml')).all()
    assert (f['binwidth'] == 25).all()
    for col in ['fabricante', 'modelo', 'kvp', 'kernel', 'grosor_corte_mm', 'pixel_spacing_mm', 'ma']:
        assert f[col].notna().all(), col
    prioritarias = [c['columna'] for c in comun.cargar_yaml(comun.CONFIG / 'features_prioritarias.yaml')['caracteristicas']]
    assert set(prioritarias) <= set(f.columns)  # incluida StandardDeviation, desactivada por defecto en pyRadiomics


def test_atenuacion_y_volumen_conocidos(ejecucion):
    _, outputs, verdad, _ = ejecucion
    f = pd.read_csv(outputs / 'features.csv').set_index('id')
    for id_caso, v in verdad.items():
        if v['segundo_componente'] or min(v['semiejes_mm']) < 6:
            continue  # SINT-008 lleva un nódulo de más; en lesiones pequeñas pesa el volumen parcial del borde
        assert abs(f.loc[id_caso, 'original_firstorder_Mean'] - v['lesion_uh']) < 5, id_caso
        assert abs(f.loc[id_caso, 'original_shape_MeshVolume'] / v['volumen_mm3'] - 1) < 0.10, id_caso


def test_qc_caza_las_trampas_y_mide_bien(ejecucion):
    _, outputs, verdad, _ = ejecucion
    qc = pd.read_csv(outputs / 'qc_report.csv').set_index('id')
    assert bool(qc.loc['SINT-005', 'menor_10mm'])
    assert qc.loc['SINT-008', 'componentes'] == 2
    limpios = qc.drop(index=['SINT-005', 'SINT-008'])
    assert (limpios['alertas'] == 'ninguna').all()
    for id_caso in limpios.index:  # entre centros de vóxel: como mucho ~1 vóxel por debajo del real
        real = verdad[id_caso]['diametro_axial_mm']
        assert real - 1.6 <= qc.loc[id_caso, 'diametro_axial_max_mm'] <= real + 0.1, id_caso
    het = pd.read_csv(outputs / 'qc_heterogeneidad_tecnica.csv')
    assert set(het.loc[het['variable'] == 'kvp', 'valor']) == {'100.0', '120.0'}


def test_reproducibilidad(ejecucion):
    _, outputs, verdad, _ = ejecucion
    seg = pd.read_csv(outputs / 'reproducibilidad_segmentacion.csv')
    # SINT-005 (excluir propuesto) y SINT-008 (revisar sin decidir) no se analizan (asunto 2 del Consejo 30/10)
    esperados = {i for i, v in verdad.items() if v['dos_observadores']} - {'SINT-005', 'SINT-008'}
    assert set(seg['id']) == esperados and len(seg) >= 5
    assert seg['dice'].between(0.6, 0.99).all() and (seg['hd95_mm'] > 0).all()
    icc = pd.read_csv(outputs / 'reproducibilidad_icc.csv')
    assert len(icc) == len(pd.read_csv(outputs / 'features.csv').filter(like='original_').columns)
    assert icc['prioritaria'].sum() == 19 and icc['icc'].notna().sum() > 80


def test_informe_pdf(ejecucion):
    _, outputs, _, _ = ejecucion
    pdf = (outputs / 'informe.pdf').read_bytes()
    assert pdf.startswith(b'%PDF') and len(pdf) > 50_000


def test_binwidth_10_cambia_la_textura(ejecucion, tmp_path):
    data, outputs, _, _ = ejecucion
    assert run_pipeline.cargar('02_extraer').main(['--entrada', str(data), '--salida', str(tmp_path),
                                                    '--binwidth', '10']) == 0
    a = pd.read_csv(outputs / 'features.csv').set_index('id')
    b = pd.read_csv(tmp_path / 'features.csv').set_index('id')
    assert (b['binwidth'] == 10).all()
    assert (b['original_firstorder_Entropy'] > a['original_firstorder_Entropy']).all()  # más intervalos
    assert np.allclose(b['original_firstorder_Mean'], a['original_firstorder_Mean'])   # no depende de binWidth


# --------------------------------------------------------------------------------- cálculos de resultado conocido
def esfera(centro, radio, tam=40):
    z, y, x = np.mgrid[:tam, :tam, :tam]
    return (x - centro[0]) ** 2 + (y - centro[1]) ** 2 + (z - centro[2]) ** 2 <= radio ** 2


def test_dice_y_hd95_conocidos():
    a = esfera((20, 20, 20), 8)
    assert reproducibilidad.dice(a, a) == 1.0
    assert reproducibilidad.hd95(a, a, (1, 1, 1)) == 0.0
    assert reproducibilidad.dice(a, esfera((5, 5, 5), 3)) == 0.0
    desplazada = esfera((22, 20, 20), 8)  # 2 mm en x
    assert 1.0 <= reproducibilidad.hd95(a, desplazada, (1, 1, 1)) <= 2.0 + 1e-9
    # Con vóxeles de 2 mm la misma figura mide el doble: el HD95 se dobla exactamente.
    assert reproducibilidad.hd95(a, desplazada, (2, 2, 2)) == pytest.approx(2 * reproducibilidad.hd95(a, desplazada, (1, 1, 1)))


def test_icc_de_observadores_identicos_es_1():
    rng = np.random.default_rng(0)
    valores = rng.normal(50, 10, 8)
    largo = pd.DataFrame({'id': [f'C{i}' for i in range(8)] * 2, 'observador': ['obs1'] * 8 + ['obs2'] * 8,
                          'caracteristica': 'x', 'valor': np.concatenate([valores, valores])})
    tabla = reproducibilidad.icc_por_caracteristica(largo, {'x'})
    assert tabla['icc'].iloc[0] == pytest.approx(1.0)
    constante = largo.assign(valor=5.0)
    assert 'no calculable' in reproducibilidad.icc_por_caracteristica(constante, set())['nota'].iloc[0]


def test_codigos_de_caso():
    comun.comprobar_id('RMH-001')
    for malo in ['Juan Perez', '12345678', 'RMH 001', '../RMH-001']:
        with pytest.raises(ValueError):
            comun.comprobar_id(malo)


def test_mascara_con_otro_espaciado_no_se_interpola():
    imagen = sitk.Image(20, 20, 10, sitk.sitkInt16)
    imagen.SetSpacing((0.8, 0.8, 2.5))
    mascara = sitk.Image(20, 20, 10, sitk.sitkUInt8)
    mascara.SetSpacing((1.0, 1.0, 1.0))
    with pytest.raises(ValueError):
        convertir.a_rejilla_de_imagen(mascara, imagen)


def test_params_se_lee_bien_con_la_codificacion_de_windows(monkeypatch):
    """En Windows, un open() sin codificación usa cp1252 y los acentos de params.yaml rompían pyRadiomics (CI del
    30/10/2026). Se simula aquí: todo open() de texto sin codificación pasa a cp1252."""
    import builtins
    abrir = builtins.open

    def abrir_como_windows(archivo, modo='r', *args, **kwargs):
        if 'b' not in modo and not args and kwargs.get('encoding') is None:
            kwargs['encoding'] = 'cp1252'
        return abrir(archivo, modo, *args, **kwargs)

    monkeypatch.setattr(builtins, 'open', abrir_como_windows)
    import pykwalify.core  # pyRadiomics valida params.yaml con pykwalify, que importa su propio open()
    monkeypatch.setattr(pykwalify.core, 'open', abrir_como_windows)
    extractor = comun.crear_extractor(comun.CONFIG / 'params.yaml')
    assert extractor.settings['binWidth'] == 25
