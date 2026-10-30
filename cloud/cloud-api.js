// Bitácora — versión en la nube (claude.ai).
// Implementa la misma API que server/app.js (window.bitacoraApi) sobre la base
// de datos del artifact. Cada persona guarda sus entradas en su espacio privado
// data/users/<id>. Sin acceso a la nube, guarda en este navegador.
// Se concatena después de public/core.js (ver cloud/build.mjs).

const LOCAL_KEY = 'bitacora.entradas';

class CloudApiError extends Error {
  constructor(message, status, details = []) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

const invalid = (details) => new CloudApiError('Datos inválidos', 400, details);
const notFound = () => new CloudApiError('No encontrado', 404);

function showMode(text) {
  const box = document.getElementById('modo');
  if (!box) return;
  box.textContent = text;
  box.hidden = !text;
}

const notifyChange = () => document.dispatchEvent(new Event('bitacora:cambio'));

// ---------- Almacenes ----------

async function connectCloud() {
  if (!window.claude?.use) return null;
  const [db, user] = await Promise.all([window.claude.use('db'), window.claude.use('user')]);
  if (!db || !user) return null;
  const uid = await user.id();
  if (!uid) return null;
  const col = db.collection(`data/users/${uid}`);
  const cache = new Map();

  await new Promise((resolve, reject) => {
    let first = true;
    const timer = setTimeout(() => { if (first) reject(new Error('timeout')); }, 15000);
    col.onSnapshot((snap) => {
      cache.clear();
      for (const d of snap.docs) cache.set(d.id, { ...d.data(), id: d.id });
      if (first) {
        first = false;
        clearTimeout(timer);
        resolve();
      } else {
        notifyChange();
      }
    }, (err) => {
      if (first) { clearTimeout(timer); reject(err); }
      else showMode('Se perdió la conexión con la nube. Recarga la página para seguir guardando.');
    });
  });

  return {
    all: () => [...cache.values()],
    get: (id) => cache.get(id) || null,
    async save(entry) {
      const { id, ...body } = entry;
      try {
        await col.doc(id).set(body);
      } catch (err) {
        if (err?.code === 'quota_exceeded') {
          throw new CloudApiError('La bitácora está llena: borra entradas antiguas para seguir.', 507);
        }
        throw new CloudApiError('No se pudo guardar en la nube. Inténtalo de nuevo.', 503);
      }
      cache.set(id, entry);
    },
    async remove(id) {
      try {
        await col.doc(id).delete();
      } catch {
        throw new CloudApiError('No se pudo borrar en la nube. Inténtalo de nuevo.', 503);
      }
      cache.delete(id);
    },
    newId: () => col.doc().id,
  };
}

function localStore() {
  let entries = [];
  try { entries = JSON.parse(localStorage.getItem(LOCAL_KEY) || '[]'); } catch { entries = []; }
  const persist = () => {
    try { localStorage.setItem(LOCAL_KEY, JSON.stringify(entries)); } catch { /* solo en memoria */ }
  };
  return {
    all: () => [...entries],
    get: (id) => entries.find((e) => e.id === id) || null,
    async save(entry) {
      entries = entries.filter((e) => e.id !== entry.id).concat(entry);
      persist();
    },
    async remove(id) {
      entries = entries.filter((e) => e.id !== id);
      persist();
    },
    newId: () => `l${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`,
  };
}

const storeReady = connectCloud()
  .catch(() => null)
  .then((cloud) => {
    if (cloud) return cloud;
    showMode('Modo sin conexión: la nube de Claude no está disponible aquí, así que las entradas se guardan solo en este navegador.');
    return localStore();
  });

// ---------- Rutas (mismo contrato que SPEC.md) ----------

function parseFilters(params, allowed) {
  const errors = [];
  const filters = {};
  for (const key of allowed) {
    let v = params.get(key);
    if (v == null) continue;
    if (key !== 'q') v = v.trim();
    if (v !== '') filters[key] = v;
  }
  for (const key of ['from', 'to']) {
    if (filters[key] !== undefined && !isValidDate(filters[key])) {
      errors.push(`El parámetro "${key}" debe ser una fecha válida YYYY-MM-DD`);
    }
  }
  if (filters.status !== undefined && !STATUSES.includes(filters.status)) {
    errors.push(`El parámetro "status" debe ser uno de: ${STATUSES.join(', ')}`);
  }
  if (errors.length) throw invalid(errors);
  return filters;
}

window.bitacoraApi = async function cloudApi(path, options = {}) {
  const store = await storeReady;
  const url = new URL(path, 'https://bitacora.local');
  const method = (options.method || 'GET').toUpperCase();
  const route = url.pathname.replace(/^\/api/, '');
  const match = route.match(/^\/entries\/([^/]+)$/);
  const id = match ? decodeURIComponent(match[1]) : null;

  if (method === 'GET' && route === '/entries') {
    return filterEntries(store.all(), parseFilters(url.searchParams, ['from', 'to', 'q', 'category', 'status', 'tag']), 'desc');
  }
  if (method === 'GET' && route === '/summary') {
    return summarize(filterEntries(store.all(), parseFilters(url.searchParams, ['from', 'to'])));
  }
  if (method === 'GET' && route === '/categories') {
    return listCategories(store.all());
  }
  if (method === 'GET' && id) {
    const entry = store.get(id);
    if (!entry) throw notFound();
    return entry;
  }
  if (method === 'POST' && route === '/entries') {
    const { value, errors } = validateEntry(options.body ?? {});
    if (errors.length) throw invalid(errors);
    const now = new Date().toISOString();
    const entry = { id: store.newId(), ...value, createdAt: now, updatedAt: now };
    await store.save(entry);
    return entry;
  }
  if (method === 'PUT' && id) {
    const current = store.get(id);
    if (!current) throw notFound();
    const { value, errors } = validateEntry(options.body ?? {});
    if (errors.length) throw invalid(errors);
    const entry = { id, ...value, createdAt: current.createdAt, updatedAt: new Date().toISOString() };
    await store.save(entry);
    return entry;
  }
  if (method === 'DELETE' && id) {
    if (!store.get(id)) throw notFound();
    await store.remove(id);
    return null;
  }
  throw notFound();
};

// Exportar CSV: el visor de claude.ai pide confirmación antes de guardar.
window.bitacoraExport = async function cloudExport({ from, to }) {
  const store = await storeReady;
  const params = new URLSearchParams();
  if (from) params.set('from', from);
  if (to) params.set('to', to);
  const entries = filterEntries(store.all(), parseFilters(params, ['from', 'to']), 'asc');
  const downloads = window.claude?.use ? await window.claude.use('downloads') : null;
  if (!downloads) throw new Error('la descarga de archivos no está disponible en esta vista');
  const filename = `bitacora${from ? `-${from}` : ''}${to ? `_${to}` : ''}.csv`;
  try {
    await downloads.save({ filename, data: toCSV(entries) });
    return true;
  } catch (err) {
    if (err?.code === 'declined') return false;
    if (err?.code === 'rate_limited') throw new Error('ya hay una descarga pendiente de confirmar');
    throw new Error('la descarga de archivos no está disponible en esta vista');
  }
};
