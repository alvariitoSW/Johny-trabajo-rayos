"""Prueba trampa de jueces.py: en un repositorio de usar y tirar mete cada cosa prohibida y comprueba que la caza,
y que lo permitido (datos simulados, diccionario) pasa."""
import subprocess
import sys
import tempfile
from pathlib import Path

JUECES = Path(__file__).resolve().parents[1] / 'jueces.py'


def jueces(raiz):
    r = subprocess.run([sys.executable, '-I', str(JUECES), '--raiz', str(raiz), '--sin-pruebas'],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


with tempfile.TemporaryDirectory() as tmp:
    raiz = Path(tmp)
    subprocess.run(['git', 'init', '-q'], cwd=raiz, check=True)
    (raiz / 'datos-ejemplo').mkdir()
    (raiz / 'analisis' / 'config').mkdir(parents=True)
    (raiz / 'datos-ejemplo' / 'muestra.csv').write_text('# DATOS SIMULADOS\ncodigo,edad\nRMH-001,64\n')
    (raiz / 'analisis' / 'config' / 'diccionario.csv').write_text('variable,unidad\nedad,años\n')
    (raiz / 'notas.md').write_text('Paciente RMH-001, segmento VII.\n')
    codigo, salida = jueces(raiz)
    assert codigo == 0, f'lo permitido no debería fallar:\n{salida}'

    trampas = {
        'serie/corte001.dcm': b'x',
        'mascara.nii.gz': b'x',
        'sin_extension': b'\0' * 128 + b'DICM',
        'export.csv': b'codigo,edad\n1,64\n',
        'datos-ejemplo/real.csv': b'codigo,edad\n1,64\n',
        # Troceado para que el propio juez no lo cace en este archivo.
        'apunte.md': ('DNI 1234' + '5678Z, ' + 'NHC: 445' + '5667').encode(),
    }
    for ruta, contenido in trampas.items():
        (raiz / ruta).parent.mkdir(parents=True, exist_ok=True)
        (raiz / ruta).write_bytes(contenido)
    codigo, salida = jueces(raiz)
    assert codigo == 1, salida
    for ruta in trampas:
        assert ruta in salida, f'no cazó {ruta}:\n{salida}'

print('jueces_trampa: caza las 6 trampas y deja pasar lo permitido')
