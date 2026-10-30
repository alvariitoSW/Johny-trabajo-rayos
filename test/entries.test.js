// Pruebas de salud, CRUD, validación y errores de /api/entries (según SPEC.md).
import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import {
  startServer,
  validEntry,
  assertValidationError,
  assertNotFound,
  ISO_RE,
} from './helpers.js';

let srv;
before(async () => {
  srv = await startServer();
});
after(async () => {
  await srv.close();
});

const ENTRY_KEYS = [
  'category',
  'createdAt',
  'date',
  'id',
  'minutes',
  'notes',
  'status',
  'tags',
  'title',
  'updatedAt',
].sort();

function assertEntryShape(e) {
  assert.deepEqual(Object.keys(e).sort(), ENTRY_KEYS, 'la entrada usa exactamente los campos del spec');
  assert.ok(Number.isInteger(e.id), 'id entero');
  assert.match(e.date, /^\d{4}-\d{2}-\d{2}$/);
  assert.equal(typeof e.title, 'string');
  assert.equal(typeof e.notes, 'string');
  assert.ok(Number.isInteger(e.minutes), 'minutes entero');
  assert.equal(typeof e.category, 'string');
  assert.ok(['pendiente', 'en_progreso', 'completada'].includes(e.status));
  assert.ok(Array.isArray(e.tags), 'tags siempre es arreglo');
  assert.match(e.createdAt, ISO_RE, 'createdAt ISO 8601');
  assert.match(e.updatedAt, ISO_RE, 'updatedAt ISO 8601');
}

describe('health', () => {
  it('GET /api/health → 200 {"status":"ok"}', async () => {
    const res = await srv.api('GET', '/api/health');
    assert.equal(res.status, 200);
    assert.match(res.headers.get('content-type') || '', /application\/json/);
    assert.deepEqual(res.body, { status: 'ok' });
  });
});

describe('POST /api/entries — creación', () => {
  it('crea con valores por defecto', async () => {
    const res = await srv.api('POST', '/api/entries', { date: '2026-10-30', title: 'Solo título' });
    assert.equal(res.status, 201, res.text);
    assertEntryShape(res.body);
    assert.equal(res.body.date, '2026-10-30');
    assert.equal(res.body.title, 'Solo título');
    assert.equal(res.body.notes, '');
    assert.equal(res.body.minutes, 0);
    assert.equal(res.body.category, 'General');
    assert.equal(res.body.status, 'completada');
    assert.deepEqual(res.body.tags, []);
  });

  it('crea con todos los campos y los devuelve', async () => {
    const payload = {
      date: '2026-10-29',
      title: 'Revisión de código',
      notes: 'PR #42',
      minutes: 90,
      category: 'Desarrollo',
      status: 'en_progreso',
      tags: ['backend', 'review'],
    };
    const res = await srv.api('POST', '/api/entries', payload);
    assert.equal(res.status, 201, res.text);
    assertEntryShape(res.body);
    for (const [k, v] of Object.entries(payload)) assert.deepEqual(res.body[k], v, k);
  });

  it('acepta cada estado válido', async () => {
    for (const status of ['pendiente', 'en_progreso', 'completada']) {
      const res = await srv.api('POST', '/api/entries', validEntry({ status }));
      assert.equal(res.status, 201, `${status}: ${res.text}`);
      assert.equal(res.body.status, status);
    }
  });

  it('asigna ids autoincrementales distintos', async () => {
    const a = await srv.api('POST', '/api/entries', validEntry());
    const b = await srv.api('POST', '/api/entries', validEntry());
    assert.equal(a.status, 201);
    assert.equal(b.status, 201);
    assert.ok(b.body.id > a.body.id, 'id creciente');
  });

  it('recorta (trim) title, tags, y almacena el valor recortado', async () => {
    const res = await srv.api(
      'POST',
      '/api/entries',
      validEntry({ title: '   Con espacios  ', tags: ['  uno ', 'dos  '] })
    );
    assert.equal(res.status, 201, res.text);
    assert.equal(res.body.title, 'Con espacios');
    assert.deepEqual(res.body.tags, ['uno', 'dos']);
    const got = await srv.api('GET', `/api/entries/${res.body.id}`);
    assert.equal(got.body.title, 'Con espacios');
    assert.deepEqual(got.body.tags, ['uno', 'dos']);
  });

  it('límites aceptados: title 200 chars, minutes 0 y 1440, notes 5000, category 50, 10 tags de 30 chars', async () => {
    const tags = Array.from({ length: 10 }, (_, i) => String(i).padEnd(30, 'x'));
    const res = await srv.api(
      'POST',
      '/api/entries',
      validEntry({
        title: 'a'.repeat(200),
        notes: 'n'.repeat(5000),
        category: 'c'.repeat(50),
        minutes: 1440,
        tags,
      })
    );
    assert.equal(res.status, 201, res.text);
    assert.equal(res.body.title.length, 200);
    assert.equal(res.body.notes.length, 5000);
    assert.equal(res.body.category.length, 50);
    assert.equal(res.body.minutes, 1440);
    assert.deepEqual(res.body.tags, tags);

    const zero = await srv.api('POST', '/api/entries', validEntry({ minutes: 0 }));
    assert.equal(zero.status, 201, zero.text);
    assert.equal(zero.body.minutes, 0);
  });

  it('title de 200 chars tras trim (con espacios alrededor) se acepta', async () => {
    const res = await srv.api('POST', '/api/entries', validEntry({ title: `  ${'b'.repeat(200)}  ` }));
    assert.equal(res.status, 201, res.text);
    assert.equal(res.body.title, 'b'.repeat(200));
  });

  it('acepta 29 de febrero en año bisiesto', async () => {
    const res = await srv.api('POST', '/api/entries', validEntry({ date: '2028-02-29' }));
    assert.equal(res.status, 201, res.text);
    assert.equal(res.body.date, '2028-02-29');
  });

  it('createdAt y updatedAt los asigna el servidor (ignora los del cliente)', async () => {
    const res = await srv.api(
      'POST',
      '/api/entries',
      validEntry({ createdAt: '1999-01-01T00:00:00.000Z', updatedAt: '1999-01-01T00:00:00.000Z' })
    );
    assert.equal(res.status, 201, res.text);
    assert.notEqual(res.body.createdAt, '1999-01-01T00:00:00.000Z');
    assert.notEqual(res.body.updatedAt, '1999-01-01T00:00:00.000Z');
    const created = Date.parse(res.body.createdAt);
    assert.ok(Math.abs(Date.now() - created) < 60_000, 'createdAt es "ahora"');
  });
});

