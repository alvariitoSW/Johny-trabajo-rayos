"""Ejecuta el pipeline de radiómica en orden: conversión → extracción → control de calidad →
reproducibilidad → descriptivo → informe PDF → resumen para el móvil (solo agregados).

Uso (desde la carpeta del proyecto, con el entorno activado):

    python run_pipeline.py --input data --output outputs
    python run_pipeline.py --input data --output outputs --binwidth 10
    python run_pipeline.py --input data --output outputs --desde 2      (si los NIfTI ya están en data/casos)

--input   carpeta de datos: <input>/crudo/<ID>/ (DICOM y segmentaciones) y <input>/casos/<ID>/ (NIfTI, la crea el paso 1)
--output  carpeta de resultados (CSV, figuras e informe.pdf)
Si <input>/crudo no existe, el paso 1 se salta y se usa <input>/casos tal cual.
Si el paso 1 no puede garantizar la anonimización de algún caso, el pipeline PARA.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / 'src'
PASOS = ['01_convertir', '02_extraer', '03_qc', '04_reproducibilidad', '05_descriptivo', '06_informe', '07_resumen_movil']


def cargar(nombre: str):
    spec = importlib.util.spec_from_file_location(f'paso_{nombre}', SRC / f'{nombre}.py')
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--input', type=Path, default=Path('data'))
    p.add_argument('--output', type=Path, default=Path('outputs'))
    p.add_argument('--binwidth', type=float, default=None, help='anchura de intervalo en UH (por defecto, la de params.yaml: 25)')
    p.add_argument('--params', type=Path, default=SRC.parent / 'config' / 'params.yaml')
    p.add_argument('--segmento', default='1', help='segmento a usar en el paso 1 (número, nombre o «mayor:<texto>»)')
    p.add_argument('--desde', type=int, default=1, choices=range(1, 8), help='primer paso que se ejecuta (1-7)')
    a = p.parse_args(argv)

    entrada, salida = ['--entrada', str(a.input)], ['--salida', str(a.output)]
    bw = ['--binwidth', str(a.binwidth)] if a.binwidth is not None else []
    argumentos = {
        '01_convertir': entrada + salida + ['--segmento', a.segmento],
        '02_extraer': entrada + salida + ['--params', str(a.params)] + bw,
        '03_qc': entrada + salida,
        '04_reproducibilidad': entrada + salida + ['--params', str(a.params)] + bw,
        '05_descriptivo': salida,
        '06_informe': entrada + salida,
        '07_resumen_movil': entrada + salida,
    }
    fallos = []
    for numero, nombre in enumerate(PASOS, 1):
        if numero < a.desde:
            continue
        if nombre == '01_convertir' and not (a.input / 'crudo').is_dir():
            print(f'== Paso 1 omitido: no existe {a.input / "crudo"}; se usa {a.input / "casos"}')
            continue
        print(f'== Paso {numero}: {nombre}')
        codigo = cargar(nombre).main(argumentos[nombre])
        if codigo:
            fallos.append(nombre)
            if nombre == '01_convertir':
                print('PARADO: revisa outputs/anonimizacion.csv antes de seguir (algún caso no está limpio o falló).')
                return 1
    print('Pipeline terminado' + (f' con avisos en: {", ".join(fallos)}' if fallos else ' sin errores')
          + f'. Informe: {a.output / "informe.pdf"}')
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
