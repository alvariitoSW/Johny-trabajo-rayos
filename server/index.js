import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { createApp } from './app.js';

const PORT = Number(process.env.PORT) || 3000;
const DB_PATH = process.env.DB_PATH || './data/bitacora.db';

// Crea la carpeta de datos si hace falta
if (DB_PATH !== ':memory:') mkdirSync(dirname(resolve(DB_PATH)), { recursive: true });

const { app, db } = createApp({ dbPath: DB_PATH });

const server = app.listen(PORT, () => {
  console.log(`Bitácora escuchando en http://localhost:${PORT}`);
});

// Cierre ordenado
function shutdown() {
  server.close(() => {
    db.close();
    process.exit(0);
  });
}
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
