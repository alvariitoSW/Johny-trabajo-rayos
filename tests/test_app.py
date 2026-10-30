"""Pruebas de la app local (app/servidor.py) con DATOS SINTÉTICOS. Servidor en un hilo, puerto libre."""
import csv
import http.client
import json
import sys
import threading
import time
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'tests'))
sys.path.insert(0, str(RAIZ / 'app'))
import generar_sinteticos  # noqa: E402
import servidor  # noqa: E402


@pytest.fixture(scope='session')
def sinteticos(tmp_path_factory):
    carpeta = tmp_path_factory.mktemp('sint')
    verdad = generar_sinteticos.generar(carpeta, 3, 7)
    c = carpeta / 'crudo' / next(iter(verdad))
    if not (c / 'mascara.seg.nrrd').exists():  # el contenido no importa aquí: se prueba la copia
        otra = next(p for p in sorted(c.iterdir()) if p.is_file())
        (c / 'mascara.seg.nrrd').write_bytes(otra.read_bytes())
    return c


@pytest.fixture
def app(tmp_path):
    datos, res = tmp_path / 'datos', tmp_path / 'res'
    datos.mkdir()
    srv = servidor.crear_servidor(datos, res, 0)
    hilo = threading.Thread(target=srv.serve_forever, daemon=True)
    hilo.start()
    yield srv, datos, res
    srv.shutdown()
    srv.server_close()


def pedir(srv, metodo, ruta, cuerpo=None, token=True, host=None):
    e = srv.estado
    c = http.client.HTTPConnection('127.0.0.1', e.puerto, timeout=20)
    cab = {'Host': host or f'127.0.0.1:{e.puerto}'}
    if token:
        cab['X-Token'] = e.token
    datos = json.dumps(cuerpo) if cuerpo is not None else None
    c.putrequest(metodo, ruta, skip_host=True, skip_accept_encoding=True)
    for k, v in cab.items():
        c.putheader(k, v)
    if datos is not None:
        c.putheader('Content-Length', str(len(datos.encode())))
    c.endheaders(datos.encode() if datos else None)
    r = c.getresponse()
    cuerpo_r = r.read()
    c.close()
    return r.status, dict(r.getheaders()), cuerpo_r


def caso(srv, sint, **extra):
    d = {'id': 'RMH-001', 'imagen': str(sint / 'imagen'), 'mascara': str(sint / 'mascara.seg.nrrd')}
    d.update(extra)
    return pedir(srv, 'POST', '/api/caso', d)


def test_solo_escucha_en_loopback(app):
    assert app[0].server_address[0] == '127.0.0.1'


def test_sin_token_403(app):
    assert pedir(app[0], 'GET', '/api/estado', token=False)[0] == 403
    assert pedir(app[0], 'GET', '/', token=False)[0] == 403
    assert pedir(app[0], 'POST', '/api/caso', {}, token=False)[0] == 403
    assert pedir(app[0], 'GET', '/api/estado?t=mal', token=False)[0] == 403


def test_token_en_url_y_cabeceras(app):
    srv = app[0]
    s, cab, cuerpo = pedir(srv, 'GET', f'/?t={srv.estado.token}', token=False)
    assert s == 200 and b'Nada sale de este ordenador' in cuerpo
    assert cab['Cache-Control'] == 'no-store'
    assert b'http://' not in cuerpo and b'https://' not in cuerpo  # ningún recurso externo


def test_host_ajeno_403(app):
    srv = app[0]
    assert pedir(srv, 'GET', '/api/estado', host='evil.example')[0] == 403
    assert pedir(srv, 'GET', '/api/estado', host=f'evil.example:{srv.estado.puerto}')[0] == 403
    assert pedir(srv, 'GET', '/api/estado', host=f'localhost:{srv.estado.puerto}')[0] == 200


def test_token_distinto_por_sesion(tmp_path):
    a, b = servidor.crear_servidor(tmp_path, tmp_path, 0), servidor.crear_servidor(tmp_path, tmp_path, 0)
    try:
        assert a.estado.token != b.estado.token and len(a.estado.token) >= 32
    finally:
        a.server_close()
        b.server_close()


