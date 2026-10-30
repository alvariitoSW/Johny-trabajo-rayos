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

## 30/10/2026 · Pipeline de radiómica (pedido directo del usuario)

El usuario (radiólogo) pidió el pipeline completo: conversión y anonimización, extracción con pyRadiomics, control
de calidad, reproducibilidad, descriptivo, informe PDF, diccionario y pruebas con datos sintéticos. Decidió 3D
Slicer + pyRadiomics (no LIFEx), binWidth 25 por defecto (10 opcional) y la matriz de Spearman.

- **pyRadiomics**: en PyPI solo hay binarios hasta Python 3.9 y el paquete fuente 3.1.0 no compila (le falta
  `cmatrices.h`). El usuario autorizó instalarlo desde el repositorio oficial fijado a la etiqueta v3.1.0 (commit
  `6a761c4`). Se compila; en Windows sin administrador, la vía recomendada es llevar un wheel compilado en otro PC
  (README). La instalación en Windows no se ha probado.
- **Del código de pyRadiomics** (no de memoria): StandardDeviation está desactivada por defecto (por eso
  `params.yaml` lista firstorder entera); la curtosis no es la de exceso (+3 frente a IBSI); la discretización
  difiere de IBSI; la máscara siempre se remuestrea con vecino más próximo.
- **IBSI**: el documento de referencia no se pudo abrir (red bloqueada); los códigos van marcados (v).
- **Decisiones técnicas**: la máscara de Slicer (recortada a su extensión) se recoloca en la rejilla de la imagen
  sin interpolar, y si el espaciado u orientación no coinciden, el paso 1 para. El criterio de ≥ 10 mm se aplica
  al diámetro axial (como RECIST 1.1). HD95 = el mayor de los dos percentiles 95 dirigidos. ICC = «ICC2» de pingouin.
- **Pruebas**: 12 (pytest) sobre 10 casos sintéticos con UH, ruido y tamaño conocidos, identificadores falsos en las
  cabeceras, segmentaciones tipo Slicer y DICOM-SEG, y dos casos trampa (lesión de 8 mm y dos componentes).
