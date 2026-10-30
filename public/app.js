// Bitácora — frontend (vanilla JS, ES module)

const $ = (sel, root = document) => root.querySelector(sel);

const STATUS_LABELS = {
  pendiente: 'Pendiente',
  en_progreso: 'En progreso',
  completada: 'Completada',
};

// ---------- Fechas (siempre locales, nunca UTC) ----------

const pad = (n) => String(n).padStart(2, '0');

function toISODate(d) {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

function parseISODate(s) {
  const [y, m, d] = s.split('-').map(Number);
  return new Date(y, m - 1, d);
}

function todayISO() {
  return toISODate(new Date());
}

function addDays(d, n) {
  const r = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  r.setDate(r.getDate() + n);
  return r;
}

function rangeFor(kind) {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  switch (kind) {
    case 'hoy':
      return { from: toISODate(today), to: toISODate(today) };
    case 'semana': {
      const dow = (today.getDay() + 6) % 7; // lunes = 0
      const monday = addDays(today, -dow);
      return { from: toISODate(monday), to: toISODate(addDays(monday, 6)) };
    }
    case 'mes': {
      const first = new Date(today.getFullYear(), today.getMonth(), 1);
      const last = new Date(today.getFullYear(), today.getMonth() + 1, 0);
      return { from: toISODate(first), to: toISODate(last) };
    }
    default:
      return { from: '', to: '' };
  }
}

const fmtLongDay = new Intl.DateTimeFormat('es-ES', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
const fmtShortDay = new Intl.DateTimeFormat('es-ES', { day: 'numeric', month: 'short' });
const fmtDayWithWeekday = new Intl.DateTimeFormat('es-ES', { weekday: 'short', day: 'numeric', month: 'short' });

const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

function dayHeading(iso) {
  const today = todayISO();
  const yesterday = toISODate(addDays(new Date(), -1));
  const long = fmtLongDay.format(parseISODate(iso));
  if (iso === today) return `Hoy · ${long}`;
  if (iso === yesterday) return `Ayer · ${long}`;
  return cap(long);
}

function formatMinutes(total) {
  const m = Math.max(0, Math.round(Number(total) || 0));
  const h = Math.floor(m / 60);
  const r = m % 60;
  if (h === 0) return `${r} min`;
  if (r === 0) return `${h} h`;
  return `${h} h ${r} min`;
}

// ---------- DOM helpers (sin innerHTML con datos) ----------

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === 'class') node.className = v;
    else if (k === 'text') node.textContent = v;
    else if (k === 'style') Object.assign(node.style, v);
    else if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v === true ? '' : String(v));
  }
  for (const c of children.flat()) {
    if (c == null || c === false) continue;
    node.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return node;
}

let toastTimer;
function toast(msg) {
  const t = $('#toast');
  t.textContent = msg;
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.hidden = true; }, 2600);
}

// ---------- API ----------

class ApiError extends Error {
  constructor(message, status, details = []) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

async function httpApi(path, options = {}) {
  const opts = { ...options, headers: { Accept: 'application/json', ...(options.headers || {}) } };
  if (opts.body !== undefined && typeof opts.body !== 'string') {
    opts.body = JSON.stringify(opts.body);
    opts.headers['Content-Type'] = 'application/json';
  }
  let res;
  try {
    res = await fetch(path, opts);
  } catch {
    throw new ApiError('No se pudo conectar con el servidor.', 0);
  }
  if (res.status === 204) return null;
  let data = null;
  const text = await res.text();
  if (text) {
    try { data = JSON.parse(text); } catch { data = null; }
  }
  if (!res.ok) {
    const msg = (data && data.error) || `Error ${res.status}`;
    const details = data && Array.isArray(data.details) ? data.details : [];
    throw new ApiError(msg, res.status, details);
  }
  return data;
}

// La versión en la nube (claude.ai) define window.bitacoraApi con la misma interfaz.
function api(path, options) {
  return (window.bitacoraApi || httpApi)(path, options);
}

function qs(params) {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== '' && v != null) sp.set(k, v);
  }
  const s = sp.toString();
  return s ? `?${s}` : '';
}

// ---------- Estado ----------

const state = {
  filters: { ...rangeFor('mes'), q: '', category: '', status: '' },
  entries: [],
  categories: [],
};

let loadSeq = 0;

// ---------- Formularios de entrada ----------