def test_log_no_escribe(app, capsys):
    pedir(app[0], 'GET', '/api/estado')
    s = capsys.readouterr()
    assert s.out == '' and s.err == ''


@pytest.mark.parametrize('codigo', ['Juan Perez', '../X', '', 'RMH-001/../../x'])
def test_codigo_invalido_no_crea_nada(app, sinteticos, codigo):
    srv, datos, _ = app
    s, _, c = caso(srv, sinteticos, id=codigo)
    assert s == 400 and 'error' in json.loads(c)
    assert list(datos.iterdir()) == []
    assert not (datos.parent / 'X').exists()


def test_nuevo_caso_copia_y_no_sobrescribe(app, sinteticos):
    srv, datos, _ = app
    s, _, c = caso(srv, sinteticos)
    assert s == 200, c
    destino = datos / 'crudo' / 'RMH-001'
    cortes = sorted((destino / 'imagen').iterdir())
    n_origen = len(list((sinteticos / 'imagen').glob('*.dcm')))
    assert len(cortes) == n_origen >= 2
    assert all(p.name.endswith('.dcm') and p.name[:4].isdigit() for p in cortes)  # nombres nuevos
    assert (destino / 'mascara.seg.nrrd').read_bytes() == (sinteticos / 'mascara.seg.nrrd').read_bytes()
    s2, _, c2 = caso(srv, sinteticos)
    assert s2 == 400 and 'ya existe' in json.loads(c2)['error']
    assert (sinteticos / 'mascara.seg.nrrd').exists()  # el origen sigue ahí


def test_errores_claros(app, sinteticos, tmp_path):
    srv, datos, _ = app
    vacia = tmp_path / 'vacia'
    vacia.mkdir()
    s, _, c = caso(srv, sinteticos, imagen=str(vacia))
    assert s == 400 and '.dcm' in json.loads(c)['error']
    otro = tmp_path / 'm.txt'
    otro.write_text('x')
    s, _, c = caso(srv, sinteticos, mascara=str(otro))
    assert s == 400 and 'seg.nrrd' in json.loads(c)['error']
    s, _, _ = caso(srv, sinteticos, mascara='')
    assert s == 400
    assert not (datos / 'crudo' / 'RMH-001').exists()


def test_dos_observadores_conservan_extension(app, sinteticos, tmp_path):
    srv, datos, _ = app
    m1, m2 = tmp_path / 'a.seg.nrrd', tmp_path / 'b.nrrd'
    m1.write_bytes(b'1')
    m2.write_bytes(b'2')
    s, _, c = caso(srv, sinteticos, mascara='', mascara1=str(m1), mascara2=str(m2))
    assert s == 200, c
    d = datos / 'crudo' / 'RMH-001'
    assert (d / 'mascara_obs1.seg.nrrd').exists() and (d / 'mascara_obs2.nrrd').exists()


def test_decision_csv_cabecera_exacta(app, sinteticos):
    srv, datos, _ = app
    assert pedir(srv, 'POST', '/api/decision', {'id': 'RMH-009', 'decision': 'incluir'})[0] == 400  # no existe
    caso(srv, sinteticos)
    assert pedir(srv, 'POST', '/api/decision', {'id': 'RMH-001', 'decision': 'quizá'})[0] == 400
    assert pedir(srv, 'POST', '/api/decision', {'id': 'RMH-001', 'decision': 'revisar', 'motivo': 'a'})[0] == 200
    assert pedir(srv, 'POST', '/api/decision', {'id': 'RMH-001', 'decision': 'excluir', 'motivo': 'artefacto, "x"\nlínea'})[0] == 200
    texto = (datos / 'decisiones_casos.csv').read_text(encoding='utf-8')
    assert texto.splitlines()[0] == 'id,decision,motivo'
    filas = list(csv.DictReader(texto.splitlines(), skipinitialspace=False))
    assert len(filas) == 1 and filas[0]['decision'] == 'excluir' and '\n' not in filas[0]['motivo']
    _, _, c = pedir(srv, 'GET', '/api/estado')
    lista = json.loads(c)['casos']
    assert lista[0]['id'] == 'RMH-001' and lista[0]['estado'] == 'preparado' and lista[0]['decision'] == 'excluir'


