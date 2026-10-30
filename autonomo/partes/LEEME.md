# Partes de sesión

Uno por sesión del plan socialista: `AAAA-MM-DD-<clave>.md`. Lo escribe el director al terminar, aunque la sesión
falle o no haya nada que hacer. Formato:

```
# AAAA-MM-DD · <clave de la tarea, o «sin tareas»>

**Resultado:** en revisión (PR: <enlace>) | necesita humano | fallida | sin tareas pendientes
**Vueltas:** N · **Jueces:** jueces.py ✓/✗ · auditoría ✓/✗ · metodólogo <nota>

## Qué se hizo
2-4 líneas en lenguaje llano.

## Qué no se pudo hacer o leer
Fuentes que no se abrieron, pasos que fallaron. Nunca se omite.

## Para el usuario
Lo que tiene que revisar o decidir.

## Visto de paso (no tocado)

## Propuestas sobre las reglas

## Vueltas
Una fila por vuelta: pieza · vuelta · nota mínima del metodólogo · modelo del constructor · pasos · tokens · qué falló.

## Gasto y cuentas
`node autonomo/gasto.mjs --clave <clave>`: total, tabla «Por papel», los 3 agentes que más gastaron; presupuesto,
recortes de Hacienda, gastado y desvío. Una línea: dónde se fue y cómo se ahorraría la próxima vez.
```