function parseTags(str) {
  const seen = new Set();
  const out = [];
  for (const raw of String(str || '').split(',')) {
    const t = raw.trim();
    if (!t) continue;
    const key = t.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(t);
  }
  return out;
}

function readEntryForm(form) {
  const f = form.elements;
  const hoursRaw = f.hours.value.trim();
  const minsRaw = f.minutes.value.trim();
  const clientErrors = [];
  const hours = hoursRaw === '' ? 0 : Number(hoursRaw);
  const mins = minsRaw === '' ? 0 : Number(minsRaw);
  if (!Number.isFinite(hours) || hours < 0 || !Number.isInteger(hours)) clientErrors.push('Las horas deben ser un número entero no negativo.');
  if (!Number.isFinite(mins) || mins < 0 || !Number.isInteger(mins)) clientErrors.push('Los minutos deben ser un número entero no negativo.');
  const payload = {
    date: f.date.value,
    title: f.title.value.trim(),
    notes: f.notes.value,
    minutes: Math.round(hours * 60 + mins),
    category: f.category.value.trim() || 'General',
    status: f.status.value,
    tags: parseTags(f.tags.value),
  };
  if (!payload.title) clientErrors.push('El título es obligatorio.');
  if (!payload.date) clientErrors.push('La fecha es obligatoria.');
  if (payload.minutes > 1440) clientErrors.push('El tiempo no puede superar 24 h (1440 min).');
  return { payload, clientErrors };
}

function fillEntryForm(form, entry) {
  const f = form.elements;
  f.date.value = entry.date;
  f.title.value = entry.title;
  const m = Number(entry.minutes) || 0;
  f.hours.value = Math.floor(m / 60) || '';
  f.minutes.value = m % 60 || (m === 0 ? '' : '0');
  f.category.value = entry.category || '';
  f.status.value = entry.status || 'completada';
  f.tags.value = (entry.tags || []).join(', ');
  f.notes.value = entry.notes || '';
}

function showErrors(box, form, messages, title = 'Revisa los datos:') {
  box.replaceChildren();
  form.querySelectorAll('[aria-invalid]').forEach((n) => n.removeAttribute('aria-invalid'));
  if (!messages || messages.length === 0) {
    box.hidden = true;
    return;
  }
  box.append(el('p', { text: title }), el('ul', {}, messages.map((m) => el('li', { text: m }))));
  box.hidden = false;
  // Marca campos con error cuando el mensaje los menciona.
  const fieldWords = {
    title: ['title', 'título', 'titulo'],
    date: ['date', 'fecha'],
    minutes: ['minutes', 'minutos', 'tiempo'],
    category: ['category', 'categoría', 'categoria'],
    tags: ['tags', 'tag', 'etiqueta'],
    notes: ['notes', 'notas'],
  };
  const text = messages.join(' ').toLowerCase();
  for (const [name, words] of Object.entries(fieldWords)) {
    if (words.some((w) => text.includes(w)) && form.elements[name]) {
      form.elements[name].setAttribute('aria-invalid', 'true');
    }
  }
}

function clearErrors(box, form) { showErrors(box, form, []); }

// ---------- Nueva entrada ----------

const formNueva = $('#form-nueva');
const errNueva = $('#n-errors');

function resetNewForm() {
  formNueva.reset();
  formNueva.elements.date.value = todayISO();
  formNueva.elements.status.value = 'completada';
}

formNueva.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const { payload, clientErrors } = readEntryForm(formNueva);
  if (clientErrors.length) {
    showErrors(errNueva, formNueva, clientErrors);
    return;
  }
  const btn = formNueva.querySelector('button[type="submit"]');
  btn.disabled = true;
  try {
    await api('/api/entries', { method: 'POST', body: payload });
    clearErrors(errNueva, formNueva);
    const keepDate = formNueva.elements.date.value;
    const keepCat = formNueva.elements.category.value;
    resetNewForm();
    formNueva.elements.date.value = keepDate;
    formNueva.elements.category.value = keepCat;
    formNueva.elements.title.focus();
    toast('Entrada agregada');
    await loadAll();
  } catch (err) {
    showErrors(errNueva, formNueva, err.details && err.details.length ? err.details : [err.message]);
  } finally {
    btn.disabled = false;
  }
});

// ---------- Edición ----------

const dlg = $('#dlg-editar');
const formEditar = $('#form-editar');
const errEditar = $('#e-errors');
let editingId = null;

