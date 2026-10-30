# Bitácora — Johny trabajo rayos

Bitácora de trabajo diario: registra actividades, tiempo dedicado, categoría, estado,
etiquetas y notas; filtra por fechas, consulta un resumen y exporta a CSV.

## Uso
```bash
npm install
npm start          # http://localhost:3000
```
Variables: `PORT` (3000) y `DB_PATH` (`./data/bitacora.db`). Requiere Node.js ≥ 22.5.

## Versión en la nube (claude.ai)
`npm run build:cloud` genera `dist/bitacora.html`, una sola página que se publica como
artifact en claude.ai. Usa la misma interfaz y las mismas reglas (`public/core.js`), pero
guarda las entradas en la base de datos privada de cada persona en claude.ai
(`cloud/cloud-api.js`) en lugar del servidor. Así se abre desde el móvil sin montar nada.

## Desarrollo
- `npm run dev` — reinicia al cambiar archivos.
- `npm test` — pruebas de la API (`node:test`).
- Contrato de la API y modelo de datos: [SPEC.md](SPEC.md).

## Estructura
- `server/` — API Express + SQLite (`node:sqlite`).
- `public/` — interfaz web (HTML/CSS/JS sin compilación).
- `cloud/` — adaptador y script de la versión en la nube.
- `test/` — pruebas.
