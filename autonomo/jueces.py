#!/usr/bin/env python3
"""Jueces del estudio: lo que nunca puede llegar a GitHub y las pruebas de los cálculos.

Uso:  python3 autonomo/jueces.py            (desde la raíz del repositorio)
      python3 autonomo/jueces.py --raiz RUTA (otro repositorio; lo usa la prueba trampa)

Comprueba los archivos que git subiría (seguidos y nuevos no ignorados):
  1. Ningún archivo de imagen médica o máscara (DICOM, NIfTI, NRRD, MHA…), por extensión o por la firma «DICM».
  2. Ninguna tabla de datos (CSV, TSV, XLSX, SAV, OMV…) fuera de `datos-ejemplo/` y `config/`;
     las de `datos-ejemplo/` empiezan por «DATOS SIMULADOS» en su primera línea.
  3. Ningún DNI, NIE ni NHC con número escrito en un archivo de texto.
Después ejecuta cada prueba de `autonomo/pruebas/*.py` (cada una sale con 0 si pasa).
Solo biblioteca estándar.
"""
import re
import subprocess
import sys
from pathlib import Path

IMAGEN = ('.dcm', '.dicom', '.ima', '.nii', '.nii.gz', '.nrrd', '.nhdr', '.seg', '.mha', '.mhd', '.raw', '.img', '.hdr')
TABLA = ('.csv', '.tsv', '.xlsx', '.xls', '.ods', '.sav', '.omv', '.dta', '.rds', '.parquet', '.feather')
TABLA_PERMITIDA = ('datos-ejemplo/', 'config/')
# DNI (8 cifras + letra), NIE (X/Y/Z + 7 cifras + letra) y «NHC» seguido de un número.
IDENTIFICADOR = re.compile(r'\b\d{8}[A-HJ-NP-TV-Z]\b|\b[XYZ]\d{7}[A-HJ-NP-TV-Z]\b|\bNHC\W{0,3}\d{4,}', re.I)
TEXTO = ('.md', '.txt', '.py', '.mjs', '.js', '.json', '.yaml', '.yml', '.csv', '.tsv', '.html', '.r', '.sps')


def archivos(raiz):
    salida = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
                            cwd=raiz, capture_output=True, check=True).stdout.decode()
    return [p for p in salida.split('\0') if p and (raiz / p).is_file()]


def fallos_de_datos(raiz):
    fallos = []
    for ruta in archivos(raiz):
        nombre = ruta.lower()
        absoluta = raiz / ruta
        if nombre.endswith(IMAGEN):
            fallos.append(f'{ruta}: imagen médica o máscara (no puede subirse)')
            continue
        with open(absoluta, 'rb') as f:
            cabecera = f.read(132)
        if cabecera[128:132] == b'DICM':
            fallos.append(f'{ruta}: es un DICOM aunque su extensión no lo diga')
            continue
        if nombre.endswith(TABLA):
            if not nombre.startswith(TABLA_PERMITIDA):
                fallos.append(f'{ruta}: tabla de datos fuera de datos-ejemplo/ o config/')
                continue
            if nombre.startswith('datos-ejemplo/'):
                primera = absoluta.read_text(encoding='utf-8', errors='replace').split('\n', 1)[0]
                if 'DATOS SIMULADOS' not in primera.upper():
                    fallos.append(f'{ruta}: le falta «DATOS SIMULADOS» en la primera línea')
                    continue
        if nombre.endswith(TEXTO):
            texto = absoluta.read_text(encoding='utf-8', errors='replace')
            for n, linea in enumerate(texto.splitlines(), 1):
                if IDENTIFICADOR.search(linea):
                    fallos.append(f'{ruta}:{n}: parece un DNI, NIE o NHC')
    return fallos


def fallos_de_pruebas(raiz):
    fallos = []
    for prueba in sorted((raiz / 'autonomo' / 'pruebas').glob('*.py')):
        r = subprocess.run([sys.executable, '-I', str(prueba)], cwd=raiz, capture_output=True, text=True)
        estado = 'pasa' if r.returncode == 0 else 'FALLA'
        print(f'  prueba {prueba.name}: {estado}')
        if r.returncode:
            fallos.append(f'{prueba.name}: {(r.stdout + r.stderr).strip()[-400:]}')
    return fallos


def main():
    raiz = Path(sys.argv[sys.argv.index('--raiz') + 1] if '--raiz' in sys.argv else '.').resolve()
    datos = fallos_de_datos(raiz)
    print(f'Datos de pacientes: {"✓ nada que no deba subirse" if not datos else "✗"}')
    for f in datos:
        print('  ✗', f)
    pruebas = [] if '--sin-pruebas' in sys.argv else fallos_de_pruebas(raiz)
    for f in pruebas:
        print('  ✗', f)
    todo = datos + pruebas
    print('JUECES EN VERDE' if not todo else f'JUECES EN ROJO: {len(todo)} fallo(s)')
    return 1 if todo else 0


if __name__ == '__main__':
    sys.exit(main())