def test_estado_muestra_alertas_qc(app, sinteticos):
    srv, _, res = app
    caso(srv, sinteticos)
    res.mkdir()
    (res / 'qc_report.csv').write_text('id,alertas\nRMH-001,2 componentes\n', encoding='utf-8')
    lista = json.loads(pedir(srv, 'GET', '/api/estado')[2])['casos']
    assert lista[0]['alertas'] == '2 componentes'


def test_informe_solo_sirve_informe_y_figuras(app, tmp_path):
    srv, _, res = app
    (res / 'figuras').mkdir(parents=True)
    (res / 'informe.pdf').write_bytes(b'%PDF-prueba')
    (res / 'figuras' / 'f1.png').write_bytes(b'png')
    (res / 'qc_report.csv').write_text('secreto')
    (tmp_path / 'fuera.png').write_bytes(b'fuera')
    assert pedir(srv, 'GET', '/informe.pdf')[2] == b'%PDF-prueba'
    assert pedir(srv, 'GET', '/figuras/f1.png')[0] == 200
    for ruta in ['/informe/../../etc/passwd', '/../../etc/passwd', '/figuras/../qc_report.csv',
                 '/figuras/..%2Fqc_report.csv', '/figuras/%2e%2e/qc_report.csv', '/figuras/f1.txt',
                 '/qc_report.csv', '/informe.pdf/../qc_report.csv']:
        assert pedir(srv, 'GET', ruta)[0] in (403, 404), ruta
        assert b'secreto' not in pedir(srv, 'GET', ruta)[2]


def test_figura_enlace_simbolico_fuera_no_se_sirve(app, tmp_path):
    srv, _, res = app
    (res / 'figuras').mkdir(parents=True)
    fuera = tmp_path / 'fuera.png'
    fuera.write_bytes(b'fuera')
    try:
        (res / 'figuras' / 'e.png').symlink_to(fuera)
    except OSError:
        pytest.skip('sin enlaces simbólicos')
    assert pedir(srv, 'GET', '/figuras/e.png')[0] == 404


def test_binwidth_no_valido_y_un_solo_proceso(app, tmp_path):
    srv, _, _ = app
    assert pedir(srv, 'POST', '/api/ejecutar', {'binwidth': '5; rm -rf /'})[0] == 400
    espera = tmp_path / 'espera.py'
    espera.write_text('import time; time.sleep(3)')
    srv.estado.pipeline = espera
    assert pedir(srv, 'POST', '/api/ejecutar', {})[0] == 200
    assert pedir(srv, 'POST', '/api/ejecutar', {})[0] == 400  # ya en marcha
    srv.estado.proceso.kill()


def test_lanzar_pipeline_desde_la_app(tmp_path):
    """Ensayo real: 3 casos sintéticos preparados por la app y pipeline completo lanzado desde ella."""
    origen = tmp_path / 'origen'
    verdad = generar_sinteticos.generar(origen, 3, 7)
    datos, res = tmp_path / 'datos', tmp_path / 'res'
    datos.mkdir()
    srv = servidor.crear_servidor(datos, res, 0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        for n, i in enumerate(verdad, 1):
            c = origen / 'crudo' / i
            m = next(p for p in c.iterdir() if p.is_file())
            s, _, r = pedir(srv, 'POST', '/api/caso', {'id': f'RMH-00{n}', 'imagen': str(c / 'imagen'), 'mascara': str(m)})
            assert s == 200, r
        assert pedir(srv, 'POST', '/api/ejecutar', {})[0] == 200
        fin = time.time() + 600
        while time.time() < fin:
            sal = json.loads(pedir(srv, 'GET', '/api/salida?desde=0')[2])
            if not sal['en_marcha']:
                break
            time.sleep(1)
        assert sal['codigo'] == 0, '\n'.join(sal['lineas'][-15:])
        assert any('Paso 1' in l for l in sal['lineas'])
        assert pedir(srv, 'GET', '/informe.pdf')[2][:4] == b'%PDF'
    finally:
        srv.shutdown()
        srv.server_close()
