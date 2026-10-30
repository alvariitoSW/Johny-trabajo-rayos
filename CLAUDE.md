# Radiómica de metástasis hepáticas colorrectales — reglas del proyecto

Proyecto de investigación: **obtener y analizar los datos que describe el protocolo de estudio**
(`docs/protocolo/protocolo-v0.md`): estudio observacional, retrospectivo, descriptivo y transversal del perfil
radiómico de las metástasis hepáticas de origen colorrectal en TC con contraste en fase portal (LIFEx, o la opción B:
3D Slicer + SlicerRadiomics + jamovi). Unidad de análisis: una lesión por paciente. Muestra inicial: 50 pacientes.

La forma de trabajar es la del proyecto `alvariitoSW/fiebres-neutropenias` (el «plan socialista»), adaptada a un
estudio de investigación. Este archivo son **las reglas vigentes**, cortas a propósito:
- Lo pendiente vive en `autonomo/BITACORA.md` (sin aprobar; skill `/bitacora`) y `autonomo/TABLERO.md` (aprobado,
  lo trabaja `/plan-socialista`), no aquí.
- La historia de cómo se hizo cada parte está en `docs/historial/` (índice al final). Búscala con grep; no la leas
  entera.

## 1. Cómo trabaja el usuario

- Es médico residente (R1), no programador. **Explícale en lenguaje llano**, sin jerga técnica. Si un término técnico
  hace falta (ICC, Dice, discretización), explícalo en una frase.
- Lo lee todo en el móvil: informes cortos, tablas estrechas, enlaces que se abren con un toque.
- **Para trabajos grandes, primero un informe o una propuesta** (a menudo una página tipo Artifact): qué se va a
  hacer, qué falla, qué falta. Después, él dice «aplica todo» o elige.
- **Pregunta antes de una decisión grande o difícil de deshacer** (cambiar el protocolo, el software, la
  configuración de extracción, quitar variables). Lo pequeño y obvio, hazlo.
- Manda las fuentes en PDF u ODT y espera que no se resuman por debajo de la fuente.
- Si pide algo que contradice una regla de aquí o el protocolo, avísale y que decida él.

## 2. Datos de pacientes: el repositorio es PÚBLICO (no se negocia)

- **Nunca** entra en git, en un Artifact, en una PR ni en un mensaje: imágenes DICOM, NIfTI, NRRD, máscaras de
  segmentación, tablas con datos reales (CSV, XLSX, SAV, OMV), nombres, NHC, DNI/NIE, fechas de nacimiento, fechas
  de estudio, números de acceso, ni la tabla que une el código del paciente con su identidad.
- Los datos reales viven **solo** en los equipos y entornos autorizados por el hospital (protocolo §13, RGPD). En
  el repositorio solo hay: el protocolo, el diccionario de variables, la configuración de extracción, los scripts y
  **datos simulados** (`datos-ejemplo/`, marcados como simulados en su primera línea).
- Lo que se publique de resultados va **agregado** (medias, medianas, ICC), nunca fila a fila, y sin celdas de menos
  de 5 pacientes que permitan reconocer a alguien.
- `.gitignore` bloquea las extensiones de datos; `python3 autonomo/jueces.py` lo comprueba antes de cada commit.
  Si un dato real llegara a subirse, **para todo y avisa al usuario**: hay que borrarlo de la historia de git y
  avisar al responsable de protección de datos; no basta con un commit que lo quite.

## 3. El protocolo manda (decisiones que no se reabren sin preguntar)

- **Es descriptivo** (protocolo §11.4): nada de modelos de clasificación, regresión pronóstica, curvas ROC,
  aprendizaje automático, selección de características por desenlace ni contrastes entre subgrupos como análisis
  principal. Si alguien lo propone, va a la bitácora como idea para otro estudio.
- **Una lesión índice por paciente**: la de mayor volumen que cumpla los criterios técnicos y de lesión diana de
  RECIST 1.1 (≥10 mm), elegida con una regla fijada **antes** de analizar las imágenes (§6).
- **Configuración de extracción única y escrita antes de extraer** (§9): imagen original en UH, 3D, remuestreo,
  interpolación, discretización y filtros. Se guarda en un archivo versionado (`analisis/config/`) y no se toca a
  mitad del estudio; si cambia, se vuelve a extraer todo y el historial lo cuenta.
- **No se asumen equivalencias entre programas** (§10): una característica de LIFEx y otra de PyRadiomics con nombre
  parecido no son la misma si su fórmula difiere. Cada variable del diccionario lleva su nombre exacto en el programa,
  definición, unidad, configuración y su correspondencia IBSI cuando exista.
- **Reproducibilidad** (§8, §11.3): 20-30 % de lesiones al azar (mínimo orientativo 15) segmentadas por un segundo
  observador independiente; ICC de acuerdo absoluto con IC 95 % (diciendo el modelo: p. ej. ICC(A,1), dos factores,
  efectos aleatorios) y Dice. Se informa por variable, sin un único umbral de ICC que declare «válida» una
  característica.
