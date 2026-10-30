import express from 'express';
import { fileURLToPath } from 'node:url';
import { openDatabase } from './db.js';
import { STATUSES, isValidDate, validateEntry, toCSV } from '../public/core.js';

export { STATUSES, isValidDate, validateEntry };

const PUBLIC_DIR = fileURLToPath(new URL('../public/', import.meta.url));

const NOT_FOUND = { error: 'No encontrado' };

class ValidationError extends Error {
  constructor(details) {
    super('Datos inválidos');
    this.details = details;
  }
}

// Lee y valida los filtros de la query (from, to, q, category, status, tag)
function parseFilters(query, allowed) {
  const errors = [];
  const filters = {};
  for (const key of allowed) {
    let v = query[key];
    if (v === undefined) continue;
    if (Array.isArray(v) || typeof v !== 'string') {
      errors.push(`El parámetro "${key}" no es válido`);
      continue;
    }
    if (key !== 'q') v = v.trim();
    if (v === '') continue; // vacío = sin filtro
    filters[key] = v;
  }
  for (const key of ['from', 'to']) {
    if (filters[key] !== undefined && !isValidDate(filters[key])) {
      errors.push(`El parámetro "${key}" debe ser una fecha válida YYYY-MM-DD`);
    }
  }
  if (filters.status !== undefined && !STATUSES.includes(filters.status)) {
    errors.push(`El parámetro "status" debe ser uno de: ${STATUSES.join(', ')}`);
  }
  if (errors.length) throw new ValidationError(errors);
  return filters;
}

// :id debe ser un entero positivo; si no, se trata como no encontrado
function parseId(raw) {
  if (!/^\d+$/.test(raw)) return null;
  const id = Number(raw);
  return Number.isSafeInteger(id) && id > 0 ? id : null;
}

export function createApp({ dbPath = ':memory:' } = {}) {
  const store = openDatabase(dbPath);
  const app = express();
  app.disable('x-powered-by');
  app.locals.store = store;

  const api = express.Router();
  api.use(express.json({ limit: '100kb' }));

  api.get('/health', (req, res) => {
    res.json({ status: 'ok' });
  });

  api.get('/entries', (req, res) => {
    const filters = parseFilters(req.query, ['from', 'to', 'q', 'category', 'status', 'tag']);
    res.json(store.listEntries(filters, 'desc'));
  });

  api.get('/entries/:id', (req, res) => {
    const id = parseId(req.params.id);
    const entry = id && store.getEntry(id);
    if (!entry) return res.status(404).json(NOT_FOUND);
    res.json(entry);
  });

  api.post('/entries', (req, res) => {
    const { value, errors } = validateEntry(req.body ?? {});
    if (errors.length) throw new ValidationError(errors);
    res.status(201).json(store.createEntry(value));
  });

  api.put('/entries/:id', (req, res) => {
    const id = parseId(req.params.id);
    if (!id || !store.getEntry(id)) return res.status(404).json(NOT_FOUND);
    const { value, errors } = validateEntry(req.body ?? {});
    if (errors.length) throw new ValidationError(errors);
    const entry = store.updateEntry(id, value);
    if (!entry) return res.status(404).json(NOT_FOUND);
    res.json(entry);
  });

  api.delete('/entries/:id', (req, res) => {
    const id = parseId(req.params.id);
    if (!id || !store.deleteEntry(id)) return res.status(404).json(NOT_FOUND);
    res.status(204).end();
  });

  api.get('/categories', (req, res) => {
    res.json(store.listCategories());
  });

  api.get('/summary', (req, res) => {
    const filters = parseFilters(req.query, ['from', 'to']);
    res.json(store.summary(filters));
  });

  api.get('/export.csv', (req, res) => {
    const filters = parseFilters(req.query, ['from', 'to']);
    const csv = toCSV(store.listEntries(filters, 'asc'));
    res.set('Content-Type', 'text/csv; charset=utf-8');
    res.set('Content-Disposition', 'attachment; filename="bitacora.csv"');
    res.send(csv);
  });

  // Ruta de API desconocida
  api.use((req, res) => {
    res.status(404).json(NOT_FOUND);
  });

  // Errores de la API: validación, JSON mal formado y otros
  api.use((err, req, res, next) => {
    if (err instanceof ValidationError) {
      return res.status(400).json({ error: 'Datos inválidos', details: err.details });
    }
    if (err.type === 'entity.parse.failed') {
      return res.status(400).json({ error: 'Datos inválidos', details: ['El cuerpo no es un JSON válido'] });
    }
    if (err.type === 'entity.too.large') {
      return res.status(413).json({ error: 'Datos inválidos', details: ['El cuerpo es demasiado grande'] });
    }
    if (err.status >= 400 && err.status < 500) {
      return res.status(err.status).json({ error: 'Datos inválidos', details: [err.message] });
    }
    console.error(err);
    res.status(500).json({ error: 'Error interno del servidor' });
  });

  app.use('/api', api);
  app.use(express.static(PUBLIC_DIR));

  return { app, db: store.db };
}