function openEdit(entry) {
  editingId = entry.id;
  clearErrors(errEditar, formEditar);
  fillEntryForm(formEditar, entry);
  dlg.showModal();
  formEditar.elements.title.focus();
}

$('#btn-cancelar').addEventListener('click', () => dlg.close());

formEditar.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  if (editingId == null) return;
  const { payload, clientErrors } = readEntryForm(formEditar);
  if (clientErrors.length) {
    showErrors(errEditar, formEditar, clientErrors);
    return;
  }
  const btn = formEditar.querySelector('button[type="submit"]');
  btn.disabled = true;
  try {
    await api(`/api/entries/${encodeURIComponent(editingId)}`, { method: 'PUT', body: payload });
    dlg.close();
    toast('Cambios guardados');
    await loadAll();
  } catch (err) {
    if (err.status === 404) {
      dlg.close();
      toast('La entrada ya no existe');
      await loadAll();
    } else {
      showErrors(errEditar, formEditar, err.details && err.details.length ? err.details : [err.message]);
    }
  } finally {
    btn.disabled = false;
  }
});

dlg.addEventListener('close', () => { editingId = null; });

// ---------- Borrado ----------

const dlgBorrar = $('#dlg-borrar');
let deleting = null;

function deleteEntry(entry) {
  deleting = entry;
  $('#borrar-nombre').textContent = `«${entry.title}»`;
  dlgBorrar.showModal();
}

$('#btn-borrar-cancelar').addEventListener('click', () => dlgBorrar.close());
dlgBorrar.addEventListener('close', () => { deleting = null; });

$('#btn-borrar-confirmar').addEventListener('click', async () => {
  const entry = deleting;
  dlgBorrar.close();
  if (!entry) return;
  try {
    await api(`/api/entries/${encodeURIComponent(entry.id)}`, { method: 'DELETE' });
    toast('Entrada borrada');
  } catch (err) {
    if (err.status !== 404) {
      toast(`No se pudo borrar: ${err.message}`);
      return;
    }
  }
  await loadAll();
});

// ---------- Filtros ----------

const formFiltros = $('#form-filtros');
const chips = [...document.querySelectorAll('[data-range]')];

function syncFilterInputs() {
  const f = formFiltros.elements;
  f.from.value = state.filters.from;
  f.to.value = state.filters.to;
  f.q.value = state.filters.q;
  f.status.value = state.filters.status;
  f.category.value = state.filters.category;
}

function updateChips() {
  const { from, to } = state.filters;
  for (const chip of chips) {
    const r = rangeFor(chip.dataset.range);
    chip.setAttribute('aria-pressed', String(r.from === from && r.to === to));
  }
}

function rangeText() {
  const { from, to } = state.filters;
  if (!from && !to) return '· todo el historial';
  if (from && to && from === to) return `· ${fmtDayWithWeekday.format(parseISODate(from))}`;
  const a = from ? fmtShortDay.format(parseISODate(from)) : 'inicio';
  const b = to ? fmtShortDay.format(parseISODate(to)) : 'hoy en adelante';
  return `· ${a} – ${b}`;
}

function updateExportLink() {
  const { from, to } = state.filters;
  $('#btn-export').href = `/api/export.csv${qs({ from, to })}`;
}

for (const chip of chips) {
  chip.addEventListener('click', () => {
    Object.assign(state.filters, rangeFor(chip.dataset.range));
    syncFilterInputs();
    loadAll();
  });
}

let qTimer;
formFiltros.addEventListener('input', (ev) => {
  const t = ev.target;
  if (!t.name) return;
  if (t.name === 'q') {
    state.filters.q = t.value;
    clearTimeout(qTimer);
    qTimer = setTimeout(loadAll, 250);
    return;
  }
  if (t.name === 'from' || t.name === 'to') {
    // Solo aplica fechas completas o vacías.
    if (t.value && !/^\d{4}-\d{2}-\d{2}$/.test(t.value)) return;
  }
  state.filters[t.name] = t.value;
  loadAll();
});
formFiltros.addEventListener('submit', (ev) => ev.preventDefault());

$('#btn-export').addEventListener('click', async (ev) => {
  if (!window.bitacoraExport) return; // servidor: el enlace descarga el CSV
  ev.preventDefault();
  const { from, to } = state.filters;
  try {
    if (await window.bitacoraExport({ from, to })) toast('CSV exportado');
  } catch (err) {
    toast(`No se pudo exportar: ${err.message}`);
  }
});

