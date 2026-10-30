// Pruebas de GET /api/entries: orden y filtros (según SPEC.md).
import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { startServer, assertValidationError } from './helpers.js';

let srv;
const ids = {};

before(async () => {
  srv = await startServer();
  // Lista vacía antes de sembrar datos.
  const empty = await srv.api('GET', '/api/entries');
  assert.equal(empty.status, 200);
  assert.deepEqual(empty.body, []);

  const seed = [
    ['a', { date: '2026-10-28', title: 'Reunión de equipo', notes: 'Planificación semanal', minutes: 60, category: 'Reuniones', status: 'completada', tags: ['equipo'] }],
    ['b', { date: '2026-10-30', title: 'Fix login bug', notes: 'Problema con OAuth', minutes: 45, category: 'Desarrollo', status: 'en_progreso', tags: ['backend', 'urgente'] }],
    ['c', { date: '2026-10-29', title: 'Documentación', notes: 'Escribir README del BACKEND', minutes: 30, category: 'Desarrollo', status: 'pendiente', tags: ['docs'] }],
    ['d', { date: '2026-10-30', title: 'Llamada cliente', notes: '', minutes: 20, category: 'General', status: 'completada', tags: [] }],
    ['e', { date: '2026-10-27', title: 'Descuento 50% aplicado', notes: 'usar_guion', minutes: 10, category: 'desarrollo', status: 'completada', tags: ['backend-legacy'] }],
    ['f', { date: '2026-11-01', title: 'Revisión mensual', notes: 'ÁREA de ventas', minutes: 15, category: 'Reuniones', status: 'pendiente', tags: ['ventas'] }],
  ];
  for (const [key, payload] of seed) {
    const res = await srv.api('POST', '/api/entries', payload);
    assert.equal(res.status, 201, res.text);
    ids[key] = res.body.id;
  }
});

after(async () => {
  await srv.close();
});

async function listIds(query = '') {
  const res = await srv.api('GET', `/api/entries${query}`);
  assert.equal(res.status, 200, `${query}: ${res.text}`);
  assert.ok(Array.isArray(res.body));
  return res.body.map((e) => e.id);
}

const sortIds = (arr) => [...arr].sort((x, y) => x - y);
const keys = (...k) => k.map((x) => ids[x]);

describe('GET /api/entries — orden', () => {
  it('ordena por date desc y luego id desc', async () => {
    const res = await srv.api('GET', '/api/entries');
    assert.equal(res.status, 200);
    assert.match(res.headers.get('content-type') || '', /application\/json/);
    // f(11-01), d(10-30, id mayor), b(10-30), c(10-29), a(10-28), e(10-27)
    assert.deepEqual(res.body.map((e) => e.id), keys('f', 'd', 'b', 'c', 'a', 'e'));
  });

  it('cada elemento tiene tags como arreglo', async () => {
    const res = await srv.api('GET', '/api/entries');
    for (const e of res.body) assert.ok(Array.isArray(e.tags));
    const b = res.body.find((e) => e.id === ids.b);
    assert.deepEqual(b.tags, ['backend', 'urgente']);
  });
});

describe('GET /api/entries — filtros', () => {
  it('from (inclusive)', async () => {
    assert.deepEqual(await listIds('?from=2026-10-29'), keys('f', 'd', 'b', 'c'));
  });

  it('to (inclusive)', async () => {
    assert.deepEqual(await listIds('?to=2026-10-28'), keys('a', 'e'));
  });

  it('from + to (ambos inclusive)', async () => {
    assert.deepEqual(await listIds('?from=2026-10-28&to=2026-10-30'), keys('d', 'b', 'c', 'a'));
  });

  it('from = to → solo ese día', async () => {
    assert.deepEqual(await listIds('?from=2026-10-30&to=2026-10-30'), keys('d', 'b'));
  });

  it('rango sin resultados → []', async () => {
    assert.deepEqual(await listIds('?from=2025-01-01&to=2025-01-31'), []);
  });

  it('q busca en title sin distinguir mayúsculas', async () => {
    assert.deepEqual(await listIds('?q=LOGIN'), keys('b'));
    assert.deepEqual(await listIds('?q=reunión'), keys('a'));
  });

  it('q busca en notes sin distinguir mayúsculas', async () => {
    assert.deepEqual(await listIds('?q=oauth'), keys('b'));
    // "backend" está en notes de c (como "BACKEND"); no busca en tags.
    assert.deepEqual(await listIds('?q=backend'), keys('c'));
  });

  it('q coincide por subcadena en title o notes', async () => {
    // "re" aparece en: a (Reunión), c (Escribir README), f (Revisión)
    assert.deepEqual(sortIds(await listIds('?q=re')), sortIds(keys('a', 'c', 'f')));
  });

  it('q sin distinguir mayúsculas con caracteres acentuados (Á/á)', async () => {
    assert.deepEqual(await listIds(`?q=${encodeURIComponent('área')}`), keys('f'));
    assert.deepEqual(await listIds(`?q=${encodeURIComponent('REUNIÓN')}`), keys('a'));
  });

  it('q trata % y _ literalmente', async () => {
    assert.deepEqual(await listIds(`?q=${encodeURIComponent('50%')}`), keys('e'));
    assert.deepEqual(await listIds(`?q=${encodeURIComponent('%')}`), keys('e'));
    assert.deepEqual(await listIds(`?q=${encodeURIComponent('_')}`), keys('e'));
  });

  it('category exacta (distingue mayúsculas y no es subcadena)', async () => {
    assert.deepEqual(await listIds('?category=Desarrollo'), keys('b', 'c'));
    assert.deepEqual(await listIds('?category=desarrollo'), keys('e'));
    assert.deepEqual(await listIds('?category=Desarr'), []);
    assert.deepEqual(await listIds('?category=General'), keys('d'));
  });

  it('status', async () => {
    assert.deepEqual(await listIds('?status=pendiente'), keys('f', 'c'));
    assert.deepEqual(await listIds('?status=en_progreso'), keys('b'));
    assert.deepEqual(await listIds('?status=completada'), keys('d', 'a', 'e'));
  });

  it('tag: contiene exactamente ese tag (no subcadena)', async () => {
    assert.deepEqual(await listIds('?tag=backend'), keys('b'));
    assert.deepEqual(await listIds('?tag=urgente'), keys('b'));
    assert.deepEqual(await listIds('?tag=equipo'), keys('a'));
    assert.deepEqual(await listIds('?tag=back'), []);
  });

  it('combinación de filtros (AND)', async () => {
    assert.deepEqual(await listIds('?category=Desarrollo&status=pendiente'), keys('c'));
    assert.deepEqual(await listIds('?from=2026-10-29&category=Reuniones'), keys('f'));
    assert.deepEqual(await listIds('?q=bug&tag=urgente&status=en_progreso'), keys('b'));
    assert.deepEqual(await listIds('?q=bug&status=completada'), []);
  });

  it('parámetros vacíos se ignoran o no rompen (sin 500)', async () => {
    const res = await srv.api('GET', '/api/entries?q=');
    assert.equal(res.status, 200, res.text);
    assert.equal(res.body.length, 6);
  });
});

describe('GET /api/entries — parámetros inválidos → 400', () => {
  const bad = [
    'from=ayer',
    'from=2026-1-5',
    'from=2026-02-30',
    'to=2026-13-01',
    'to=30/10/2026',
    'status=hecho',
    'status=COMPLETADA',
  ];
  for (const qs of bad) {
    it(`?${qs}`, async () => {
      const res = await srv.api('GET', `/api/entries?${qs}`);
      assertValidationError(assert, res, qs);
    });
  }
});
