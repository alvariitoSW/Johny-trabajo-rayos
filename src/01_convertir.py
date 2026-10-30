"""Paso 1 · Conversión a NIfTI, geometría y anonimización.

Entrada (una carpeta por caso, con el CÓDIGO de estudio como nombre, nunca datos del paciente):

    <entrada>/crudo/<ID>/imagen/                  serie DICOM de la TC en fase portal (solo esa serie)
    <entrada>/crudo/<ID>/mascara.<ext>            segmentación de un observador, o bien
    <entrada>/crudo/<ID>/mascara_obs1.<ext>       las de dos observadores (reproducibilidad)
    <entrada>/crudo/<ID>/mascara_obs2.<ext>
    <ext> = seg.nrrd o nrrd (exportada de 3D Slicer) o dcm (DICOM-SEG)

Salida:

    <entrada>/casos/<ID>/imagen.nii.gz            TC en UH, sin metadatos
    <entrada>/casos/<ID>/mascara.nii.gz           0/1 en la rejilla de la imagen (la del observador 1 si hay dos)
    <entrada>/casos/<ID>/mascara_obs1.nii.gz, mascara_obs2.nii.gz (si hay dos observadores)
    <entrada>/casos/<ID>/tecnicas.json            variables técnicas de la cabecera DICOM (nada identificable)
    <salida>/anonimizacion.csv                    informe: qué identificadores tenía el origen (solo el NOMBRE
                                                  del atributo, nunca su valor) y si la copia NIfTI está limpia

Uso:  python src/01_convertir.py --entrada data --salida outputs [--segmento 1 | --segmento Tumor_1 | --segmento mayor:Tumor]
"""
from __future__ import annotations

import argparse
import csv
import gzip
import struct
import sys
from pathlib import Path

import numpy as np
import pydicom
import SimpleITK as sitk

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

SEG_SOP_CLASS = '1.2.840.10008.5.1.4.1.1.66.4'
EXTENSIONES_SEG = ('.seg.nrrd', '.nrrd', '.dcm')


# --------------------------------------------------------------------------------------------- DICOM
def leer_serie(carpeta: Path) -> tuple[sitk.Image, list[str]]:
    lector = sitk.ImageSeriesReader()
    series = lector.GetGDCMSeriesIDs(str(carpeta))
    if not series:
        raise ValueError(f'no hay ninguna serie DICOM en {carpeta}')
    if len(series) > 1:
        raise ValueError(f'hay {len(series)} series DICOM en {carpeta}: deja solo la fase portal')
    archivos = lector.GetGDCMSeriesFileNames(str(carpeta), series[0])
    lector.SetFileNames(archivos)
    imagen = lector.Execute()  # GDCM aplica RescaleSlope/Intercept: la imagen sale en UH
    return imagen, list(archivos)


def valor_dicom(ds, atributo: str):
    v = ds.get(atributo)
    if v is None or v == '':
        return None
    if isinstance(v, pydicom.multival.MultiValue):
        return '×'.join(str(round(float(x), 4)) for x in v)
    if isinstance(v, (pydicom.valuerep.DSfloat, pydicom.valuerep.IS, float, int)):
        return float(v)
    return str(v)


def variables_tecnicas(ds, imagen: sitk.Image, n_cortes: int) -> dict:
    datos = {nombre: valor_dicom(ds, atributo) for nombre, atributo in comun.VARIABLES_TECNICAS.items()}
    datos['espaciado_reconstruido_mm'] = [round(s, 4) for s in imagen.GetSpacing()]
    datos['n_cortes'] = n_cortes
    return datos


def identificadores_presentes(ds) -> dict[str, str]:
    """Atributos identificadores presentes y no vacíos. El valor solo se usa en memoria para comprobar
    que no llega a la copia NIfTI; nunca se escribe."""
    presentes = {}
    for atributo in comun.IDENTIFICADORES_DICOM:
        v = ds.get(atributo)
        if v not in (None, '') and not isinstance(v, pydicom.sequence.Sequence):
            presentes[atributo] = str(v)
        elif isinstance(v, pydicom.sequence.Sequence) and len(v):
            presentes[atributo] = ''
    return presentes


