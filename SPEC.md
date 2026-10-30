# Bitácora — especificación (contrato compartido)

App web para llevar una **bitácora de trabajo diario**: registrar actividades del día,
tiempo dedicado, categoría, estado y notas; consultar, filtrar, resumir y exportar.

## Stack
- Node.js ≥ 22 (sin dependencias nativas). Base de datos: `node:sqlite` (`DatabaseSync`).
- Backend: Express 5 (`server/`). Frontend: HTML/CSS/JS vanilla servido estático desde `public/`.
- Pruebas: `node:test` + `fetch` nativo (`test/`). Sin dependencias extra.

## Estructura
```
server/app.js     -> export function createApp({ dbPath }) => { app, db }   (no hace listen)
server/db.js      -> abre la BD, crea el esquema, expone funciones de acceso
server/index.js   -> arranca: PORT (default 3000), DB_PATH (default ./data/bitacora.db)
public/           -> index.html, styles.css, app.js (SPA en español)
test/*.test.js    -> pruebas de la API
```
`createApp({ dbPath: ':memory:' })` debe funcionar (lo usan las pruebas).
`app` sirve `public/` como estático y la API bajo `/api`.

## Modelo: Entrada (`entry`)
| campo      | tipo                | reglas |
|------------|---------------------|--------|
| id         | entero              | autoincremental |
| date       | string `YYYY-MM-DD` | requerido, fecha válida |
| title      | string              | requerido, 1–200 caracteres (se recorta con trim) |
| notes      | string              | opcional, ≤ 5000, default `""` |
| minutes    | entero              | opcional, 0–1440, default `0` |
| category   | string              | opcional, ≤ 50, default `"General"` |
| status     | string              | `pendiente` \| `en_progreso` \| `completada`; default `completada` |
| tags       | string[]            | opcional, cada tag trim, no vacío, ≤ 30 chars, máx 10, sin duplicados; default `[]` |
| createdAt  | string ISO 8601     | lo asigna el servidor |
| updatedAt  | string ISO 8601     | lo asigna el servidor |

Las respuestas JSON usan exactamente estos nombres (camelCase). `tags` siempre es arreglo.

## API (JSON, prefijo `/api`)
- `GET /api/health` → `200 {"status":"ok"}`
- `GET /api/entries` → `200 [entry...]`, orden `date` desc, luego `id` desc.
  Query opcionales: `from`, `to` (inclusive, `YYYY-MM-DD`), `q` (busca en title/notes, sin distinguir mayúsculas),
  `category` (exacta), `status`, `tag` (contiene ese tag). Parámetro inválido (fecha/estado) → 400.
- `GET /api/entries/:id` → `200 entry` | `404`
- `POST /api/entries` → `201 entry` | `400`
- `PUT /api/entries/:id` → reemplazo completo (mismas reglas que POST) → `200 entry` | `400` | `404`
- `DELETE /api/entries/:id` → `204` | `404`
- `GET /api/categories` → `200 ["General", ...]` categorías distintas usadas, orden alfabético
- `GET /api/summary?from&to` →
  ```json
  { "totalEntries": 3, "totalMinutes": 150,
    "byDay": [{"date":"2026-10-30","count":2,"minutes":90}],          // orden date asc
    "byCategory": [{"category":"General","count":3,"minutes":150}],   // orden minutes desc
    "byStatus": {"pendiente":0,"en_progreso":1,"completada":2} }
  ```
- `GET /api/export.csv?from&to` → `200 text/csv; charset=utf-8`, con
  `Content-Disposition: attachment; filename="bitacora.csv"`.
  Columnas: `id,date,title,minutes,category,status,tags,notes` (tags unidos con `;`), escapado RFC 4180, orden date asc.

Errores: `400 {"error":"Datos inválidos","details":["mensaje", ...]}`, `404 {"error":"No encontrado"}`.
`:id` no numérico → 404. JSON mal formado → 400.

## Frontend (español)
- Formulario rápido para nueva entrada (fecha = hoy por defecto, título, minutos/horas, categoría con
  sugerencias de `/api/categories`, estado, tags separados por coma, notas).
- Lista agrupada por día con total de tiempo por día; editar y borrar (con confirmación) cada entrada.
- Filtros: rango de fechas (atajos Hoy / Semana / Mes), búsqueda de texto, categoría, estado.
- Panel de resumen del rango: total entradas, total horas, gráfico de barras simple por día (SVG/CSS) y por categoría.
- Botón "Exportar CSV" que respeta el rango.
- Responsive (móvil primero), modo claro/oscuro con `prefers-color-scheme`, accesible (labels, foco visible).