describe('POST /api/entries — validación (400 + details)', () => {
  const cases = [
    ['sin date', { title: 'x' }],
    ['date null', { date: null, title: 'x' }],
    ['date vacía', { date: '', title: 'x' }],
    ['date numérica', { date: 20261030, title: 'x' }],
    ['date formato inválido (texto)', { date: 'ayer', title: 'x' }],
    ['date sin ceros (2026-1-5)', { date: '2026-1-5', title: 'x' }],
    ['date formato DD/MM/YYYY', { date: '30/10/2026', title: 'x' }],
    ['date con hora', { date: '2026-10-30T10:00:00Z', title: 'x' }],
    ['date imposible 2026-02-30', { date: '2026-02-30', title: 'x' }],
    ['date imposible 2026-02-29 (no bisiesto)', { date: '2026-02-29', title: 'x' }],
    ['date imposible 2026-13-01', { date: '2026-13-01', title: 'x' }],
    ['date imposible 2026-04-31', { date: '2026-04-31', title: 'x' }],
    ['date imposible 2026-00-10', { date: '2026-00-10', title: 'x' }],
    ['date imposible 2026-10-00', { date: '2026-10-00', title: 'x' }],
    ['sin title', { date: '2026-10-30' }],
    ['title vacío', { date: '2026-10-30', title: '' }],
    ['title solo espacios', { date: '2026-10-30', title: '    ' }],
    ['title 201 chars', { date: '2026-10-30', title: 'a'.repeat(201) }],
    ['title no string', { date: '2026-10-30', title: 123 }],
    ['notes > 5000', validEntry({ notes: 'n'.repeat(5001) })],
    ['notes no string', validEntry({ notes: 42 })],
    ['minutes negativo', validEntry({ minutes: -1 })],
    ['minutes 1441', validEntry({ minutes: 1441 })],
    ['minutes decimal 1.5', validEntry({ minutes: 1.5 })],
    ['minutes texto no numérico', validEntry({ minutes: 'mucho' })],
    ['minutes booleano', validEntry({ minutes: true })],
    ['category > 50', validEntry({ category: 'c'.repeat(51) })],
    ['category no string', validEntry({ category: 7 })],
    ['status inválido', validEntry({ status: 'hecho' })],
    ['status en mayúsculas', validEntry({ status: 'COMPLETADA' })],
    ['tags no arreglo (string)', validEntry({ tags: 'a,b' })],
    ['tags con elemento no string', validEntry({ tags: ['ok', 5] })],
    ['tags con elemento vacío', validEntry({ tags: ['ok', ''] })],
    ['tags con elemento solo espacios', validEntry({ tags: ['ok', '   '] })],
    ['tag > 30 chars', validEntry({ tags: ['t'.repeat(31)] })],
    ['más de 10 tags', validEntry({ tags: Array.from({ length: 11 }, (_, i) => `t${i}`) })],
  ];

  for (const [name, payload] of cases) {
    it(`rechaza: ${name}`, async () => {
      const res = await srv.api('POST', '/api/entries', payload);
      assertValidationError(assert, res, `(${name})`);
    });
  }

  it('reporta varios errores a la vez en details', async () => {
    const res = await srv.api('POST', '/api/entries', {
      date: '2026-02-30',
      title: '',
      minutes: 5000,
      status: 'x',
    });
    assertValidationError(assert, res);
    assert.ok(res.body.details.length >= 2, `esperaba ≥2 details, obtuvo ${JSON.stringify(res.body.details)}`);
  });

  it('cuerpo no-objeto (arreglo) → 400', async () => {
    const res = await srv.api('POST', '/api/entries', [validEntry()]);
    assert.equal(res.status, 400, res.text);
  });

  it('una entrada rechazada no se guarda', async () => {
    const before = await srv.api('GET', '/api/entries');
    await srv.api('POST', '/api/entries', validEntry({ title: 'NO-GUARDAR', minutes: -5 }));
    const after = await srv.api('GET', '/api/entries');
    assert.equal(after.body.length, before.body.length);
    assert.ok(!after.body.some((e) => e.title === 'NO-GUARDAR'));
  });
});