// Cambios hechos desde otro dispositivo (versión en la nube)
document.addEventListener('bitacora:cambio', () => loadAll());

$('#btn-limpiar').addEventListener('click', () => {
  state.filters = { ...rangeFor('mes'), q: '', category: '', status: '' };
  syncFilterInputs();
  loadAll();
});

// ---------- Render: categorías ----------

function renderCategories() {
  const dl = $('#lista-categorias');
  dl.replaceChildren(...state.categories.map((c) => el('option', { value: c })));
  const sel = formFiltros.elements.category;
  const current = state.filters.category;
  const opts = [el('option', { value: '', text: 'Todas' })];
  const cats = [...state.categories];
  if (current && !cats.includes(current)) cats.push(current);
  for (const c of cats) opts.push(el('option', { value: c, text: c }));
  sel.replaceChildren(...opts);
  sel.value = current;
}

// ---------- Render: resumen ----------

function renderSummary(summary) {
  const s = summary || { totalEntries: 0, totalMinutes: 0, byDay: [], byCategory: [], byStatus: {} };
  const bs = s.byStatus || {};
  $('#s-total').textContent = String(s.totalEntries || 0);
  $('#s-tiempo').textContent = formatMinutes(s.totalMinutes);
  $('#s-completadas').textContent = String(bs.completada || 0);
  $('#s-pendientes').textContent = String((bs.pendiente || 0) + (bs.en_progreso || 0));
  $('#rango-texto').textContent = rangeText();
  renderDayChart(s.byDay || []);
  renderCategoryChart(s.byCategory || []);
}

function renderDayChart(byDay) {
  const box = $('#chart-dias');
  box.replaceChildren();
  // Completa los días vacíos cuando el rango es acotado y razonable.
  const map = new Map(byDay.map((d) => [d.date, d]));
  let days = [];
  const { from, to } = state.filters;
  if (from && to && from <= to) {
    const start = parseISODate(from);
    const end = parseISODate(to);
    const span = Math.round((end - start) / 86400000) + 1;
    if (span <= 62) {
      for (let i = 0; i < span; i++) {
        const iso = toISODate(addDays(start, i));
        days.push(map.get(iso) || { date: iso, count: 0, minutes: 0 });
      }
    }
  }
  if (days.length === 0) days = [...byDay];
  if (days.length === 0 || days.every((d) => !d.minutes && !d.count)) {
    box.append(el('p', { class: 'chart-empty', text: 'Sin datos en este rango.' }));
    return;
  }
  const max = Math.max(1, ...days.map((d) => d.minutes || 0));
  const chart = el('div', { class: 'day-chart', role: 'list', 'aria-label': 'Minutos por día' });
  for (const d of days) {
    const label = `${fmtDayWithWeekday.format(parseISODate(d.date))}: ${formatMinutes(d.minutes)}, ${d.count} ${d.count === 1 ? 'entrada' : 'entradas'}`;
    const pct = d.minutes ? Math.max(2, (d.minutes / max) * 100) : 0;
    chart.append(
      el('div', { class: 'day-col', role: 'listitem', title: label },
        el('span', { class: 'sr-only', text: label }),
        pct ? el('div', { class: 'day-bar', style: { height: `${pct}%` } }) : null,
      ),
    );
  }
  box.append(chart);
  box.append(
    el('div', { class: 'day-axis', 'aria-hidden': 'true' },
      el('span', { text: fmtShortDay.format(parseISODate(days[0].date)) }),
      el('span', { text: `máx. ${formatMinutes(max)}` }),
      el('span', { text: fmtShortDay.format(parseISODate(days[days.length - 1].date)) }),
    ),
  );
}

function renderCategoryChart(byCategory) {
  const box = $('#chart-categorias');
  box.replaceChildren();
  if (!byCategory.length) {
    box.append(el('p', { class: 'chart-empty', text: 'Sin datos en este rango.' }));
    return;
  }
  const max = Math.max(1, ...byCategory.map((c) => c.minutes || 0));
  const list = el('ul', { class: 'cat-list' });
  for (const c of byCategory) {
    const pct = c.minutes ? Math.max(2, (c.minutes / max) * 100) : 0;
    list.append(
      el('li', { class: 'cat-row' },
        el('span', { class: 'cat-name', text: c.category, title: c.category }),
        el('span', { class: 'cat-value', text: `${formatMinutes(c.minutes)} · ${c.count}` }),
        el('div', { class: 'cat-track', 'aria-hidden': 'true' },
          el('div', { class: 'cat-bar', style: { width: `${pct}%` } }),
        ),
      ),
    );
  }
  box.append(list);
}

