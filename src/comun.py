"""Piezas compartidas por los pasos del pipeline.

Todas las rutas son relativas a lo que se pasa por la línea de órdenes (nunca rutas absolutas escritas
en el código). Funciona en Windows y en Linux.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import SimpleITK as sitk
import yaml

RAIZ = Path(__file__).resolve().parents[1]
CONFIG = RAIZ / 'config'

# Código de estudio de cada caso: letras, guion opcional y números (RMH-001, CRLM-0042, SINT-001).
# Si una carpeta no cumple el patrón, el pipeline para: así no se cuela un NHC ni un nombre.
PATRON_ID = re.compile(r'^[A-Za-z]{2,6}-?\d{2,5}$')

# Tolerancias para decir que dos imágenes comparten rejilla.
TOL_MM = 1e-3
TOL_DIRECCION = 1e-4

# Variables técnicas que se leen de la cabecera DICOM (protocolo §10, «TC»). Nada que identifique.
VARIABLES_TECNICAS = {
    'fabricante': 'Manufacturer',
    'modelo': 'ManufacturerModelName',
    'kvp': 'KVP',
    'kernel': 'ConvolutionKernel',
    'grosor_corte_mm': 'SliceThickness',
    'pixel_spacing_mm': 'PixelSpacing',
    'ma': 'XRayTubeCurrent',
    'mas': 'Exposure',
    'contraste_agente': 'ContrastBolusAgent',
}

# Atributos DICOM que identifican (o pueden identificar) al paciente, al centro o la fecha.
# Se comprueban en el informe de anonimización (solo si están presentes, nunca su valor).
IDENTIFICADORES_DICOM = [
    'PatientName', 'PatientID', 'OtherPatientIDs', 'OtherPatientNames', 'PatientBirthDate',
    'PatientBirthTime', 'PatientAddress', 'PatientTelephoneNumbers', 'PatientMotherBirthName',
    'MilitaryRank', 'EthnicGroup', 'PatientComments', 'MedicalRecordLocator',
    'AccessionNumber', 'StudyID', 'StudyDate', 'SeriesDate', 'AcquisitionDate', 'ContentDate',
    'StudyTime', 'SeriesTime', 'AcquisitionTime', 'ContentTime', 'AcquisitionDateTime',
    'InstitutionName', 'InstitutionAddress', 'InstitutionalDepartmentName', 'StationName',
    'ReferringPhysicianName', 'PerformingPhysicianName', 'OperatorsName', 'NameOfPhysiciansReadingStudy',
    'RequestingPhysician', 'DeviceSerialNumber', 'StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID',
    'FrameOfReferenceUID', 'RequestAttributesSequence',
]


def cargar_yaml(ruta: Path) -> dict:
    with open(ruta, encoding='utf-8') as f:
        return yaml.safe_load(f)


def sha256(ruta: Path) -> str:
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def comprobar_id(id_caso: str) -> None:
    if not PATRON_ID.match(id_caso):
        raise ValueError(f'«{id_caso}» no parece un código de estudio (p. ej. RMH-001). '
                         'Renombra la carpeta con el código, nunca con datos del paciente.')


def casos(carpeta: Path) -> list[Path]:
    """Subcarpetas de casos, en orden, comprobando que su nombre es un código de estudio."""
    if not carpeta.is_dir():
        raise FileNotFoundError(f'No existe la carpeta de casos: {carpeta}')
    salida = sorted(p for p in carpeta.iterdir() if p.is_dir() and not p.name.startswith('.'))
    for p in salida:
        comprobar_id(p.name)
    return salida


def misma_geometria(a: sitk.Image, b: sitk.Image) -> tuple[bool, str]:
    """¿Misma rejilla (tamaño, espaciado, origen y dirección)? Devuelve (sí/no, motivo)."""
    if a.GetSize() != b.GetSize():
        return False, f'tamaño {a.GetSize()} ≠ {b.GetSize()}'
    if not np.allclose(a.GetSpacing(), b.GetSpacing(), atol=TOL_MM):
        return False, f'espaciado {a.GetSpacing()} ≠ {b.GetSpacing()}'
    if not np.allclose(a.GetOrigin(), b.GetOrigin(), atol=TOL_MM):
        return False, f'origen {a.GetOrigin()} ≠ {b.GetOrigin()}'
    if not np.allclose(a.GetDirection(), b.GetDirection(), atol=TOL_DIRECCION):
        return False, 'dirección distinta'
    return True, 'misma geometría'


def limpiar_metadatos(img: sitk.Image) -> sitk.Image:
    """Quita todo metadato que SimpleITK arrastre (p. ej. etiquetas DICOM) antes de escribir NIfTI."""
    for clave in img.GetMetaDataKeys():
        img.EraseMetaData(clave)
    return img


def escribir_json(ruta: Path, datos: dict) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding='utf-8')


def leer_json(ruta: Path) -> dict:
    return json.loads(Path(ruta).read_text(encoding='utf-8')) if Path(ruta).exists() else {}


def crear_extractor(params: Path, binwidth: float | None = None):
    """Extractor de pyRadiomics con params.yaml; binwidth (si se da) sustituye al del archivo."""
    import logging
    import radiomics
    from radiomics import featureextractor
    radiomics.setVerbosity(logging.WARNING)
    # Se lee aquí en UTF-8 y se pasa ya leído: si pyRadiomics abre el archivo, en Windows usa la codificación del
    # sistema (cp1252) y los acentos de los comentarios lo rompen (visto en la prueba de Windows del 30/10/2026).
    extractor = featureextractor.RadiomicsFeatureExtractor(cargar_yaml(Path(params)))
    if binwidth is not None:
        extractor.settings['binWidth'] = float(binwidth)
    return extractor


def extraer(extractor, imagen: Path, mascara: Path) -> dict:
    """Características «original_*» de un caso (sin las columnas de diagnóstico de pyRadiomics)."""
    resultado = extractor.execute(str(imagen), str(mascara), label=1)
    return {k: float(v) for k, v in resultado.items() if k.startswith('original_')}


def versiones() -> dict:
    import platform
    import pandas
    import pydicom
    import radiomics
    return {'python': platform.python_version(), 'pyradiomics': radiomics.__version__,
            'numpy': np.__version__, 'SimpleITK': sitk.Version.VersionString(),
            'pydicom': pydicom.__version__, 'pandas': pandas.__version__}


def mascara_binaria(mascara: sitk.Image) -> sitk.Image:
    """Cualquier valor > 0 pasa a 1; tipo uint8."""
    return sitk.Cast(mascara > 0, sitk.sitkUInt8)


def fiabilidad_koo_li(inf, sup) -> str:
    """Etiqueta de fiabilidad según el IC 95 % del ICC (es una etiqueta, nunca un filtro).

    Fuente: Koo TK, Li MY. J Chiropr Med 2016;15(2):155-163: «Based on the 95% confident interval of the ICC
    estimate, values less than 0.5, between 0.5 and 0.75, between 0.75 and 0.9, and greater than 0.90 are
    indicative of poor, moderate, good, and excellent reliability».
    Se clasifica el IC entero: el límite inferior y el superior. Si caen en la misma categoría, esa; si no,
    «de <inferior> a <superior>». NaN en cualquiera de los dos → «no calculable».
    Fronteras usadas: <0,5 pobre; 0,5 a 0,75 (0,5 incluido) moderada; 0,75 a 0,9 (0,75 y 0,9 incluidos) buena;
    >0,9 excelente. Dónde cae cada frontera exacta es una decisión de implementación (la fuente no lo precisa).
    """
    if inf is None or sup is None or np.isnan(inf) or np.isnan(sup):
        return 'no calculable'

    def categoria(x: float) -> str:
        if x < 0.5:
            return 'pobre'
        if x < 0.75:
            return 'moderada'
        if x <= 0.9:
            return 'buena'
        return 'excelente'

    a, b = categoria(float(inf)), categoria(float(sup))
    return a if a == b else f'de {a} a {b}'


# ------------------------------------------------------------------------- decisiones sobre los casos
# Tipos de alerta del paso 3 (prefijo del texto → nombre en llano). Lo usan el paso 3 y el resumen para el móvil.
TIPOS_ALERTA = [('máscara vacía', 'máscara vacía'), ('valores de máscara', 'valores de máscara no válidos'),
                ('geometría', 'geometría distinta'), ('componentes', 'varios componentes'),
                ('diámetro axial <', 'lesión menor de 10 mm')]
DECISIONES = ('incluir', 'excluir', 'revisar')


def tipos_de_alerta(alertas: str) -> str:
    """Nombres en llano de los tipos de alerta de un caso («ninguna» → cadena vacía)."""
    return '; '.join(nombre for prefijo, nombre in TIPOS_ALERTA if prefijo in str(alertas))


def leer_decisiones(ruta: Path) -> dict[str, dict]:
    """<datos>/decisiones_casos.csv (columnas exactas id,decision,motivo). Sin archivo → {}. Una decisión que no
    sea incluir, excluir o revisar es un error: nunca se interpreta a escondidas."""
    if not Path(ruta).exists():
        return {}
    t = pd.read_csv(ruta, dtype=str).fillna('')
    if list(t.columns) != ['id', 'decision', 'motivo']:
        raise ValueError(f'{ruta}: las columnas deben ser exactamente id,decision,motivo (hay {list(t.columns)})')
    t['decision'] = t['decision'].str.strip().str.lower()
    malas = t.loc[~t['decision'].isin(DECISIONES), 'decision'].unique().tolist()
    if malas:
        raise ValueError(f'{ruta}: decisión no válida {malas}; usa incluir, excluir o revisar')
    return {f['id'].strip(): {'decision': f['decision'], 'motivo': f['motivo'].strip()} for _, f in t.iterrows()}


def ids_analizados(salida: Path, paso: str = ''):
    """Casos que se analizan en los pasos 4 y 5: decision == incluir en qc_report.csv (o, si ese archivo no lleva
    decisión, los que no tienen alerta). Sin qc_report.csv devuelve None (sin filtro). Avisa de los que se dejan fuera."""
    ruta = Path(salida) / 'qc_report.csv'
    if not ruta.exists():
        return None
    qc = pd.read_csv(ruta)
    ok = qc['decision'] == 'incluir' if 'decision' in qc else qc['alertas'] == 'ninguna'
    fuera = qc[~ok]
    if len(fuera):
        pend = int((fuera['decision'] == 'revisar').sum()) if 'decision' in fuera else 0
        print(f'AVISO{" (" + paso + ")" if paso else ""}: {len(fuera)} caso(s) no se analizan: '
              f'{len(fuera) - pend} excluido(s) y {pend} pendiente(s) de revisar por el radiólogo '
              f'(ver qc_report.csv, columna «decision»).')
    return set(qc.loc[ok, 'id'])
