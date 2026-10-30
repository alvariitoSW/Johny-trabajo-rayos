# Cómo se montó el proyecto

## 30/10/2026 · El método de fiebres-neutropenias, adaptado a un estudio de radiómica

El usuario pidió «aplicar la forma de trabajar de fiebres-neutropenias en este repositorio, teniendo en cuenta las
páginas web de radiología que le mandó», con el fin de «obtener y analizar los datos descritos en el protocolo de
estudio». Eligió copiar **todo, adaptado**, y subir el protocolo aunque el repositorio sea público.

**Qué se trajo y cómo se adaptó** (origen: `alvariitoSW/fiebres-neutropenias`, `main` del 30/10/2026):

| Allí | Aquí |
|---|---|
| `CLAUDE.md` de una app web de UCI | `CLAUDE.md` de un estudio: el protocolo manda, datos de pacientes fuera del repositorio, análisis solo descriptivo |
| `autonomo/REGLAS.md` (contenido clínico, app, rúbrica «sirve para estudiar») | mismas ideas de fuentes, gasto, gobierno y Consejo; la app se cambia por «datos y análisis»; rúbrica «sirve para el estudio» |
| 7 agentes con el **profesor** | 7 agentes con el **metodólogo** (diseña y juzga el método) |
| `jueces.mjs` (navegador a 390 px) | `jueces.py`: ningún dato de paciente en git + las pruebas de los cálculos |
| skills `plan-socialista`, `bitacora`, `ahorro`, `ingenieria-reversa` | las mismas, reescritas para el estudio |
| `gasto.mjs`, `AGENTS.md` (Ponytail) | copiados tal cual |
| informes de Radiology Assistant y NavRad | copiados en `autonomo/ideas/ingenieria-inversa/` + `webs-radiologia.md` con lo útil para el estudio |

**No se trajo**: la app, sus motores, Motion, la Mayéutica, los jueces de móvil, graft y sus ganchos (no aplican a un
estudio), ni las skills de anatomía, radar y mayéutica. Las skills de investigación (`claim-check`, `paper-lookup`,
`pydicom`…) se pueden copiar cuando una tarea las pida.

**Decisiones**:
- El repositorio es público: `.gitignore` bloquea imágenes y tablas, y `jueces.py` lo comprueba (prueba trampa
  `autonomo/pruebas/jueces_trampa.py`).
- Lo que el protocolo deja abierto («???») no lo decide ningún agente: B-001 de la bitácora lo lista para el usuario.
- Páginas de Radiology Assistant útiles para el estudio, abiertas con 200 el 30/10/2026 (anatomía segmentaria,
  lesiones hepáticas, RECIST 1.1, protocolos de contraste). TCIA, Zenodo, arXiv, readthedocs y lifexsoft.org están
  bloqueados en la red del entorno: la colección «Colorectal-Liver-Metastases» y el IBSI quedan «por verificar».