- **Lo que el protocolo deja abierto** (marcado con «???» o «¿…?» en el texto: grosor de corte, matriz, un solo
  equipo de TC, marca del contraste, erosión del contorno, matriz de Spearman, LIFEx frente a la opción B) **no lo
  decide el agente**: va a la bitácora como duda para el usuario y su tutor.

## 4. Estructura

```
docs/protocolo/      el protocolo (fuente principal) y sus versiones
docs/fuentes/        PDF de las fuentes (IBSI, RECIST 1.1, manuales de LIFEx y PyRadiomics…) con su #page=
docs/historial/      la historia del trabajo
analisis/            scripts del análisis (descriptiva, ICC, Dice, gráficos) y config/ (extracción, diccionario)
datos-ejemplo/       datos SIMULADOS para probar los scripts (nunca reales)
autonomo/            plan socialista: guía, reglas, bitácora, tablero, sesiones, partes, Consejo y jueces
```

## 5. Fuentes

1. **Nunca inventes.** Toda cifra, parámetro, definición o afirmación metodológica sale de una fuente que se puede
   abrir: el protocolo (con su §), un PDF de `docs/fuentes/` con `#page=N`, o una web verificada. Si no está, se
   busca y se cita (`autonomo/REGLAS.md` §1.5); hueco solo si se buscó y no se encontró.
2. **Webs**: solo URL comprobadas (que se abren y salen literales en la búsqueda), nunca un buscador genérico.
3. **Webs de radiología de referencia** (enviadas por el usuario; informes en `autonomo/ideas/`): The Radiology
   Assistant y NavRad Anatomy. Sirven para **aprender y para saber qué buscar** (anatomía segmentaria, RECIST 1.1,
   protocolos de contraste, cómo se ven las metástasis); sus textos e imágenes no se copian, y sus cifras no son
   fuente del estudio sin una referencia primaria. Lista de páginas útiles: `autonomo/ideas/webs-radiologia.md`.
4. **Leer un PDF largo**: en lotes de 6-8 páginas; si un lote devuelve menos páginas, relee las que faltan.
5. **Discrepancias**: si dos fuentes (o el protocolo y una fuente) no coinciden, se muestran las dos con una nota;
   no se elige ganadora por criterio propio. Lo que afecta al protocolo lo decide el usuario.

## 6. Análisis y código

- **Reproducible de punta a punta**: de la tabla exportada (CSV de LIFEx o SlicerRadiomics) al resultado, con un
  script que se vuelve a ejecutar y da lo mismo. Nada de pasos a mano sin escribir.
- **Antes de dar por bueno un cálculo, se prueba con datos simulados de resultado conocido** (p. ej. dos
  observadores idénticos → ICC = 1 y Dice = 1). La prueba se queda en `autonomo/pruebas/`.
- Un campo vacío es **dato ausente**, nunca 0. Se cuenta y se informa (§11.1).
- El coeficiente de variación solo donde tenga sentido (no con medias cercanas a cero ni escalas con negativos,
  §11.2).
- Herramientas: las que diga el protocolo (SPSS, Python, jamovi). Ninguna librería nueva sin que el usuario la elija;
  mientras no elija, Python con la biblioteca estándar.
- Escalera antes de escribir código (ver `AGENTS.md`): reutiliza lo que hay antes de escribir nada nuevo.

## 7. Git

- Rama de trabajo de esta sesión: `claude/fiebres-neutropenias-radiologia-h6a59g`. Tras cada tanda: commit y push.
  Fusionar a `main` solo con el visto bueno del usuario.
- **Plan socialista** (`/plan-socialista`): cada tarea va a una rama `auto/<clave>` con una sola PR en borrador; los
  arreglos y lo técnico, con los jueces en verde.
- Antes de cada commit: `python3 autonomo/jueces.py` en verde (sin datos de pacientes, sin archivos prohibidos).

## 8. Redacción e idioma

Todo en español: documentos, scripts y comentarios. Frases cortas, voz activa, sin muletillas. Nombra las cosas
como las conoce un radiólogo o un médico, no como están hechas por dentro.

## 9. Antes de dar un trabajo por terminado

- [ ] `python3 autonomo/jueces.py` en verde.
- [ ] Ningún dato real en git, en el Artifact ni en la PR (§2).
- [ ] Todo lo nuevo, fiel al protocolo; lo que se aparta, con su nota y la decisión del usuario.
- [ ] Toda cifra o parámetro nuevo con su fuente y su página.
- [ ] Los scripts nuevos, probados con datos simulados de resultado conocido.
- [ ] La historia, en `docs/historial/`. Lo pendiente nuevo, en `autonomo/BITACORA.md`.
- [ ] Al usuario, en llano: qué se hizo, qué se comprobó y qué queda para él.

## 10. Índice del historial (`docs/historial/`)

| Archivo | Qué cuenta |
|---|---|
| `general.md` | Cómo se montó el proyecto y el método de trabajo (30/10/2026) |