# --------------------------------------------------------------------------------------- segmentación
def buscar_segmentaciones(carpeta: Path) -> dict[str, Path]:
    """{'mascara': ruta} o {'mascara_obs1': ruta, 'mascara_obs2': ruta}."""
    encontradas = {}
    for base in ('mascara', 'mascara_obs1', 'mascara_obs2'):
        for ext in EXTENSIONES_SEG:
            ruta = carpeta / f'{base}{ext}'
            if ruta.exists():
                encontradas[base] = ruta
                break
    if 'mascara' in encontradas and len(encontradas) > 1:
        raise ValueError('hay «mascara» y «mascara_obsN» a la vez: usa solo una de las dos formas')
    if ('mascara_obs1' in encontradas) != ('mascara_obs2' in encontradas):
        raise ValueError('falta la segmentación de uno de los dos observadores')
    if not encontradas:
        raise ValueError(f'no hay segmentación (mascara.seg.nrrd, .nrrd o .dcm) en {carpeta}')
    return encontradas


def elegir_segmento(segmentos: dict, criterio: str, volumen) -> object:
    """segmentos: {clave: nombre}. criterio: número, nombre o «mayor:<texto>». volumen(clave) → nº de vóxeles."""
    if criterio.startswith('mayor:'):
        texto = criterio.split(':', 1)[1].lower()
        candidatos = [k for k, n in segmentos.items() if texto in str(n).lower()]
        if not candidatos:
            raise ValueError(f'ningún segmento contiene «{texto}»; hay: {sorted(map(str, segmentos.values()))}')
        return max(candidatos, key=volumen)
    for k, n in segmentos.items():
        if criterio == str(n):
            return k
    for k in segmentos:
        if criterio == str(k):
            return k
    if len(segmentos) == 1 and criterio == '1':
        return next(iter(segmentos))
    raise ValueError(f'no encuentro el segmento «{criterio}»; hay: {sorted(map(str, segmentos.values()))}')


def leer_nrrd(ruta: Path, criterio: str) -> sitk.Image:
    seg = sitk.ReadImage(str(ruta))
    if seg.GetDimension() != 3 or seg.GetNumberOfComponentsPerPixel() != 1:
        raise ValueError(f'{ruta.name}: segmentación con varias capas; en Slicer, expórtala como labelmap')
    arr = sitk.GetArrayViewFromImage(seg)
    # Segmentación de Slicer: el encabezado trae Segment<i>_Name y Segment<i>_LabelValue.
    segmentos = {}
    claves = seg.GetMetaDataKeys()
    i = 0
    while f'Segment{i}_Name' in claves:
        etiqueta = int(seg.GetMetaData(f'Segment{i}_LabelValue')) if f'Segment{i}_LabelValue' in claves else i + 1
        segmentos[etiqueta] = seg.GetMetaData(f'Segment{i}_Name')
        i += 1
    if not segmentos:  # labelmap simple: cada valor > 0 es un segmento
        segmentos = {int(v): int(v) for v in np.unique(arr) if v > 0}
    if not segmentos:
        raise ValueError(f'{ruta.name}: la segmentación está vacía')
    etiqueta = elegir_segmento(segmentos, criterio, lambda k: int((arr == k).sum()))
    mascara = sitk.Cast(seg == etiqueta, sitk.sitkUInt8)
    return comun.limpiar_metadatos(mascara)


