# Tablero del plan socialista

Lo edita el usuario (orden, notas, límites), la bitácora (`/bitacora`: mete las tareas que el usuario aprueba y las
marca `hecha` al fusionarse su PR) y el director del plan (estados). Una tarea por línea, en orden de prioridad.

- **Límite por sesión:** 1 tarea. La siguiente, en una sesión nueva (el director relee su conversación en cada paso).
- **Vueltas máximas por tarea:** 3 (constructor ↔ jueces). Una 4.ª solo si tras la 2.ª quedan más de 3 fallos.
- **Parar si:** 2 tareas seguidas fallan o quedan bloqueadas.
- **Límite de gasto por día:** como mucho el **18 % del uso semanal**, sumando todas las sesiones (heredado de
  fiebres-neutropenias, 27/10/2026; lo puede cambiar el usuario). Hasta calibrar su equivalencia en millones de
  `gasto.mjs`, el director avisa antes de lanzar algo que pase de ~10 M en el día.
- **Presupuestos vigentes** (de fiebres-neutropenias; se ajustan con lo medido aquí): metodólogo diseñar · potente
  40 pasos / 0,85 M · metodólogo juzgar · potente 20 / 0,4 M · rejuicio · potente 13 / 0,25 M · constructor de un
  documento o script · sonnet 60 / 1,1 M · constructor arreglos cortos · sonnet 15 / 0,1 M · auditor · sonnet
  35 / 0,55 M · lector de fuente · sonnet 30 / 0,5 M · revisión del encargo · sonnet 10 / 0,15 M · director, una
  tarea: 0,9 M.
- **Datos de pacientes**: ninguna tarea los sube a GitHub (`CLAUDE.md` §2). Una tarea que necesita datos reales se
  entrega como script probado con datos simulados y con las instrucciones para ejecutarlo en el hospital.
- **Una tarea solo pasa a `en revisión`** con el enlace de su PR anotado; sin enlace, no avanza.

Estados: `pendiente` · `en curso` · `en revisión` (PR abierta) · `hecha` (PR aprobada) · `necesita humano` · `aparcada`

## Tipos de tarea y su «hecho»

| Tipo | Qué es | «Hecho» propio | Modelo del constructor |
|---|---|---|---|
| `documento` | algo para usar en el estudio: diccionario de variables, cuaderno de recogida, procedimiento de segmentación, configuración de extracción | fiel al protocolo (auditor sin graves) + rúbrica del metodólogo ≥8 (meta 8,75; REGLAS §8) + jueces | sonnet |
| `script` | código del análisis (descriptiva, ICC, Dice, gráficos, selección al azar, comprobación de cabeceras DICOM) | prueba con datos simulados de resultado conocido en `autonomo/pruebas/` + jueces + metodólogo ≥8 | sonnet (el primero de algo nuevo, opus) |
| `informe` | una propuesta o un resultado para el usuario o el tutor (Artifact) | fuentes con página + auditor sin graves + solo agregados | sonnet |
| `fuentes` | buscar y bajar a `docs/fuentes/` las fuentes que faltan (IBSI, RECIST 1.1, manuales) | cada fuente abierta, con su URL comprobada y su página | sonnet |
| `ingenieria-inversa` | estudiar una web o programa ajeno (`/ingenieria-reversa`) | informe-propuesta y elección del usuario | sonnet |
| `arreglo` | un fallo concreto | el fallo ya no se reproduce y los jueces siguen en verde | sonnet |

## Ficha de encargo (una por tarea, debajo de su fila)

```
**Encargo `<clave>`** · tipo: documento | script | informe | fuentes | ingenieria-inversa | arreglo
- Qué quiero: una frase.
- Para qué: qué paso del estudio desbloquea (protocolo §…).
- Resultado que debe salir: cómo se sabrá que está bien (prueba con datos simulados, cotejo con el protocolo…).
- Datos reales: no | sí (dónde se ejecuta y qué sale: solo agregados).
- Lo que NO quiero.
- Fuente: protocolo §… y archivo/página o URL comprobada.
```

---

## Objetivo 0 · Preparar el estudio

Tareas aprobadas por el usuario. **De momento, ninguna**: lo apuntado espera su visto bueno en
`autonomo/BITACORA.md`.

| # | Clave | Qué | Estado | Nota |
|---|---|---|---|---|