// ---------- Render: lista ----------

function renderEntry(entry) {
  const meta = el('div', { class: 'entry-meta' },
    el('span', { class: 'badge badge-cat', text: entry.category || 'General' }),
    el('span', { class: `badge status-${entry.status}`, text: STATUS_LABELS[entry.status] || entry.status }),
    (entry.tags || []).map((t) => el('span', { class: 'tag', text: `#${t}` })),
  );
  return el('li', { class: 'entry' },
    el('div', { class: 'entry-top' },
      el('h4', { class: 'entry-title', text: entry.title }),
      el('span', { class: 'entry-time', text: formatMinutes(entry.minutes) }),
    ),
    meta,
    entry.notes ? el('p', { class: 'entry-notes', text: entry.notes }) : null,
    el('div', { class: 'entry-actions' },
      el('button', { type: 'button', class: 'icon-btn', 'aria-label': `Editar «${entry.title}»`, onclick: () => openEdit(entry) }, 'Editar'),
      el('button', { type: 'button', class: 'icon-btn danger', 'aria-label': `Borrar «${entry.title}»`, onclick: () => deleteEntry(entry) }, 'Borrar'),
    ),
  );
}

function renderList() {
  const container = $('#dias');
  container.replaceChildren();
  const entries = state.entries;
  $('#vacio').hidden = entries.length > 0;
  const total = entries.reduce((a, e) => a + (Number(e.minutes) || 0), 0);
  $('#lista-conteo').textContent = entries.length
    ? `${entries.length} ${entries.length === 1 ? 'entrada' : 'entradas'} · ${formatMinutes(total)}`
    : '';

  // Agrupa por fecha preservando el orden (date desc) del servidor.
  const groups = new Map();
  for (const e of entries) {
    if (!groups.has(e.date)) groups.set(e.date, []);
    groups.get(e.date).push(e);
  }
  const dates = [...groups.keys()].sort((a, b) => (a < b ? 1 : a > b ? -1 : 0));
  for (const date of dates) {
    const items = groups.get(date);
    const mins = items.reduce((a, e) => a + (Number(e.minutes) || 0), 0);
    const headId = `dia-${date}`;
    container.append(
      el('section', { class: 'day-group', 'aria-labelledby': headId },
        el('div', { class: 'day-head' },
          el('h3', { id: headId, text: dayHeading(date) }),
          el('span', { class: 'day-total', text: `${formatMinutes(mins)} · ${items.length} ${items.length === 1 ? 'entrada' : 'entradas'}` }),
        ),
        el('ul', { class: 'entries' }, items.map(renderEntry)),
      ),
    );
  }
}

// ---------- Carga ----------

async function loadAll() {
  const seq = ++loadSeq;
  updateChips();
  updateExportLink();
  $('#rango-texto').textContent = rangeText();
  const { from, to, q, category, status } = state.filters;
  const errBox = $('#load-error');
  try {
    const [entries, summary, categories] = await Promise.all([
      api(`/api/entries${qs({ from, to, q: q.trim(), category, status })}`),
      api(`/api/summary${qs({ from, to })}`),
      api('/api/categories'),
    ]);
    if (seq !== loadSeq) return;
    errBox.hidden = true;
    state.entries = Array.isArray(entries) ? entries : [];
    state.categories = Array.isArray(categories) ? categories : [];
    renderCategories();
    renderSummary(summary);
    renderList();
  } catch (err) {
    if (seq !== loadSeq) return;
    const extra = err.details && err.details.length ? ` (${err.details.join('; ')})` : '';
    errBox.textContent = `No se pudieron cargar los datos: ${err.message}${extra}`;
    errBox.hidden = false;
  }
}

// ---------- Inicio ----------

function init() {
  const hoyTexto = cap(fmtLongDay.format(new Date()));
  $('#hoy-texto').textContent = hoyTexto;
  const timeEl = $('#hoy-texto');
  timeEl.setAttribute('title', todayISO());
  resetNewForm();
  syncFilterInputs();
  loadAll();
}

init();
