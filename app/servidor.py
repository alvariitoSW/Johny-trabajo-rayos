"""Interfaz local para preparar casos y lanzar el pipeline desde el navegador del PC del hospital.

Uso (desde la carpeta del proyecto):

    python app/servidor.py --datos data --resultados outputs [--puerto 8765] [--abrir]

Solo biblioteca estándar. Escucha únicamente en 127.0.0.1. Cada arranque crea un token aleatorio que va en la
URL impresa; sin él, 403. No recibe archivos por el navegador: el usuario escribe la ruta de una carpeta local y el
servidor copia. No borra nada del usuario. No escribe registro de peticiones.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'src'))
from comun import PATRON_ID, comprobar_id  # noqa: E402

EXT_MASCARA = ('.seg.nrrd', '.nrrd', '.dcm')
DECISIONES = ('incluir', 'excluir', 'revisar')
CABECERA_DECISIONES = ['id', 'decision', 'motivo']
MAX_CUERPO = 64 * 1024
MAX_LINEAS = 3000
FIGURA = re.compile(r'^[\w.-]+\.(png|svg|jpg)$')
TIPOS = {'.png': 'image/png', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg'}


class ErrorUsuario(Exception):
    """Error que se le explica al usuario (código 400)."""


class Estado:
    def __init__(self, datos: Path, resultados: Path, pipeline: Path):
        self.datos, self.resultados, self.pipeline = datos, resultados, pipeline
        self.token = secrets.token_urlsafe(32)
        self.puerto = 0
        self.lock = threading.Lock()
        self.proceso: subprocess.Popen | None = None
        self.lineas: list[str] = []
        self.codigo: int | None = None
        self.pyradiomics: bool | None = None

    def hay_pyradiomics(self) -> bool:
        if self.pyradiomics is None:
            try:
                import radiomics  # noqa: F401
                self.pyradiomics = True
            except Exception:
                self.pyradiomics = False
        return self.pyradiomics

    # ---- casos ----
    def _ids(self, carpeta: Path) -> set[str]:
        if not carpeta.is_dir():
            return set()
        return {p.name for p in carpeta.iterdir() if p.is_dir() and PATRON_ID.match(p.name)}

    def alertas_qc(self) -> dict[str, str]:
        ruta = self.resultados / 'qc_report.csv'
        if not ruta.is_file():
            return {}
        with ruta.open(encoding='utf-8', newline='') as f:
            return {fila.get('id', ''): fila.get('alertas', '') for fila in csv.DictReader(f)}

    def decisiones(self) -> dict[str, dict]:
        ruta = self.datos / 'decisiones_casos.csv'
        if not ruta.is_file():
            return {}
        with ruta.open(encoding='utf-8', newline='') as f:
            return {fila['id']: fila for fila in csv.DictReader(f) if fila.get('id')}

    def lista_casos(self) -> list[dict]:
        crudo, convertidos = self._ids(self.datos / 'crudo'), self._ids(self.datos / 'casos')
        qc, dec = self.alertas_qc(), self.decisiones()
        salida = []
        for i in sorted(crudo | convertidos):
            d = dec.get(i, {})
            salida.append({'id': i, 'estado': 'convertido' if i in convertidos else 'preparado',
                           'alertas': qc.get(i), 'decision': d.get('decision', ''), 'motivo': d.get('motivo', '')})
        return salida

    def nuevo_caso(self, d: dict) -> str:
        id_caso = str(d.get('id', '')).strip()
        try:
            comprobar_id(id_caso)
        except ValueError as e:
            raise ErrorUsuario(str(e))
        base = self.datos.resolve()
        destino = (base / 'crudo' / id_caso).resolve()
        if destino.parent.parent != base:
            raise ErrorUsuario('El destino queda fuera de la carpeta de datos.')
        if destino.exists() or (base / 'casos' / id_caso).exists():
            raise ErrorUsuario(f'El caso {id_caso} ya existe. No se sobrescribe.')
        carpeta = Path(str(d.get('imagen', '')).strip().strip('"')).expanduser()
        if not carpeta.is_dir():
            raise ErrorUsuario('La ruta de la imagen no es una carpeta.')
        cortes = sorted(p for p in carpeta.iterdir() if p.is_file() and p.suffix.lower() == '.dcm')
        if not cortes:
            raise ErrorUsuario('La carpeta no contiene archivos .dcm.')
        pares = [('mascara', 'mascara'), ('mascara1', 'mascara_obs1'), ('mascara2', 'mascara_obs2')]
        dadas = {k: str(d.get(k, '')).strip().strip('"') for k, _ in pares}
        if dadas['mascara'] and (dadas['mascara1'] or dadas['mascara2']):
            raise ErrorUsuario('Da una máscara o las dos de los observadores, no ambas.')
        if not dadas['mascara'] and not (dadas['mascara1'] and dadas['mascara2']):
            raise ErrorUsuario('Falta la máscara (o las dos de los observadores).')
        mascaras = []  # (origen, nombre de destino)
        for clave, nombre in pares:
            if not dadas[clave]:
                continue
            origen = Path(dadas[clave]).expanduser()
            if not origen.is_file():
                raise ErrorUsuario('La ruta de una máscara no es un archivo.')
            bajo = origen.name.lower()
            ext = next((e for e in EXT_MASCARA if bajo.endswith(e)), None)
            if ext is None:
                raise ErrorUsuario('La máscara debe ser .seg.nrrd, .nrrd o .dcm.')
            mascaras.append((origen, nombre + ext))
        (base / 'crudo').mkdir(parents=True, exist_ok=True)
        destino.mkdir()  # sin exist_ok: si alguien lo creó entre medias, falla
        try:
            (destino / 'imagen').mkdir()
            for n, c in enumerate(cortes, 1):  # nombres nuevos: no se conserva ningún nombre original
                shutil.copyfile(c, destino / 'imagen' / f'{n:04d}.dcm')
            for origen, nombre in mascaras:
                shutil.copyfile(origen, destino / nombre)
        except OSError:
            shutil.rmtree(destino, ignore_errors=True)  # solo la copia parcial que creamos nosotros
            raise ErrorUsuario('No se pudo copiar. Se deshizo la copia parcial.')
        return f'Caso {id_caso} preparado: {len(cortes)} cortes y {len(mascaras)} máscara(s).'

    def guardar_decision(self, d: dict) -> str:
        id_caso = str(d.get('id', '')).strip()
        try:
            comprobar_id(id_caso)
        except ValueError as e:
            raise ErrorUsuario(str(e))
        if id_caso not in self._ids(self.datos / 'crudo') | self._ids(self.datos / 'casos'):
            raise ErrorUsuario(f'El caso {id_caso} no existe.')
        decision = str(d.get('decision', '')).strip().lower()
        if decision not in DECISIONES:
            raise ErrorUsuario('La decisión debe ser incluir, excluir o revisar.')
        motivo = ' '.join(str(d.get('motivo', '')).split())[:200]
        with self.lock:
            filas = self.decisiones()
            filas[id_caso] = {'id': id_caso, 'decision': decision, 'motivo': motivo}
            self.datos.mkdir(parents=True, exist_ok=True)
            with (self.datos / 'decisiones_casos.csv').open('w', encoding='utf-8', newline='') as f:
                w = csv.DictWriter(f, fieldnames=CABECERA_DECISIONES, lineterminator='\n')
                w.writeheader()
                for i in sorted(filas):
                    w.writerow({k: filas[i].get(k, '') for k in CABECERA_DECISIONES})
        return f'Decisión de {id_caso} guardada.'

    # ---- ejecución ----
    def ejecutar(self, d: dict) -> str:
        bw = str(d.get('binwidth', '')).strip()
        if bw not in ('', '10', '25'):
            raise ErrorUsuario('binWidth solo puede ser 25, 10 o vacío.')
        with self.lock:
            if self.proceso is not None and self.codigo is None:
                raise ErrorUsuario('Ya hay una ejecución en marcha.')
            orden = [sys.executable, '-u', str(self.pipeline), '--input', str(self.datos),
                     '--output', str(self.resultados)] + (['--binwidth', bw] if bw else [])
            self.lineas, self.codigo = [], None
            self.proceso = subprocess.Popen(orden, cwd=str(RAIZ), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                            text=True, encoding='utf-8', errors='replace', shell=False,
                                            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
            threading.Thread(target=self._leer, args=(self.proceso,), daemon=True).start()
        return 'Pipeline lanzado.'

    def _leer(self, proc: subprocess.Popen) -> None:
        for linea in proc.stdout:
            with self.lock:
                if len(self.lineas) < MAX_LINEAS:
                    self.lineas.append(linea.rstrip('\n'))
        proc.wait()
        with self.lock:
            self.codigo = proc.returncode

    def salida(self, desde: int) -> dict:
        with self.lock:
            marcha = self.proceso is not None and self.codigo is None
            return {'lineas': self.lineas[desde:], 'total': len(self.lineas), 'en_marcha': marcha,
                    'codigo': self.codigo, 'lanzado': self.proceso is not None}

    def resumen(self) -> dict:
        figuras = self.resultados / 'figuras'
        return {'datos': str(self.datos), 'resultados': str(self.resultados), 'pyradiomics': self.hay_pyradiomics(),
                'casos': self.lista_casos(), 'informe': (self.resultados / 'informe.pdf').is_file(),
                'figuras': sorted(p.name for p in figuras.iterdir() if FIGURA.match(p.name))
                if figuras.is_dir() else []}


class Manejador(BaseHTTPRequestHandler):
    server_version = 'AppLocal'
    sys_version = ''

    def log_message(self, *args, **kwargs):  # no se escribe nada: ni rutas ni nombres
        pass

    @property
    def est(self) -> Estado:
        return self.server.estado

    def _enviar(self, codigo: int, cuerpo: bytes, tipo: str, extra: dict | None = None) -> None:
        self.send_response(codigo)
        self.send_header('Content-Type', tipo)
        self.send_header('Content-Length', str(len(cuerpo)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Content-Type-Options', 'nosniff')
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(cuerpo)

    def _json(self, codigo: int, obj) -> None:
        self._enviar(codigo, json.dumps(obj, ensure_ascii=False).encode('utf-8'), 'application/json; charset=utf-8')

    def _autorizado(self, consulta: dict) -> bool:
        host = self.headers.get('Host', '')
        if host not in (f'127.0.0.1:{self.est.puerto}', f'localhost:{self.est.puerto}'):
            return False
        token = self.headers.get('X-Token') or (consulta.get('t') or [''])[0]
        return secrets.compare_digest(token.encode(), self.est.token.encode())

    def _prohibido(self) -> None:
        self._enviar(403, 'Acceso denegado.'.encode(), 'text/plain; charset=utf-8')

    def _no_encontrado(self) -> None:
        self._enviar(404, b'No encontrado.', 'text/plain; charset=utf-8')

    def do_GET(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)
        if not self._autorizado(q):
            return self._prohibido()
        ruta = url.path
        if ruta == '/':
            html = (Path(__file__).resolve().parent / 'pagina.html').read_bytes()
            csp = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
                   "connect-src 'self'; img-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
            return self._enviar(200, html, 'text/html; charset=utf-8', {'Content-Security-Policy': csp})
        if ruta == '/api/estado':
            return self._json(200, self.est.resumen())
        if ruta == '/api/salida':
            try:
                desde = max(0, int((q.get('desde') or ['0'])[0]))
            except ValueError:
                desde = 0
            return self._json(200, self.est.salida(desde))
        if ruta == '/informe.pdf':
            return self._archivo(self.est.resultados / 'informe.pdf', 'application/pdf')
        if ruta.startswith('/figuras/'):
            nombre = ruta[len('/figuras/'):]
            if not FIGURA.match(nombre):
                return self._no_encontrado()
            return self._archivo(self.est.resultados / 'figuras' / nombre, TIPOS[Path(nombre).suffix])
        self._no_encontrado()

    def _archivo(self, ruta: Path, tipo: str) -> None:
        try:
            real = ruta.resolve(strict=True)
            if real.parent != ruta.parent.resolve() or not real.is_file():
                raise FileNotFoundError
            contenido = real.read_bytes()
        except OSError:
            return self._no_encontrado()
        self._enviar(200, contenido, tipo)

    def do_POST(self):
        url = urlparse(self.path)
        if not self._autorizado(parse_qs(url.query)):
            return self._prohibido()
        try:
            n = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            n = -1
        if n < 0 or n > MAX_CUERPO:
            return self._json(413, {'error': 'Petición demasiado grande.'})
        try:
            d = json.loads(self.rfile.read(n) or b'{}')
            if not isinstance(d, dict):
                raise ValueError
        except ValueError:
            return self._json(400, {'error': 'Petición no válida.'})
        acciones = {'/api/caso': self.est.nuevo_caso, '/api/decision': self.est.guardar_decision,
                    '/api/ejecutar': self.est.ejecutar}
        accion = acciones.get(url.path)
        if accion is None:
            return self._json(404, {'error': 'No encontrado.'})
        try:
            self._json(200, {'mensaje': accion(d)})
        except ErrorUsuario as e:
            self._json(400, {'error': str(e)})
        except Exception:
            self._json(500, {'error': 'Error interno.'})


def crear_servidor(datos: Path, resultados: Path, puerto: int = 8765, pipeline: Path | None = None) -> ThreadingHTTPServer:
    srv = ThreadingHTTPServer(('127.0.0.1', puerto), Manejador)
    srv.daemon_threads = True
    srv.estado = Estado(Path(datos), Path(resultados), pipeline or RAIZ / 'run_pipeline.py')
    srv.estado.puerto = srv.server_address[1]
    return srv


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--datos', type=Path, default=Path('data'))
    p.add_argument('--resultados', type=Path, default=Path('outputs'))
    p.add_argument('--puerto', type=int, default=8765)
    p.add_argument('--abrir', action='store_true', help='abre la dirección en el navegador')
    a = p.parse_args(argv)
    srv = crear_servidor(a.datos, a.resultados, a.puerto)
    url = f'http://127.0.0.1:{srv.estado.puerto}/?t={srv.estado.token}'
    print('Solo en el PC del hospital. Nada sale de este ordenador.')
    print(f'Abre esta dirección en el navegador:\n{url}')
    print('Para cerrar: Ctrl+C.', flush=True)
    if a.abrir:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\nCerrado.')
    finally:
        srv.server_close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
