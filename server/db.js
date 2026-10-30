import { DatabaseSync } from 'node:sqlite';

const SCHEMA = `
  CREATE TABLE IF NOT EXISTS entries (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    date       TEXT    NOT NULL,
    title      TEXT    NOT NULL,
    notes      TEXT    NOT NULL DEFAULT '',
    minutes    INTEGER NOT NULL DEFAULT 0,
    category   TEXT    NOT NULL DEFAULT 'General',
    status     TEXT    NOT NULL DEFAULT 'completada',
    tags       TEXT    NOT NULL DEFAULT '[]',
    created_at TEXT    NOT NULL,
    updated_at TEXT    NOT NULL
  );
  CREATE INDEX IF NOT EXISTS idx_entries_date ON entries (date, id);
`;

// Convierte una fila de SQLite en la entrada pública (camelCase, tags como arreglo)
export function rowToEntry(row) {
  if (!row) return null;
  let tags = [];
  try {
    const parsed = JSON.parse(row.tags);
    if (Array.isArray(parsed)) tags = parsed;
  } catch {
    tags = [];
  }
  return {
    id: row.id,
    date: row.date,
    title: row.title,
    notes: row.notes,
    minutes: row.minutes,
    category: row.category,
    status: row.status,
    tags,
    createdAt: row.created_at,
    updatedAt: row.updated_at,
  };
}

/**
 * Abre la base de datos y devuelve un objeto con funciones de acceso.
 * Los filtros ya deben venir validados.
 */
export function openDatabase(dbPath = ':memory:') {
  const db = new DatabaseSync(dbPath);
  db.exec('PRAGMA foreign_keys = ON;');
  if (dbPath !== ':memory:') db.exec('PRAGMA journal_mode = WAL;');
  db.exec(SCHEMA);

  // Minúsculas con soporte Unicode (lower() de SQLite solo cubre ASCII)
  db.function('lower_u', { deterministic: true }, (s) =>
    s == null ? '' : String(s).toLocaleLowerCase('es')
  );

  const stmts = {
    getById: db.prepare('SELECT * FROM entries WHERE id = ?'),
    insert: db.prepare(`
      INSERT INTO entries (date, title, notes, minutes, category, status, tags, created_at, updated_at)
      VALUES (:date, :title, :notes, :minutes, :category, :status, :tags, :now, :now)
    `),
    update: db.prepare(`
      UPDATE entries
         SET date = :date, title = :title, notes = :notes, minutes = :minutes,
             category = :category, status = :status, tags = :tags, updated_at = :now
       WHERE id = :id
    `),
    remove: db.prepare('DELETE FROM entries WHERE id = ?'),
    categories: db.prepare('SELECT DISTINCT category FROM entries'),
  };

  // Construye la cláusula WHERE a partir de los filtros
  function buildWhere(filters = {}) {
    const clauses = [];
    const params = [];
    if (filters.from) { clauses.push('date >= ?'); params.push(filters.from); }
    if (filters.to) { clauses.push('date <= ?'); params.push(filters.to); }
    if (filters.q) {
      clauses.push('(instr(lower_u(title), ?) > 0 OR instr(lower_u(notes), ?) > 0)');
      const q = filters.q.toLocaleLowerCase('es');
      params.push(q, q);
    }
    if (filters.category) { clauses.push('category = ?'); params.push(filters.category); }
    if (filters.status) { clauses.push('status = ?'); params.push(filters.status); }
    if (filters.tag) {
      clauses.push('EXISTS (SELECT 1 FROM json_each(entries.tags) WHERE json_each.value = ?)');
      params.push(filters.tag);
    }
    return { where: clauses.length ? `WHERE ${clauses.join(' AND ')}` : '', params };
  }

  function toParams(data, now) {
    return {
      date: data.date,
      title: data.title,
      notes: data.notes,
      minutes: data.minutes,
      category: data.category,
      status: data.status,
      tags: JSON.stringify(data.tags),
      now,
    };
  }

  return {
    db,

    listEntries(filters = {}, order = 'desc') {
      const { where, params } = buildWhere(filters);
      const dir = order === 'asc' ? 'ASC' : 'DESC';
      const rows = db.prepare(`SELECT * FROM entries ${where} ORDER BY date ${dir}, id ${dir}`).all(...params);
      return rows.map(rowToEntry);
    },

    getEntry(id) {
      return rowToEntry(stmts.getById.get(id));
    },

    createEntry(data) {
      const now = new Date().toISOString();
      const { lastInsertRowid } = stmts.insert.run(toParams(data, now));
      return rowToEntry(stmts.getById.get(lastInsertRowid));
    },

    updateEntry(id, data) {
      const now = new Date().toISOString();
      const { changes } = stmts.update.run({ ...toParams(data, now), id });
      return changes ? rowToEntry(stmts.getById.get(id)) : null;
    },

    deleteEntry(id) {
      return stmts.remove.run(id).changes > 0;
    },

    listCategories() {
      // Orden alfabético en español (acentos y mayúsculas incluidos)
      const collator = new Intl.Collator('es', { sensitivity: 'base' });
      return stmts.categories.all().map((r) => r.category).sort((a, b) => collator.compare(a, b) || (a < b ? -1 : 1));
    },

    summary(filters = {}) {
      const { where, params } = buildWhere(filters);
      const totals = db.prepare(
        `SELECT COUNT(*) AS count, COALESCE(SUM(minutes), 0) AS minutes FROM entries ${where}`
      ).get(...params);
      const byDay = db.prepare(
        `SELECT date, COUNT(*) AS count, COALESCE(SUM(minutes), 0) AS minutes
           FROM entries ${where} GROUP BY date ORDER BY date ASC`
      ).all(...params).map((r) => ({ date: r.date, count: r.count, minutes: r.minutes }));
      const byCategory = db.prepare(
        `SELECT category, COUNT(*) AS count, COALESCE(SUM(minutes), 0) AS minutes
           FROM entries ${where} GROUP BY category ORDER BY minutes DESC, category ASC`
      ).all(...params).map((r) => ({ category: r.category, count: r.count, minutes: r.minutes }));
      const byStatus = { pendiente: 0, en_progreso: 0, completada: 0 };
      for (const r of db.prepare(
        `SELECT status, COUNT(*) AS count FROM entries ${where} GROUP BY status`
      ).all(...params)) {
        if (r.status in byStatus) byStatus[r.status] = r.count;
      }
      return {
        totalEntries: totals.count,
        totalMinutes: totals.minutes,
        byDay,
        byCategory,
        byStatus,
      };
    },

    close() {
      db.close();
    },
  };
}