describe('tags — duplicados', () => {
  it('no se almacenan duplicados (se rechazan con 400 o se eliminan)', async () => {
    const res = await srv.api('POST', '/api/entries', validEntry({ tags: ['a', 'b', 'a'] }));
    if (res.status === 400) {
      assertValidationError(assert, res);
    } else {
      assert.equal(res.status, 201, res.text);
      assert.deepEqual(res.body.tags, ['a', 'b']);
    }
  });

  it('duplicados tras trim cuentan como duplicados', async () => {
    const res = await srv.api('POST', '/api/entries', validEntry({ tags: ['a', ' a '] }));
    if (res.status === 400) {
      assertValidationError(assert, res);
    } else {
      assert.equal(res.status, 201, res.text);
      assert.deepEqual(res.body.tags, ['a']);
    }
  });
});

describe('JSON mal formado', () => {
  it('POST con JSON inválido → 400', async () => {
    const res = await srv.api('POST', '/api/entries', '{"date": "2026-10-30", "title": ', { raw: true });
    assert.equal(res.status, 400, res.text);
    assert.ok(res.body && typeof res.body.error === 'string', `cuerpo JSON con error: ${res.text}`);
  });

  it('PUT con JSON inválido → 400', async () => {
    const created = await srv.api('POST', '/api/entries', validEntry());
    const res = await srv.api('PUT', `/api/entries/${created.body.id}`, '{not json}', { raw: true });
    assert.equal(res.status, 400, res.text);
    assert.ok(res.body && typeof res.body.error === 'string', `cuerpo JSON con error: ${res.text}`);
  });
});

describe('GET /api/entries/:id', () => {
  it('devuelve la entrada', async () => {
    const created = await srv.api('POST', '/api/entries', validEntry({ title: 'Leer', tags: ['x'] }));
    const res = await srv.api('GET', `/api/entries/${created.body.id}`);
    assert.equal(res.status, 200);
    assertEntryShape(res.body);
    assert.deepEqual(res.body, created.body);
  });

  it('id inexistente → 404 {"error":"No encontrado"}', async () => {
    assertNotFound(assert, await srv.api('GET', '/api/entries/999999'));
  });

  it('id no numérico → 404', async () => {
    assertNotFound(assert, await srv.api('GET', '/api/entries/abc'));
    assertNotFound(assert, await srv.api('GET', '/api/entries/1abc'));
    assertNotFound(assert, await srv.api('GET', '/api/entries/1.5'));
  });
});

