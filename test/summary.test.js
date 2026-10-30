// Pruebas de /api/categories y /api/summary (según SPEC.md).
import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { startServer } from './helpers.js';

let srv;
before(async () => {
  srv = await startServer();
});
after(async () => {
  await srv.close();
});

const post = async (payload) => {
  const res = await srv.api('POST', '/api/entries', payload);
  assert.equal(res.status, 201, res.text);
  return res.body;
};

describe('summary y categorías con BD vacía', () => {
  it('GET /api/categories → [] sin entradas', async () => {
    const res = await srv.api('GET', '/api/categories');
    assert.equal(res.status, 200);
    assert.deepEqual(res.body, []);
  });

  it('GET /api/summary vacío → ceros y byStatus con las 3 claves', async () => {
    const res = await srv.api('GET', '/api/summary');
    assert.equal(res.status, 200, res.text);
    assert.deepEqual(res.body, {
      totalEntries: 0,
      totalMinutes: 0,
      byDay: [],
      byCategory: [],
      byStatus: { pendiente: 0, en_progreso: 0, completada: 0 },
    });
  });
});

describe('con datos', () => {
  let deleted;
  before(async () => {
    await post({ date: '2026-10-30', title: 'A', minutes: 60, category: 'Desarrollo', status: 'completada' });
    await post({ date: '2026-10-28', title: 'B', minutes: 30, category: 'Reuniones', status: 'pendiente' });
    await post({ date: '2026-10-30', title: 'C', minutes: 40, category: 'Desarrollo', status: 'en_progreso' });
    await post({ date: '2026-10-29', title: 'D', minutes: 5, status: 'completada' }); // General
    await post({ date: '2026-11-02', title: 'E', minutes: 100, category: 'Admin', status: 'completada' });
    await post({ date: '2026-10-29', title: 'F', category: 'Reuniones', status: 'pendiente' }); // 0 minutos
    deleted = await post({ date: '2026-10-29', title: 'G', minutes: 999, category: 'Borrada' });
    const del = await srv.api('DELETE', `/api/entries/${deleted.id}`);
    assert.equal(del.status, 204);
  });

  describe('GET /api/categories', () => {
    it('categorías distintas usadas, orden alfabético, sin las de entradas borradas', async () => {
      const res = await srv.api('GET', '/api/categories');
      assert.equal(res.status, 200);
      assert.match(res.headers.get('content-type') || '', /application\/json/);
      assert.deepEqual(res.body, ['Admin', 'Desarrollo', 'General', 'Reuniones']);
    });

    it('refleja cambios tras PUT', async () => {
      const e = await post({ date: '2026-10-01', title: 'tmp', category: 'Zeta' });
      let res = await srv.api('GET', '/api/categories');
      assert.deepEqual(res.body, ['Admin', 'Desarrollo', 'General', 'Reuniones', 'Zeta']);
      const put = await srv.api('PUT', `/api/entries/${e.id}`, { date: '2026-10-01', title: 'tmp', category: 'Admin' });
      assert.equal(put.status, 200, put.text);
      res = await srv.api('GET', '/api/categories');
      assert.deepEqual(res.body, ['Admin', 'Desarrollo', 'General', 'Reuniones']);
      assert.equal((await srv.api('DELETE', `/api/entries/${e.id}`)).status, 204);
    });
  });

  describe('GET /api/summary', () => {
    it('forma exacta de la respuesta', async () => {
      const res = await srv.api('GET', '/api/summary');
      assert.equal(res.status, 200, res.text);
      assert.match(res.headers.get('content-type') || '', /application\/json/);
      assert.deepEqual(
        Object.keys(res.body).sort(),
        ['byCategory', 'byDay', 'byStatus', 'totalEntries', 'totalMinutes']
      );
      for (const d of res.body.byDay) assert.deepEqual(Object.keys(d).sort(), ['count', 'date', 'minutes']);
      for (const c of res.body.byCategory) assert.deepEqual(Object.keys(c).sort(), ['category', 'count', 'minutes']);
      assert.deepEqual(Object.keys(res.body.byStatus).sort(), ['completada', 'en_progreso', 'pendiente']);
    });

    it('totales, byDay (date asc), byCategory (minutes desc), byStatus — sin rango', async () => {
      const res = await srv.api('GET', '/api/summary');
      assert.equal(res.status, 200, res.text);
      const s = res.body;
      assert.equal(s.totalEntries, 6);
      assert.equal(s.totalMinutes, 235);
      assert.deepEqual(
        s.byDay.filter((d) => d.count > 0),
        [
          { date: '2026-10-28', count: 1, minutes: 30 },
          { date: '2026-10-29', count: 2, minutes: 5 },
          { date: '2026-10-30', count: 2, minutes: 100 },
          { date: '2026-11-02', count: 1, minutes: 100 },
        ]
      );
      const dates = s.byDay.map((d) => d.date);
      assert.deepEqual(dates, [...dates].sort(), 'byDay en orden date asc');
      // Admin y Desarrollo empatan en 100 min: el orden entre ellos no está especificado.
      const mins = s.byCategory.map((c) => c.minutes);
      assert.deepEqual(mins, [...mins].sort((a, b) => b - a), 'byCategory en orden minutes desc');
      const byName = Object.fromEntries(s.byCategory.map((c) => [c.category, c]));
      assert.deepEqual(byName, {
        Admin: { category: 'Admin', count: 1, minutes: 100 },
        Desarrollo: { category: 'Desarrollo', count: 2, minutes: 100 },
        Reuniones: { category: 'Reuniones', count: 2, minutes: 30 },
        General: { category: 'General', count: 1, minutes: 5 },
      });
      assert.equal(s.byCategory.length, 4);
      assert.deepEqual(s.byStatus, { pendiente: 2, en_progreso: 1, completada: 3 });
    });

    it('respeta from/to (inclusive) y sigue reportando las 3 claves de byStatus', async () => {
      const res = await srv.api('GET', '/api/summary?from=2026-10-29&to=2026-10-30');
      assert.equal(res.status, 200, res.text);
      const s = res.body;
      assert.equal(s.totalEntries, 4);
      assert.equal(s.totalMinutes, 105);
      assert.deepEqual(
        s.byDay.filter((d) => d.count > 0),
        [
          { date: '2026-10-29', count: 2, minutes: 5 },
          { date: '2026-10-30', count: 2, minutes: 100 },
        ]
      );
      for (const d of s.byDay) {
        assert.ok(d.date >= '2026-10-29' && d.date <= '2026-10-30', `byDay fuera de rango: ${d.date}`);
      }
      assert.deepEqual(s.byCategory, [
        { category: 'Desarrollo', count: 2, minutes: 100 },
        { category: 'General', count: 1, minutes: 5 },
        { category: 'Reuniones', count: 1, minutes: 0 },
      ]);
      assert.deepEqual(s.byStatus, { pendiente: 1, en_progreso: 1, completada: 2 });
    });

    it('solo from', async () => {
      const res = await srv.api('GET', '/api/summary?from=2026-10-30');
      assert.equal(res.status, 200, res.text);
      assert.equal(res.body.totalEntries, 3);
      assert.equal(res.body.totalMinutes, 200);
      assert.deepEqual(res.body.byStatus, { pendiente: 0, en_progreso: 1, completada: 2 });
    });

    it('solo to', async () => {
      const res = await srv.api('GET', '/api/summary?to=2026-10-28');
      assert.equal(res.status, 200, res.text);
      assert.equal(res.body.totalEntries, 1);
      assert.equal(res.body.totalMinutes, 30);
      assert.deepEqual(res.body.byCategory, [{ category: 'Reuniones', count: 1, minutes: 30 }]);
    });

    it('rango sin entradas → ceros', async () => {
      const res = await srv.api('GET', '/api/summary?from=2020-01-01&to=2020-01-31');
      assert.equal(res.status, 200, res.text);
      assert.equal(res.body.totalEntries, 0);
      assert.equal(res.body.totalMinutes, 0);
      assert.deepEqual(res.body.byDay.filter((d) => d.count > 0), []);
      assert.deepEqual(res.body.byCategory, []);
      assert.deepEqual(res.body.byStatus, { pendiente: 0, en_progreso: 0, completada: 0 });
    });

    it('fechas de rango inválidas → 400', async () => {
      for (const qs of ['from=ayer', 'to=2026-02-30']) {
        const res = await srv.api('GET', `/api/summary?${qs}`);
        assert.equal(res.status, 400, `${qs}: ${res.status} ${res.text}`);
      }
    });
  });
});