def leer_dicom_seg(ruta: Path, imagen: sitk.Image, criterio: str) -> sitk.Image:
    ds = pydicom.dcmread(str(ruta))
    if ds.SOPClassUID != SEG_SOP_CLASS:
        raise ValueError(f'{ruta.name} no es un DICOM-SEG')
    tam = imagen.GetSize()
    if (int(ds.Rows), int(ds.Columns)) != (tam[1], tam[0]):
        raise ValueError(f'{ruta.name}: los cortes del SEG ({ds.Rows}×{ds.Columns}) no son los de la imagen')
    frames = ds.pixel_array
    if frames.ndim == 2:
        frames = frames[np.newaxis]
    if getattr(ds, 'SegmentationType', 'BINARY') == 'FRACTIONAL':
        frames = frames >= 0.5 * float(ds.MaximumFractionalValue)
    segmentos = {int(s.SegmentNumber): str(s.SegmentLabel) for s in ds.SegmentSequence}
    por_frame = []
    for grupo in ds.PerFrameFunctionalGroupsSequence:
        numero = int(grupo.SegmentIdentificationSequence[0].ReferencedSegmentNumber)
        posicion = [float(x) for x in grupo.PlanePositionSequence[0].ImagePositionPatient]
        indice = imagen.TransformPhysicalPointToContinuousIndex(posicion)
        if abs(indice[0]) > 0.01 or abs(indice[1]) > 0.01 or abs(indice[2] - round(indice[2])) > 0.01:
            raise ValueError(f'{ruta.name}: un frame no cae en un corte de la imagen (índice {indice})')
        por_frame.append((numero, int(round(indice[2]))))

    def volumen(numero):
        return int(sum(frames[i].sum() for i, (n, _) in enumerate(por_frame) if n == numero))

    numero = elegir_segmento(segmentos, criterio, volumen)
    arr = np.zeros(tam[::-1], dtype=np.uint8)
    for i, (n, z) in enumerate(por_frame):
        if n == numero:
            if not 0 <= z < tam[2]:
                raise ValueError(f'{ruta.name}: un frame cae fuera de la imagen (corte {z})')
            arr[z] |= (frames[i] > 0).astype(np.uint8)
    mascara = sitk.GetImageFromArray(arr)
    mascara.CopyInformation(imagen)
    return mascara


def a_rejilla_de_imagen(mascara: sitk.Image, imagen: sitk.Image) -> tuple[sitk.Image, str]:
    """Pone la máscara en la rejilla de la imagen SIN interpolar. Slicer suele guardar la segmentación
    recortada a su extensión: si el espaciado y la dirección coinciden y el origen cae en un vóxel de la
    imagen, basta con recolocarla (vecino más próximo exacto). Si no, para: no se interpolan máscaras."""
    igual, motivo = comun.misma_geometria(mascara, imagen)
    if igual:
        return mascara, 'misma geometría'
    if not np.allclose(mascara.GetSpacing(), imagen.GetSpacing(), atol=comun.TOL_MM):
        raise ValueError(f'la máscara no tiene el espaciado de la imagen ({motivo})')
    if not np.allclose(mascara.GetDirection(), imagen.GetDirection(), atol=comun.TOL_DIRECCION):
        raise ValueError('la máscara no tiene la orientación de la imagen')
    indice = np.array(imagen.TransformPhysicalPointToContinuousIndex(mascara.GetOrigin()))
    if np.abs(indice - np.round(indice)).max() > 0.01:
        raise ValueError('el origen de la máscara no cae en un vóxel de la imagen')
    recolocada = sitk.Resample(mascara, imagen, sitk.Transform(), sitk.sitkNearestNeighbor, 0, sitk.sitkUInt8)
    if int(sitk.GetArrayViewFromImage(recolocada).sum()) != int(sitk.GetArrayViewFromImage(mascara).sum()):
        raise ValueError('parte de la máscara queda fuera de la imagen')
    return recolocada, 'recolocada en la rejilla de la imagen (sin interpolar)'


# ------------------------------------------------------------------------------------- anonimización
def cabecera_nifti(ruta: Path) -> bytes:
    """Bytes de la cabecera y extensiones de un .nii.gz (todo lo que va antes de los vóxeles)."""
    with gzip.open(ruta, 'rb') as f:
        cabecera = f.read(352)
        vox_offset = int(struct.unpack('<f', cabecera[108:112])[0])
        return cabecera + f.read(max(0, vox_offset - 352))


def nifti_limpio(ruta: Path, valores: list[str]) -> bool:
    texto = cabecera_nifti(ruta)
    return not any(v.encode('utf-8', 'ignore') in texto for v in valores if len(v.strip()) >= 3)


def escribir(img: sitk.Image, ruta: Path) -> None:
    sitk.WriteImage(comun.limpiar_metadatos(img), str(ruta), useCompression=True)


