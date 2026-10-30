// Pruebas de GET /api/export.csv (según SPEC.md).
import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { startServer, parseCsv } from './helpers.js';

let srv;
const created = {};

const HEADER = ['id', 'date', 'title', 'minutes', 'category', 'status', 'tags', 'notes'];

async function getCsv(qs = '') {
  const res = await fetch(`${srv.base}/api/export.csv${qs}`);
  const buf = Buffer.from(await res.arrayBuffer());
  return { res, buf, text: buf.toString('utf8') };
}

before(async () => {
  srv = await startServer();
});
after(async () => {
  await srv.close();
});

describe('export.csv sin datos', () => {
  it('solo encabezado', async () => {
    const { res, text } = await getCsv();
    assert.equal(res.status, 200);
    const rows = parseCsv(text).filter((r) => !(r.length === 1 && r[0] === ''));
    assert.deepEqual(rows, [HEADER]);
  });
});

describe('export.csv con datos', () => {
  before(async () => {
    const seed = [
      ['plain', { date: '2026-10-30', title: 'Simple', minutes: 15, category: 'General', status: 'completada', tags: ['a', 'b', 'c'], notes: 'nada raro' }],
      ['comma', { date: '2026-10-28', title: 'Uno, dos, tres', minutes: 30, category: 'Cat, con coma', status: 'pendiente', tags: [], notes: '' }],
      ['quote', { date: '2026-10-29', title: 'Dijo "hola"', minutes: 0, status: 'en_progreso', tags: ['x'], notes: 'comillas "dobles" aquí' }],
      ['newline', { date: '2026-10-31', title: 'Multilínea', minutes: 1440, tags: ['solo'], notes: 'línea 1\nlínea 2\r\nlínea 3' }],
      ['accent', { date: '2026-10-27', title: 'Ñandú café — acción', minutes: 5, category: 'Reunión', tags: ['ñ'], notes: 'ü' }],
    ];
    for (const [k, payload] of seed) {
      const res = await srv.api('POST', '/api/entries', payload);
      assert.equal(res.status, 201, res.text);
      created[k] = res.body;
    }
  });

  it('cabeceras: 200, text/csv; charset=utf-8, Content-Disposition attachment', async () => {
    const { res } = await getCsv();
    assert.equal(res.status, 200);
    const ct = (res.headers.get('content-type') || '').toLowerCase().replace(/\s+/g, '');
    assert.match(ct, /^text\/csv;charset=utf-8$/, `content-type: ${res.headers.get('content-type')}`);
    assert.equal(res.headers.get('content-disposition'), 'attachment; filename="bitacora.csv"');
  });

  it('BOM opcional al inicio y encabezado exacto en la primera línea', async () => {
    const { buf, text } = await getCsv();
    const hasBom = buf[0] === 0xef && buf[1] === 0xbb && buf[2] === 0xbf;
    const body = hasBom ? text.slice(1) : text;
    assert.ok(body.startsWith('id,date,title,minutes,category,status,tags,notes\r\n') ||
      body.startsWith('id,date,title,minutes,category,status,tags,notes\n'),
      `primera línea: ${JSON.stringify(body.slice(0, 80))}`);
  });

  it('orden date asc y valores de cada columna', async () => {
    const { text } = await getCsv();
    const rows = parseCsv(text).filter((r) => !(r.length === 1 && r[0] === ''));
    assert.deepEqual(rows[0], HEADER);
    const data = rows.slice(1);
    assert.equal(data.length, 5);
    for (const r of data) assert.equal(r.length, 8, `fila con 8 columnas: ${JSON.stringify(r)}`);
    assert.deepEqual(
      data.map((r) => r[1]),
      ['2026-10-27', '2026-10-28', '2026-10-29', '2026-10-30', '2026-10-31']
    );
    const byId = Object.fromEntries(data.map((r) => [r[0], r]));
    const expectRow = (e) => [
      String(e.id), e.date, e.title, String(e.minutes), e.category, e.status, e.tags.join(';'), e.notes,
    ];
    for (const k of Object.keys(created)) {
      assert.deepEqual(byId[String(created[k].id)], expectRow(created[k]), k);
    }
  });

  it('tags unidos con ";"', async () => {
    const { text } = await getCsv();
    const rows = parseCsv(text);
    const row = rows.find((r) => r[0] === String(created.plain.id));
    assert.equal(row[6], 'a;b;c');
    const empty = rows.find((r) => r[0] === String(created.comma.id));
    assert.equal(empty[6], '');
  });

  it('escapado RFC 4180: comas, comillas y saltos de línea van entre comillas', async () => {
    const { text } = await getCsv();
    assert.ok(text.includes('"Uno, dos, tres"'), 'campo con coma entre comillas');
    assert.ok(text.includes('"Cat, con coma"'), 'categoría con coma entre comillas');
    assert.ok(text.includes('"Dijo ""hola"""'), 'comillas duplicadas y campo entre comillas');
    assert.ok(text.includes('"comillas ""dobles"" aquí"'));
    assert.ok(/"línea 1\nlínea 2\r\nlínea 3"/.test(text), 'salto de línea preservado dentro de comillas');
    // Un campo sin caracteres especiales no rompe el parseo y conserva su valor.
    const rows = parseCsv(text);
    const nl = rows.find((r) => r[0] === String(created.newline.id));
    assert.equal(nl[7], 'línea 1\nlínea 2\r\nlínea 3');
  });

  it('UTF-8 correcto en acentos', async () => {
    const { text } = await getCsv();
    const rows = parseCsv(text);
    const r = rows.find((x) => x[0] === String(created.accent.id));
    assert.equal(r[2], 'Ñandú café — acción');
    assert.equal(r[4], 'Reunión');
    assert.equal(r[6], 'ñ');
  });

  it('respeta from/to (inclusive)', async () => {
    const { res, text } = await getCsv('?from=2026-10-28&to=2026-10-30');
    assert.equal(res.status, 200);
    const rows = parseCsv(text).filter((r) => !(r.length === 1 && r[0] === ''));
    assert.deepEqual(rows[0], HEADER);
    assert.deepEqual(
      rows.slice(1).map((r) => r[0]),
      [created.comma.id, created.quote.id, created.plain.id].map(String)
    );
  });

  it('mismo día: orden estable por fecha (varias entradas el mismo día)', async () => {
    const extra = await srv.api('POST', '/api/entries', { date: '2026-10-27', title: 'Otra del 27' });
    assert.equal(extra.status, 201);
    const { text } = await getCsv('?to=2026-10-27');
    const rows = parseCsv(text).filter((r) => !(r.length === 1 && r[0] === '')).slice(1);
    assert.deepEqual(rows.map((r) => r[1]), ['2026-10-27', '2026-10-27']);
    assert.deepEqual(rows.map((r) => r[0]).sort(), [created.accent.id, extra.body.id].map(String).sort());
  });

  it('fechas de rango inválidas → 400', async () => {
    for (const qs of ['?from=ayer', '?to=2026-02-30']) {
      const { res } = await getCsv(qs);
      assert.equal(res.status, 400, qs);
    }
  });
});
