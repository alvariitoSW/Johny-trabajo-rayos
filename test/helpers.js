// Utilidades compartidas para las pruebas de la API de Bitácora.
// Cada archivo de pruebas levanta su propia app con una BD en memoria.
import { createApp } from '../server/app.js';

/**
 * Arranca una app nueva con BD ':memory:' en un puerto libre.
 * @returns {Promise<{ base: string, api: Function, close: Function, db: any }>}
 */
export async function startServer() {
  const { app, db } = createApp({ dbPath: ':memory:' });
  const server = await new Promise((resolve, reject) => {
    const s = app.listen(0, (err) => (err ? reject(err) : resolve(s)));
    s.on('error', reject);
  });
  const { port } = server.address();
  const base = `http://127.0.0.1:${port}`;

  /**
   * Petición a la API. `body` se serializa como JSON salvo que `raw` sea true.
   * Devuelve { status, headers, body, text } con body parseado si es JSON.
   */
  async function api(method, path, body, { raw = false, headers = {} } = {}) {
    const init = { method, headers: { ...headers } };
    if (body !== undefined) {
      init.body = raw ? body : JSON.stringify(body);
      if (!init.headers['content-type']) init.headers['content-type'] = 'application/json';
    }
    const res = await fetch(base + path, init);
    const text = await res.text();
    let parsed;
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json') && text.length > 0) {
      try {
        parsed = JSON.parse(text);
      } catch {
        parsed = undefined;
      }
    }
    return { status: res.status, headers: res.headers, body: parsed, text };
  }

  async function close() {
    await new Promise((resolve) => {
      if (typeof server.closeAllConnections === 'function') server.closeAllConnections();
      server.close(() => resolve());
    });
    try {
      if (db && typeof db.close === 'function') db.close();
    } catch {
      // ya cerrada
    }
  }

  return { base, api, close, db };
}

/** Entrada mínima válida, con campos sobreescribibles. */
export function validEntry(overrides = {}) {
  return { date: '2026-10-30', title: 'Tarea de prueba', ...overrides };
}

/** Comprueba la forma estándar de error 400. */
export function assertValidationError(assert, res, msg = '') {
  assert.equal(res.status, 400, `esperaba 400 ${msg}; obtuvo ${res.status}: ${res.text}`);
  assert.ok(res.body && typeof res.body === 'object', `cuerpo JSON esperado ${msg}: ${res.text}`);
  assert.equal(res.body.error, 'Datos inválidos', `error ${msg}`);
  assert.ok(Array.isArray(res.body.details), `details debe ser arreglo ${msg}: ${res.text}`);
  assert.ok(res.body.details.length >= 1, `details no debe estar vacío ${msg}`);
  for (const d of res.body.details) assert.equal(typeof d, 'string', `cada detail es string ${msg}`);
}

/** Comprueba la forma estándar de error 404. */
export function assertNotFound(assert, res, msg = '') {
  assert.equal(res.status, 404, `esperaba 404 ${msg}; obtuvo ${res.status}: ${res.text}`);
  assert.deepEqual(res.body, { error: 'No encontrado' }, `cuerpo 404 ${msg}`);
}

/** Parser CSV RFC 4180 mínimo (soporta comillas, comillas dobles, saltos de línea embebidos, CRLF o LF). */
export function parseCsv(text) {
  if (text.charCodeAt(0) === 0xfeff) text = text.slice(1);
  const rows = [];
  let row = [];
  let field = '';
  let inQuotes = false;
  let i = 0;
  while (i < text.length) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') {
          field += '"';
          i += 2;
          continue;
        }
        inQuotes = false;
        i++;
        continue;
      }
      field += c;
      i++;
      continue;
    }
    if (c === '"') {
      inQuotes = true;
      i++;
    } else if (c === ',') {
      row.push(field);
      field = '';
      i++;
    } else if (c === '\r' && text[i + 1] === '\n') {
      row.push(field);
      rows.push(row);
      row = [];
      field = '';
      i += 2;
    } else if (c === '\n') {
      row.push(field);
      rows.push(row);
      row = [];
      field = '';
      i++;
    } else {
      field += c;
      i++;
    }
  }
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

export const ISO_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$/;
