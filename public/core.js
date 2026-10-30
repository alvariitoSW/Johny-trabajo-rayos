// Bitácora — reglas compartidas entre el servidor y la versión en la nube.
// Sin dependencias: se importa desde server/ (Node) y desde el navegador.

export const STATUSES = ['pendiente', 'en_progreso', 'completada'];

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

// Escapado RFC 4180
export function csvField(value) {
  const s = value == null ? '' : String(value);
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

// CSV con BOM UTF-8 para que Excel muestre bien los acentos
export function toCSV(entries) {
  const header = ['id', 'date', 'title', 'minutes', 'category', 'status', 'tags', 'notes'];
  const lines = [header.join(',')];
  for (const e of entries) {
    lines.push([
      e.id, e.date, e.title, e.minutes, e.category, e.status, e.tags.join(';'), e.notes,
    ].map(csvField).join(','));
  }
  return '﻿' + lines.join('\r\n') + '\r\n';
}

// ---------- Consultas en memoria (versión en la nube) ----------
// Reproducen el comportamiento de server/db.js sobre un arreglo de entradas.

const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

export function filterEntries(entries, filters = {}, dir = 'desc') {
  const q = filters.q ? filters.q.toLowerCase() : '';
  const out = entries.filter((e) =>
    (!filters.from || e.date >= filters.from) &&
    (!filters.to || e.date <= filters.to) &&
    (!q || e.title.toLowerCase().includes(q) || e.notes.toLowerCase().includes(q)) &&
    (!filters.category || e.category === filters.category) &&
    (!filters.status || e.status === filters.status) &&
    (!filters.tag || e.tags.includes(filters.tag)));
  const sign = dir === 'asc' ? 1 : -1;
  return out.sort((a, b) => sign * (cmp(a.date, b.date) || cmp(a.createdAt, b.createdAt) || cmp(a.id, b.id)));
}

export function listCategories(entries) {
  const collator = new Intl.Collator('es', { sensitivity: 'base' });
  return [...new Set(entries.map((e) => e.category))]
    .sort((a, b) => collator.compare(a, b) || cmp(a, b));
}

export function summarize(entries) {
  const byDay = new Map();
  const byCategory = new Map();
  const byStatus = Object.fromEntries(STATUSES.map((s) => [s, 0]));
  let totalMinutes = 0;
  for (const e of entries) {
    totalMinutes += e.minutes;
    const d = byDay.get(e.date) || { date: e.date, count: 0, minutes: 0 };
    d.count += 1; d.minutes += e.minutes; byDay.set(e.date, d);
    const c = byCategory.get(e.category) || { category: e.category, count: 0, minutes: 0 };
    c.count += 1; c.minutes += e.minutes; byCategory.set(e.category, c);
    if (e.status in byStatus) byStatus[e.status] += 1;
  }
  return {
    totalEntries: entries.length,
    totalMinutes,
    byDay: [...byDay.values()].sort((a, b) => cmp(a.date, b.date)),
    byCategory: [...byCategory.values()].sort((a, b) => b.minutes - a.minutes || cmp(a.category, b.category)),
    byStatus,
  };
}