# ------------------------------------------------------------------------------------------- un caso
def convertir_caso(origen: Path, destino: Path, criterio: str) -> dict:
    id_caso = origen.name
    imagen, archivos = leer_serie(origen / 'imagen')
    ds = pydicom.dcmread(archivos[0], stop_before_pixels=True)
    presentes = identificadores_presentes(ds)
    if presentes.get('PatientID', '').strip() == id_caso or presentes.get('PatientName', '').strip() == id_caso:
        raise ValueError(f'{id_caso}: el código de estudio coincide con un dato del paciente en el DICOM')

    destino.mkdir(parents=True, exist_ok=True)
    escribir(imagen, destino / 'imagen.nii.gz')
    notas = []
    for base, ruta in buscar_segmentaciones(origen).items():
        if ruta.name.endswith('.dcm'):
            mascara = leer_dicom_seg(ruta, imagen, criterio)
        else:
            mascara = leer_nrrd(ruta, criterio)
        mascara, nota = a_rejilla_de_imagen(mascara, imagen)
        igual, motivo = comun.misma_geometria(mascara, imagen)
        if not igual:
            raise ValueError(f'{id_caso}/{base}: geometría distinta de la imagen ({motivo})')
        if int(sitk.GetArrayViewFromImage(mascara).sum()) == 0:
            notas.append(f'{base}: máscara vacía')
        escribir(mascara, destino / f'{base}.nii.gz')
        notas.append(f'{base}: {nota}')
    if (destino / 'mascara_obs1.nii.gz').exists():  # la del observador 1 es la máscara principal
        escribir(sitk.ReadImage(str(destino / 'mascara_obs1.nii.gz')), destino / 'mascara.nii.gz')

    comun.escribir_json(destino / 'tecnicas.json', variables_tecnicas(ds, imagen, len(archivos)))

    valores = [v for v in presentes.values() if v]
    limpios = all(nifti_limpio(p, valores) for p in destino.glob('*.nii.gz'))
    tecnicas_txt = (destino / 'tecnicas.json').read_text(encoding='utf-8')
    tecnicas_limpias = not any(v in tecnicas_txt for v in valores if len(v.strip()) >= 3)
    return {
        'id': id_caso,
        'identificadores_en_origen': ';'.join(sorted(presentes)) or 'ninguno',
        'nifti_sin_identificadores': limpios,
        'tecnicas_sin_identificadores': tecnicas_limpias,
        'resultado': 'OK' if limpios and tecnicas_limpias else 'REVISAR',
        'notas': ' | '.join(notas),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--entrada', type=Path, default=Path('data'))
    p.add_argument('--salida', type=Path, default=Path('outputs'))
    p.add_argument('--segmento', default='1',
                   help='segmento a usar: número, nombre o «mayor:<texto>» (el de mayor volumen cuyo nombre lo contenga)')
    a = p.parse_args(argv)

    filas, errores = [], []
    for origen in comun.casos(a.entrada / 'crudo'):
        try:
            filas.append(convertir_caso(origen, a.entrada / 'casos' / origen.name, a.segmento))
            print(f'  {origen.name}: {filas[-1]["resultado"]}')
        except Exception as e:  # un caso malo no para los demás; queda en el informe
            errores.append(origen.name)
            filas.append({'id': origen.name, 'identificadores_en_origen': '', 'nifti_sin_identificadores': '',
                          'tecnicas_sin_identificadores': '', 'resultado': 'ERROR', 'notas': str(e)})
            print(f'  {origen.name}: ERROR · {e}')

    a.salida.mkdir(parents=True, exist_ok=True)
    with open(a.salida / 'anonimizacion.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    print(f'Paso 1: {len(filas) - len(errores)} de {len(filas)} casos convertidos → {a.salida / "anonimizacion.csv"}')
    revisar = [f['id'] for f in filas if f['resultado'] != 'OK']
    if revisar:
        print(f'  ATENCIÓN, revisar: {", ".join(revisar)}')
    return 1 if revisar else 0


if __name__ == '__main__':
    sys.exit(main())