describe('PUT /api/entries/:id', () => {
  it('reemplazo completo: actualiza campos y conserva id/createdAt', async () => {
    const created = await srv.api(
      'POST',
      '/api/entries',
      validEntry({ notes: 'antes', minutes: 30, category: 'Viejo', status: 'pendiente', tags: ['t1'] })
    );
    await new Promise((r) => setTimeout(r, 15));
    const payload = {
      date: '2026-10-01',
      title: '  Nuevo título ',
      notes: 'después',
      minutes: 45,
      category: 'Nuevo',
      status: 'en_progreso',
      tags: ['t2', 't3'],
    };
    const res = await srv.api('PUT', `/api/entries/${created.body.id}`, payload);
    assert.equal(res.status, 200, res.text);
    assertEntryShape(res.body);
    assert.equal(res.body.id, created.body.id);
    assert.equal(res.body.title, 'Nuevo título');
    assert.equal(res.body.date, '2026-10-01');
    assert.equal(res.body.notes, 'después');
    assert.equal(res.body.minutes, 45);
    assert.equal(res.body.category, 'Nuevo');
    assert.equal(res.body.status, 'en_progreso');
    assert.deepEqual(res.body.tags, ['t2', 't3']);
    assert.equal(res.body.createdAt, created.body.createdAt, 'createdAt no cambia');
    assert.ok(
      Date.parse(res.body.updatedAt) >= Date.parse(created.body.createdAt),
      'updatedAt ≥ createdAt'
    );
    const got = await srv.api('GET', `/api/entries/${created.body.id}`);
    assert.deepEqual(got.body, res.body, 'el cambio persiste');
  });

  it('reemplazo completo: campos omitidos vuelven a su default', async () => {
    const created = await srv.api(
      'POST',
      '/api/entries',
      validEntry({ notes: 'algo', minutes: 30, category: 'Otra', status: 'pendiente', tags: ['t'] })
    );
    const res = await srv.api('PUT', `/api/entries/${created.body.id}`, {
      date: '2026-10-30',
      title: 'Mínimo',
    });
    assert.equal(res.status, 200, res.text);
    assert.equal(res.body.notes, '');
    assert.equal(res.body.minutes, 0);
    assert.equal(res.body.category, 'General');
    assert.equal(res.body.status, 'completada');
    assert.deepEqual(res.body.tags, []);
  });

  it('mismas reglas que POST → 400 con details', async () => {
    const created = await srv.api('POST', '/api/entries', validEntry());
    const bads = [
      { title: 'x' },
      { date: '2026-02-30', title: 'x' },
      validEntry({ title: '' }),
      validEntry({ minutes: 1441 }),
      validEntry({ minutes: 2.5 }),
      validEntry({ status: 'nope' }),
      validEntry({ tags: Array.from({ length: 11 }, (_, i) => `t${i}`) }),
    ];
    for (const b of bads) {
      const res = await srv.api('PUT', `/api/entries/${created.body.id}`, b);
      assertValidationError(assert, res, JSON.stringify(b).slice(0, 80));
    }
    const got = await srv.api('GET', `/api/entries/${created.body.id}`);
    assert.deepEqual(got.body, created.body, 'un PUT inválido no modifica la entrada');
  });

  it('id inexistente → 404', async () => {
    assertNotFound(assert, await srv.api('PUT', '/api/entries/999999', validEntry()));
  });

  it('id no numérico → 404', async () => {
    assertNotFound(assert, await srv.api('PUT', '/api/entries/abc', validEntry()));
  });
});

describe('DELETE /api/entries/:id', () => {
  it('borra → 204 sin cuerpo, luego GET → 404', async () => {
    const created = await srv.api('POST', '/api/entries', validEntry());
    const res = await srv.api('DELETE', `/api/entries/${created.body.id}`);
    assert.equal(res.status, 204);
    assert.equal(res.text, '');
    assertNotFound(assert, await srv.api('GET', `/api/entries/${created.body.id}`));
  });

  it('borrar dos veces → 404 la segunda', async () => {
    const created = await srv.api('POST', '/api/entries', validEntry());
    assert.equal((await srv.api('DELETE', `/api/entries/${created.body.id}`)).status, 204);
    assertNotFound(assert, await srv.api('DELETE', `/api/entries/${created.body.id}`));
  });

  it('id inexistente → 404', async () => {
    assertNotFound(assert, await srv.api('DELETE', '/api/entries/999999'));
  });

  it('id no numérico → 404', async () => {
    assertNotFound(assert, await srv.api('DELETE', '/api/entries/abc'));
  });
});
