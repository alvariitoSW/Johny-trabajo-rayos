import express from 'express';
import { fileURLToPath } from 'node:url';
import { openDatabase } from './db.js';

const PUBLIC_DIR = fileURLToPath(new URL('../public/', import.meta.url));

export const STATUSES = ['pendiente', 'en_progreso', 'completada'];

const NOT_FOUND = { error: 'No encontrado' };

class ValidationError extends Error {
  constructor(details) {
    super('Datos inválidos');
    this.details = details;
  }
}

// Fecha real del calendario en formato YYYY-MM-DD (rechaza 2026-02-30)
export function isValidDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [y, m, d] = value.split('-').map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  return dt.getUTCFullYear() === y && dt.getUTCMonth() === m - 1 && dt.getUTCDate() === d;
}

/**
 * Valida y normaliza el cuerpo de una entrada (POST y PUT).
 * Devuelve { value, errors } con todos los mensajes acumulados.
 */
export function validateEntry(body) {
  const errors = [];
  if (body === null || typeof body !== 'object' || Array.isArray(body)) {
    return { value: null, errors: ['El cuerpo debe ser un objeto JSON'] };
  }
  const value = {};

  // date
  if (body.date === undefined || body.date === null || body.date === '') {
    errors.push('La fecha es obligatoria');
  } else if (!isValidDate(body.date)) {
    errors.push('La fecha debe ser válida con formato YYYY-MM-DD');
  } else {
    value.date = body.date;
  }

  // title
  if (body.title === undefined || body.title === null) {
    errors.push('El título es obligatorio');
  } else if (typeof body.title !== 'string') {
    errors.push('El título debe ser texto');
  } else {
    const title = body.title.trim();
    if (title.length === 0) errors.push('El título es obligatorio');
    else if (title.length > 200) errors.push('El título no puede superar 200 caracteres');
    else value.title = title;
  }

  // notes
  if (body.notes === undefined || body.notes === null) {
    value.notes = '';
  } else if (typeof body.notes !== 'string') {
    errors.push('Las notas deben ser texto');
  } else if (body.notes.length > 5000) {
    errors.push('Las notas no pueden superar 5000 caracteres');
  } else {
    value.notes = body.notes;
  }

  // minutes
  if (body.minutes === undefined || body.minutes === null) {
    value.minutes = 0;
  } else if (typeof body.minutes !== 'number' || !Number.isInteger(body.minutes)) {
    errors.push('Los minutos deben ser un número entero');
  } else if (body.minutes < 0 || body.minutes > 1440) {
    errors.push('Los minutos deben estar entre 0 y 1440');
  } else {
    value.minutes = body.minutes;
  }

  // category
  if (body.category === undefined || body.category === null) {
    value.category = 'General';
  } else if (typeof body.category !== 'string') {
    errors.push('La categoría debe ser texto');
  } else {
    const category = body.category.trim();
    if (category.length > 50) errors.push('La categoría no puede superar 50 caracteres');
    else value.category = category || 'General';
  }

  // status
  if (body.status === undefined || body.status === null) {
    value.status = 'completada';
  } else if (!STATUSES.includes(body.status)) {
    errors.push(`El estado debe ser uno de: ${STATUSES.join(', ')}`);
  } else {
    value.status = body.status;
  }

  // tags
  if (body.tags === undefined || body.tags === null) {
    value.tags = [];
  } else if (!Array.isArray(body.tags)) {
    errors.push('Las etiquetas deben ser un arreglo de textos');
  } else {
    const tags = [];
    let tagErrors = false;
    body.tags.forEach((raw, i) => {
      if (typeof raw !== 'string') {
        errors.push(`La etiqueta ${i + 1} debe ser texto`);
        tagErrors = true;
        return;
      }
      const tag = raw.trim();
      if (tag.length === 0) {
        errors.push(`La etiqueta ${i + 1} no puede estar vacía`);
        tagErrors = true;
      } else if (tag.length > 30) {
        errors.push(`La etiqueta "${tag.slice(0, 30)}…" no puede superar 30 caracteres`);
        tagErrors = true;
      } else if (tags.includes(tag)) {
        errors.push(`La etiqueta "${tag}" está duplicada`);
        tagErrors = true;
      } else {
        tags.push(tag);
      }
    });
    if (body.tags.length > 10) {
      errors.push('No se permiten más de 10 etiquetas');
      tagErrors = true;
    }
    if (!tagErrors) value.tags = tags;
  }

  return { value: errors.length ? null : value, errors };
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

// Escapado RFC 4180
function csvField(value) {
  const s = value == null ? '' : String(value);
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
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
    const entries = store.listEntries(filters, 'asc');
    const header = ['id', 'date', 'title', 'minutes', 'category', 'status', 'tags', 'notes'];
    const lines = [header.join(',')];
    for (const e of entries) {
      lines.push([
        e.id, e.date, e.title, e.minutes, e.category, e.status, e.tags.join(';'), e.notes,
      ].map(csvField).join(','));
    }
    // BOM UTF-8 para que Excel muestre bien los acentos
    const csv = '﻿' + lines.join('\r\n') + '\r\n';
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
