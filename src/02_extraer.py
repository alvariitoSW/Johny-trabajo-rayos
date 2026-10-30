"""Paso 2 · Extracción de características radiómicas con pyRadiomics.

Entrada:  <entrada>/casos/<ID>/imagen.nii.gz, mascara.nii.gz y tecnicas.json (las variables técnicas que el
          paso 1 leyó de la cabecera DICOM: fabricante, modelo, kVp, kernel, grosor de corte, pixel spacing, mA…)
Salida:   <salida>/features.csv           una fila por caso: ID codificado, variables técnicas, binWidth,
                                          hash de params.yaml, versión de pyRadiomics y las características
          <salida>/extraccion_meta.json   versiones de todo el software, hash y ajustes efectivos

Uso:  python src/02_extraer.py --entrada data --salida outputs [--params config/params.yaml] [--binwidth 10]
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--entrada', type=Path, default=Path('data'))
    p.add_argument('--salida', type=Path, default=Path('outputs'))
    p.add_argument('--params', type=Path, default=comun.CONFIG / 'params.yaml')
    p.add_argument('--binwidth', type=float, default=None, help='anchura de intervalo en UH (sustituye a params.yaml)')
    a = p.parse_args(argv)

    extractor = comun.crear_extractor(a.params, a.binwidth)
    binwidth = extractor.settings['binWidth']
    huella = comun.sha256(a.params)
    version = comun.versiones()['pyradiomics']

    filas, errores = [], []
    for caso in comun.casos(a.entrada / 'casos'):
        fila = {'id': caso.name}
        tecnicas = comun.leer_json(caso / 'tecnicas.json')
        if not tecnicas:
            print(f'  {caso.name}: sin tecnicas.json (variables técnicas en blanco)')
        for nombre in comun.VARIABLES_TECNICAS:
            fila[nombre] = tecnicas.get(nombre)
        fila.update({'binwidth': binwidth, 'params_sha256': huella, 'pyradiomics_version': version, 'error': ''})
        try:
            fila.update(comun.extraer(extractor, caso / 'imagen.nii.gz', caso / 'mascara.nii.gz'))
            print(f'  {caso.name}: {sum(k.startswith("original_") for k in fila)} características')
        except Exception as e:  # un caso malo no para los demás; queda anotado en su fila
            fila['error'] = str(e)
            errores.append(caso.name)
            print(f'  {caso.name}: ERROR · {e}')
        filas.append(fila)

    a.salida.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(filas).to_csv(a.salida / 'features.csv', index=False, encoding='utf-8')
    comun.escribir_json(a.salida / 'extraccion_meta.json', {
        'fecha_ejecucion': datetime.now().isoformat(timespec='seconds'),
        'params': a.params.name,
        'params_sha256': huella,
        'binWidth': binwidth,
        'ajustes_efectivos': {k: v for k, v in extractor.settings.items()},
        'clases': {k: v for k, v in extractor.enabledFeatures.items()},
        'versiones': comun.versiones(),
        'casos': len(filas),
        'casos_con_error': errores,
    })
    print(f'Paso 2: {len(filas) - len(errores)} de {len(filas)} casos extraídos (binWidth {binwidth} UH) '
          f'→ {a.salida / "features.csv"}')
    return 1 if errores else 0


if __name__ == '__main__':
    sys.exit(main())
