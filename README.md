# Bitácora — Johny trabajo rayos

Bitácora de trabajo diario: registra actividades, tiempo dedicado, categoría, estado,
etiquetas y notas; filtra por fechas, consulta un resumen y exporta a CSV.

## Uso
```bash
npm install
npm start          # http://localhost:3000
```
Variables: `PORT` (3000) y `DB_PATH` (`./data/bitacora.db`). Requiere Node.js ≥ 22.5.

## Desarrollo
- `npm run dev` — reinicia al cambiar archivos.
- `npm test` — pruebas de la API (`node:test`).
- Contrato de la API y modelo de datos: [SPEC.md](SPEC.md).

## Estructura
- `server/` — API Express + SQLite (`node:sqlite`).
- `public/` — interfaz web (HTML/CSS/JS sin compilación).
- `test/` — pruebas.
