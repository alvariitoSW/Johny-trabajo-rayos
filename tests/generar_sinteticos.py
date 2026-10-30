"""Generador de DATOS SINTÉTICOS para probar el pipeline. Ninguna imagen sale de un paciente.

Cada caso es una TC DICOM de un «hígado» (elipsoide de UH conocidas, con ruido gaussiano) con una lesión
(esfera o elipsoide) de atenuación, ruido y tamaño conocidos, y su segmentación:
  · como la exporta 3D Slicer (.seg.nrrd recortado a la lesión, con Segment0_Name/LabelValue), o
  · como DICOM-SEG (caso SINT-003, con un segundo segmento «Liver» que el pipeline debe ignorar).
Seis casos (los 7 primeros salvo el DICOM-SEG) llevan dos observadores: el 2.º dibuja la lesión algo más
grande y desplazada.
Casos trampa para el control de calidad: SINT-005 (lesión de 8 mm, < 10 mm) y SINT-008 (dos componentes).
Las cabeceras DICOM llevan identificadores FALSOS (nombre, ID, fechas, centro) para comprobar que no
llegan a los NIfTI ni a los CSV.

Uso:  python tests/generar_sinteticos.py --salida data_sintetica --casos 10 [--semilla 42]
Crea  <salida>/crudo/SINT-001…/, <salida>/verdad.json y <salida>/DATOS_SINTETICOS.txt
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pydicom
import SimpleITK as sitk
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.pixels import pack_bits
from pydicom.uid import CTImageStorage, ExplicitVRLittleEndian, generate_uid

SEG_SOP_CLASS = '1.2.840.10008.5.1.4.1.1.66.4'
FILAS = COLUMNAS = 128
PIXEL_MM = 0.78
HIGADO_UH, HIGADO_RUIDO, FONDO_UH = 110.0, 12.0, -100.0

# Identificadores FALSOS: el pipeline no debe dejar que lleguen a ninguna salida.
FALSOS = {'PatientName': 'SINTETICO^PRUEBA', 'PatientID': 'PRUEBA-0001', 'PatientBirthDate': '19500101',
          'StudyDate': '20200101', 'InstitutionName': 'HOSPITAL FICTICIO', 'AccessionNumber': 'ACC123456'}

EQUIPOS = [  # (fabricante, modelo, kVp, kernel, grosor de corte en mm, mA)
    ('SintetiCT', 'Modelo A', 120, 'B30f', 2.5, 250),
    ('SintetiCT', 'Modelo A', 100, 'B30f', 2.5, 300),
    ('OtraMarca', 'Modelo B', 120, 'STANDARD', 1.25, 280),
]


def plan_de_casos(n: int, rng: np.random.Generator) -> list[dict]:
    casos = []
    for i in range(n):
        radios = [9.0, 11.0, 13.0, 15.0, 4.0, 10.0, 12.0, 14.0, 16.0, 8.0][i % 10]
        forma = 'esfera' if i % 2 == 0 else 'elipsoide'
        semiejes = [radios] * 3 if forma == 'esfera' else [radios * 1.3, radios, radios * 0.8]
        casos.append({
            'id': f'SINT-{i + 1:03d}',
            'equipo': EQUIPOS[i % len(EQUIPOS)],
            'lesion_uh': float(rng.uniform(45, 75)),
            'lesion_ruido': float(rng.uniform(8, 20)),
            'semiejes_mm': semiejes,
            'forma': forma,
            'dos_observadores': i < 7,
            'formato_mascara': 'dicom-seg' if i == 2 else 'seg.nrrd',
            'segundo_componente': i == 7,
        })
    return casos


def elipsoide(zz, yy, xx, centro, semiejes):
    return (((xx - centro[0]) / semiejes[0]) ** 2 + ((yy - centro[1]) / semiejes[1]) ** 2
            + ((zz - centro[2]) / semiejes[2]) ** 2) <= 1.0


def volumen(caso: dict, rng: np.random.Generator):
    grosor = caso['equipo'][4]
    n_cortes = int(round(100 / grosor))
    z = np.arange(n_cortes) * grosor
    y = np.arange(FILAS) * PIXEL_MM
    x = np.arange(COLUMNAS) * PIXEL_MM
    zz, yy, xx = np.meshgrid(z, y, x, indexing='ij')
    centro_higado = [50.0, 50.0, 50.0]
    higado = elipsoide(zz, yy, xx, centro_higado, [42, 38, 40])
    centro = [50.0 + rng.uniform(-4, 4), 50.0 + rng.uniform(-4, 4), 50.0 + rng.uniform(-4, 4)]
    lesion = elipsoide(zz, yy, xx, centro, caso['semiejes_mm'])

    uh = np.full(zz.shape, FONDO_UH) + rng.normal(0, 6, zz.shape)
    uh[higado] = HIGADO_UH + rng.normal(0, HIGADO_RUIDO, int(higado.sum()))
    uh[lesion] = caso['lesion_uh'] + rng.normal(0, caso['lesion_ruido'], int(lesion.sum()))

    obs1 = lesion.copy()
    if caso['segundo_componente']:  # un nódulo aparte dentro del hígado, mal incluido en la máscara
        otro = elipsoide(zz, yy, xx, [30.0, 30.0, 70.0], [3.5, 3.5, 3.5])
        uh[otro] = caso['lesion_uh']
        obs1 |= otro
    obs2 = elipsoide(zz, yy, xx, [c + 0.8 for c in centro], [s * 1.06 for s in caso['semiejes_mm']])
    return np.round(uh).astype(np.int16), obs1, obs2, n_cortes, grosor, centro


def escribir_dicom(carpeta: Path, uh: np.ndarray, caso: dict, grosor: float) -> tuple[str, str]:
    carpeta.mkdir(parents=True, exist_ok=True)
    estudio, serie, marco = generate_uid(), generate_uid(), generate_uid()
    fabricante, modelo, kvp, kernel, _, ma = caso['equipo']
    for k in range(uh.shape[0]):
        meta = FileMetaDataset()
        meta.MediaStorageSOPClassUID = CTImageStorage
        meta.MediaStorageSOPInstanceUID = generate_uid()
        meta.TransferSyntaxUID = ExplicitVRLittleEndian
        ds = Dataset()
        ds.file_meta = meta
        ds.SOPClassUID, ds.SOPInstanceUID = CTImageStorage, meta.MediaStorageSOPInstanceUID
        ds.StudyInstanceUID, ds.SeriesInstanceUID, ds.FrameOfReferenceUID = estudio, serie, marco
        for clave, valor in FALSOS.items():
            setattr(ds, clave, valor)
        ds.Modality, ds.SeriesDescription = 'CT', 'PORTAL SINTETICA'
        ds.Manufacturer, ds.ManufacturerModelName, ds.KVP, ds.ConvolutionKernel = fabricante, modelo, kvp, kernel
        ds.SliceThickness, ds.XRayTubeCurrent, ds.ContrastBolusAgent = grosor, ma, 'IODADO'
        ds.PixelSpacing = [PIXEL_MM, PIXEL_MM]
        ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
        ds.ImagePositionPatient = [0.0, 0.0, k * grosor]
        ds.InstanceNumber = k + 1
        ds.Rows, ds.Columns = uh.shape[1], uh.shape[2]
        ds.SamplesPerPixel, ds.PhotometricInterpretation = 1, 'MONOCHROME2'
        ds.BitsAllocated, ds.BitsStored, ds.HighBit, ds.PixelRepresentation = 16, 16, 15, 1
        ds.RescaleIntercept, ds.RescaleSlope, ds.RescaleType = 0, 1, 'HU'
        ds.PixelData = uh[k].astype('<i2').tobytes()
        ds.save_as(carpeta / f'corte_{k:04d}.dcm', enforce_file_format=True)
    return estudio, marco


def imagen_de(arr: np.ndarray, grosor: float) -> sitk.Image:
    img = sitk.GetImageFromArray(arr.astype(np.uint8))
    img.SetSpacing((PIXEL_MM, PIXEL_MM, grosor))
    img.SetOrigin((0.0, 0.0, 0.0))
    return img


def escribir_seg_nrrd(ruta: Path, mascara: np.ndarray, grosor: float) -> None:
    """Como Slicer: recortada a la extensión de la lesión (con margen) y con los campos Segment0_*."""
    img = imagen_de(mascara, grosor)
    z, y, x = np.nonzero(mascara)
    inicio = [max(0, int(v.min()) - 2) for v in (x, y, z)]
    fin = [min(t, int(v.max()) + 3) for v, t in zip((x, y, z), img.GetSize())]
    recorte = img[inicio[0]:fin[0], inicio[1]:fin[1], inicio[2]:fin[2]]
    recorte.SetMetaData('Segment0_Name', 'Lesion')
    recorte.SetMetaData('Segment0_LabelValue', '1')
    recorte.SetMetaData('Segment0_Layer', '0')
    sitk.WriteImage(recorte, str(ruta), useCompression=True)


def escribir_dicom_seg(ruta: Path, segmentos: list[tuple[str, np.ndarray]], grosor: float, estudio: str, marco: str):
    """DICOM-SEG binario mínimo: un frame por corte con contenido y por segmento."""
    meta = FileMetaDataset()
    meta.MediaStorageSOPClassUID, meta.MediaStorageSOPInstanceUID = SEG_SOP_CLASS, generate_uid()
    meta.TransferSyntaxUID = ExplicitVRLittleEndian
    ds = Dataset()
    ds.file_meta = meta
    ds.SOPClassUID, ds.SOPInstanceUID = SEG_SOP_CLASS, meta.MediaStorageSOPInstanceUID
    ds.StudyInstanceUID, ds.SeriesInstanceUID, ds.FrameOfReferenceUID = estudio, generate_uid(), marco
    for clave, valor in FALSOS.items():
        setattr(ds, clave, valor)
    ds.Modality, ds.SegmentationType = 'SEG', 'BINARY'
    ds.Rows, ds.Columns = FILAS, COLUMNAS
    ds.SamplesPerPixel, ds.PhotometricInterpretation = 1, 'MONOCHROME2'
    ds.BitsAllocated, ds.BitsStored, ds.HighBit, ds.PixelRepresentation = 1, 1, 0, 0
    ds.SegmentSequence = []
    frames, grupos = [], []
    for numero, (etiqueta, arr) in enumerate(segmentos, 1):
        s = Dataset()
        s.SegmentNumber, s.SegmentLabel, s.SegmentAlgorithmType = numero, etiqueta, 'MANUAL'
        ds.SegmentSequence.append(s)
        for k in np.unique(np.nonzero(arr)[0]):
            frames.append(arr[k].astype(np.uint8))
            g = Dataset()
            ident, plano = Dataset(), Dataset()
            ident.ReferencedSegmentNumber = numero
            plano.ImagePositionPatient = [0.0, 0.0, float(k) * grosor]
            g.SegmentIdentificationSequence, g.PlanePositionSequence = [ident], [plano]
            grupos.append(g)
    ds.PerFrameFunctionalGroupsSequence = grupos
    ds.NumberOfFrames = len(frames)
    ds.PixelData = pack_bits(np.stack(frames))
    ds.save_as(ruta, enforce_file_format=True)


def generar(salida: Path, n: int, semilla: int) -> dict:
    rng = np.random.default_rng(semilla)
    verdad = {}
    (salida / 'crudo').mkdir(parents=True, exist_ok=True)
    (salida / 'DATOS_SINTETICOS.txt').write_text(
        'DATOS SIMULADOS por tests/generar_sinteticos.py. Ninguna imagen procede de un paciente.\n', encoding='utf-8')
    for caso in plan_de_casos(n, rng):
        uh, obs1, obs2, n_cortes, grosor, centro = volumen(caso, rng)
        carpeta = salida / 'crudo' / caso['id']
        estudio, marco = escribir_dicom(carpeta / 'imagen', uh, caso, grosor)
        if caso['formato_mascara'] == 'dicom-seg':
            higado = uh > 90
            escribir_dicom_seg(carpeta / 'mascara.dcm', [('Tumor_1', obs1), ('Liver', higado)], grosor, estudio, marco)
        elif caso['dos_observadores']:
            escribir_seg_nrrd(carpeta / 'mascara_obs1.seg.nrrd', obs1, grosor)
            escribir_seg_nrrd(carpeta / 'mascara_obs2.seg.nrrd', obs2, grosor)
        else:
            escribir_seg_nrrd(carpeta / 'mascara.seg.nrrd', obs1, grosor)
        a, b, c = caso['semiejes_mm']
        verdad[caso['id']] = {**caso, 'centro_mm': centro, 'n_cortes': n_cortes,
                              'volumen_mm3': 4 / 3 * np.pi * a * b * c,
                              'diametro_axial_mm': 2 * max(a, b),
                              'dos_observadores': caso['dos_observadores'] and caso['formato_mascara'] != 'dicom-seg'}
    (salida / 'verdad.json').write_text(json.dumps(verdad, indent=2, ensure_ascii=False, default=float), encoding='utf-8')
    return verdad


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--salida', type=Path, required=True)
    p.add_argument('--casos', type=int, default=10)
    p.add_argument('--semilla', type=int, default=42)
    a = p.parse_args(argv)
    verdad = generar(a.salida, a.casos, a.semilla)
    print(f'{len(verdad)} casos sintéticos en {a.salida / "crudo"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
