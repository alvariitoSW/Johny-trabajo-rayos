# Reglas del plan socialista (equipo autónomo)

Corto a propósito: todos los agentes lo leen en cada vuelta, junto con `CLAUDE.md`. Vienen del proyecto
`alvariitoSW/fiebres-neutropenias` (aprobadas allí por el usuario entre el 14 y el 30/10/2026) y se adaptan a un
estudio de investigación: aquí no se construye una app, se **obtienen y analizan los datos del protocolo**.

## 1. Fuentes y fidelidad al protocolo

1. **Nunca inventes.** Toda cifra, parámetro, definición o afirmación sale de una fuente que se puede abrir (el
   protocolo con su §, un PDF de `docs/fuentes/` con su página, una web verificada). Si no la encuentras, no la
   escribas: anótala como hueco.
2. **El protocolo es la fuente principal.** Lo que hace el equipo (diccionario, cuaderno de recogida, configuración,
   scripts, informes) se coteja con él apartado por apartado. Apartarse del protocolo nunca es silencioso: nota
   visible con el § y la decisión del usuario.
3. **Lo que el protocolo deja abierto** («???», «¿…?», campos vacíos) es una **duda para el usuario**, no una
   decisión del agente. El agente puede proponer opciones con su fuente; elige el usuario (y su tutor).
4. **Si dos fuentes no coinciden**, se muestran las dos con una nota de fuentes. No se elige una ganadora.
5. **Lo que la fuente no dice, se busca y se cita** (regla nacida en fiebres-neutropenias el 27/10/2026): IBSI,
   documentación de LIFEx y de PyRadiomics, RECIST 1.1, artículos de PubMed (`/claim-check`, `/paper-lookup` si
   están). Si es un PDF de acceso abierto, va a `docs/fuentes/` con su `#page=`. Hueco solo cuando se buscó y no se
   encontró: el parte dice qué se buscó y dónde.
6. **Antes de pedir un PDF al usuario**, quien lo necesita lo busca en abierto (Europe PMC, PubMed Central, la web del
   editor o de la sociedad) y anota dónde buscó. Solo se pide si es de pago, y con el enlace exacto.
7. **Cada frase nueva de método, con su fuente.** El constructor entrega la lista de frases nuevas (definiciones,
   fórmulas, parámetros) con su página; el auditor la coteja frase a frase. Sin fuente y no trivial = grave.
8. **Tres tipos de nota**: **las fuentes discrepan**, **la fuente no lo dice** y **opinión del autor**. Nunca se marca
   como error algo que la fuente afirma literalmente.
9. **Nombres exactos de las características** (protocolo §10): el nombre que da el programa (LIFEx o PyRadiomics),
   su fórmula y su código IBSI si existe. Dos características con nombre parecido y fórmula distinta son dos
   variables.

## 2. Datos de pacientes (el repositorio es público)

1. **Ningún dato real fuera del entorno del hospital**: ni en git, ni en Artifacts, ni en PR, ni en mensajes, ni en la
   carpeta temporal de un agente. Prohibido: DICOM, NIfTI, NRRD, máscaras, CSV/XLSX/SAV/OMV con datos reales,
   nombres, NHC, DNI/NIE, fechas de nacimiento o de estudio, números de acceso y la tabla de correspondencia
   código ↔ paciente (`CLAUDE.md` §2).
2. **Datos simulados para todo lo demás**: los scripts se prueban con datos sintéticos de `tests/generar_sinteticos.py`,
   que marcan «DATOS SIMULADOS» o «DATOS SINTÉTICOS» y no se suben. Nunca se «disfraza» un dato real como simulado.
3. **Seudonimización** (protocolo §13): código de estudio por paciente (`RMH-001`…); la tabla de correspondencia, solo
   en el hospital. Antes de exportar imágenes para el análisis, se comprueba que no quedan identificadores en las
   cabeceras DICOM (lo hace y lo informa `src/01_convertir.py`: `outputs/anonimizacion.csv`).
4. **Resultados agregados**: nada fila a fila; ninguna celda con menos de 5 pacientes que permita reconocer a alguien.
5. **Si se cuela un dato real**: se para, se avisa al usuario y no se intenta arreglar con un commit encima (queda en
   la historia de git).

## 3. Análisis

1. **Solo lo que dice el plan de análisis** (protocolo §11): descriptiva de la muestra, perfil radiómico (media,
   mediana, DE, RIC, mínimo, máximo, histogramas o cajas, CV cuando proceda) y reproducibilidad (ICC de acuerdo
   absoluto con IC 95 % y Dice). Lo de §11.4 (modelos, ROC, aprendizaje automático, contrastes entre subgrupos) no se
   hace.
2. **Cada cálculo, probado con datos de resultado conocido** antes de usarse (observadores idénticos → ICC 1 y Dice
   1; máscaras sin solapamiento → Dice 0; una tabla de libro con su ICC publicado). La prueba se guarda en
   `autonomo/pruebas/` y la pasa `jueces.py`.
3. **El modelo de ICC se escribe** (p. ej. Koo y Li 2016 o McGraw y Wong 1996: dos factores, efectos aleatorios,
   acuerdo absoluto, medida única), con la fuente de la fórmula.
4. **Ausentes ≠ 0.** Se cuentan y se informan por variable.
5. **La configuración de extracción no cambia a mitad** (`CLAUDE.md` §3). Si cambia, se reextrae todo.
6. **Mismo número, mismo resultado**: un script con semilla fija para la selección al azar del 20-30 % de
   reproducibilidad; la semilla y la lista quedan registradas (la lista, en el hospital).

## 4. Redacción

1. Español claro, frases cortas y en voz activa. Sin muletillas.
2. Nombra las cosas como las conoce un radiólogo; si un término es de estadística o de programación, una frase que lo
   explique.
3. **Nada interno a la vista** en los documentos para el tutor o el comité: ni códigos del plan, ni rutas, ni notas de
   trabajo.
4. **La ley de explicar en llano** (Consejo del 30/10/2026, aprobada por el usuario: «aplica todo»). Toda cifra que
   llegue al usuario (tabla, figura, informe) va con una frase en llano: qué mide, en qué unidad y qué indica un valor
   alto, tomada de `docs/guia_interpretacion.md`. La guía separa tres niveles: qué mide (de la documentación del
   programa), qué se ve en la TC (solo con fuente radiológica citada con página) y significado clínico (no se da: el
   estudio es descriptivo, protocolo §11.4, y las características no son biomarcadores validados). Si falta la fuente,
   se escribe «sin fuente» y no se rellena. Cada estadístico (Dice, ICC con su IC 95 %, CV, mediana y RIC, Spearman)
   lleva su explicación de una frase y su límite. Las características que dependen del tamaño, del binWidth o con
   escala distinta a IBSI llevan su aviso. Nada de «válida / no válida» por un umbral de ICC (§11.3).

## 5. Trabajo y git

1. **Solo la tarea encargada.** Si ves otro problema, anótalo en el parte («Visto de paso»); no lo arregles de paso.
2. **Nada se da por hecho sin los jueces**: `python3 autonomo/jueces.py` en verde y los puntos de «hecho» del tablero.
3. **Pocas paradas para el usuario**: por tarea, como mucho el plan, el resultado y sus cambios. Lo técnico y los
   arreglos, con los jueces en verde, sin pedir aprobación; se cuenta en una línea. **Se pregunta siempre** lo grande
   o difícil de deshacer: cambiar el protocolo, el software, la configuración de extracción o quitar variables.
4. **El contenedor se borra**: lo que no está en una rama subida a GitHub se pierde.
5. **Trabajo en paralelo**: como mucho 3 agentes pesados a la vez, encargos de una pieza, cada uno en su subcarpeta
   (`/tmp/plan-socialista/<clave>/<agente>/`). Nunca `git stash` ni `pkill` amplios. **Una tarea, una sola sesión**:
   antes de empezar, mira las sesiones activas (`list_sessions` con `mine: true`) y la rama `auto/<clave>`.
6. **Gasto que baja** (decisión del usuario del 26/10/2026 en fiebres-neutropenias: «cada operación que cueste X
   tokens, la siguiente que intente costar un poco menos»):
   - Cada encargo lleva su **presupuesto** (pasos y tokens; tabla «Presupuestos vigentes» del tablero). Al llegar, el
     agente para y entrega lo hecho con lo que falta. El parte compara gasto y presupuesto.
   - **Modelos**: el más potente solo para pensar (metodólogo: diseñar y juzgar el análisis). Constructores, arreglos,
     auditor y revisores, en sonnet.
   - **Sesiones cortas**: una sesión por tarea; la siguiente, en otra sesión.
   - **Lecturas acotadas**: cada agente lee su encargo y solo los apartados de estas reglas que le nombren; las
     fuentes por archivo y páginas exactas.
   - **Encargos de una pieza** (≤100 pasos; si no cabe, se parte antes).
   - **Lo hecho no se repite**: los scripts de prueba se guardan en `autonomo/pruebas/` y se reutilizan.
7. **El encargo, revisado antes de gastar** (lista de calidad, la pasan `/bitacora` y el director):
   1. ¿Dice **qué resultado debe salir** (o cómo se sabrá que está bien: prueba con datos simulados)?
   2. ¿Está **«lo que NO quiero»**?
   3. ¿Cada **fuente** tiene archivo (o URL verificada) y **página o §**?
   4. ¿**Qué juez comprueba** cada punto del «hecho»? Lo que ninguno mide se marca.
   5. ¿Toca **datos reales**? Si sí, ¿dónde se ejecuta (solo en el hospital) y qué sale (solo agregados)?
   Como mucho **5 preguntas al usuario por encargo**; lo demás se decide y se marca «(supongo)».
8. **El gobierno** (reforma aprobada en fiebres-neutropenias el 28/10/2026):
   - **Gobierno central**: el usuario, con la bitácora. Aprueba el presupuesto y las paradas.
   - **Interior = `/plan-socialista`**: presupuesta cada tarea antes de gastar y rinde cuentas en el parte.
   - **Hacienda = `/ahorro`**: revisa el presupuesto antes de gastar (solo tareas de 2 M o más) y recorta lo que no
     baja la calidad ni la fidelidad; lo deja escrito.
   - **Transportes = `/bitacora`**: rumbo, cola y calendario.
   - **Ciencia = `/ingenieria-reversa`**: estudia webs y programas ajenos (Radiology Assistant, NavRad, LIFEx,
     SlicerRadiomics) y propone qué traer.
   - **Justicia = los jueces automáticos y el auditor ciego**: independientes; nadie los recorta.
   - **Comparecer**: si una tarea va a pasarse más de un 25 % de su presupuesto, el director para y lo explica.
9. **El Consejo de Ministros** (como mucho una reunión al día, cuando haya asuntos): lo convoca la bitácora, que
   preside y escribe el acta en `autonomo/consejo/AAAA-MM-DD.md` (formato en su `LEEME.md`). Dictámenes de ≤15 líneas
   por asunto (Interior, Hacienda, Justicia, Transportes; Ciencia si toca). Aprueba dudas de los planes, orden y
   opciones de los informes dentro del presupuesto. **Reservado al usuario**: el presupuesto total, cualquier cambio
   del protocolo, del software o de la configuración de extracción, y quitar variables. Gasto de una reunión: ≤2 M.

## 6. Lo que el agente puede y no puede tocar

1. **Las reglas son de solo lectura** para el agente: nunca edita `autonomo/REGLAS.md`, `CLAUDE.md`, el protocolo
   (`docs/protocolo/`) ni sus propias instrucciones (`.claude/agents/`, skills del proyecto). Si cree que una regla
   falla, lo propone en su parte y el usuario decide.
2. **El estado sí lo escribe**: los estados de `autonomo/TABLERO.md` y su parte en `autonomo/partes/`.
3. **No avanzar sin prueba**: una tarea solo pasa a `en revisión` cuando la PR existe (con su enlace en el parte).
4. **Lo que no se pudo leer es un hueco, no un hecho.**
5. **«No había nada que hacer» no es un fallo.**
6. **Límite de gasto**: el del tablero, por sesión y por día. Al llegar, se para.

## 7. Cómo crecen estas reglas

Cuando un fallo se cuela por los jueces, no se arregla solo esa vez:
1. El parte lo anota en «Propuestas sobre las reglas»: qué falló, por qué no lo vio ningún juez y qué regla o
   comprobación lo habría cazado (y si se puede automatizar en `autonomo/jueces.py`).
2. **El usuario decide.** Si la aprueba, entra aquí, en el agente que debía verlo y, si aplica, en `CLAUDE.md` y en
   los jueces. El agente nunca la añade por su cuenta.
3. Cada regla nacida así se apunta abajo, con la tarea donde se vio.

**Reglas nacidas de fallos**
- (ninguna todavía en este proyecto)

## 8. Sirve para el estudio (rúbrica del metodólogo; manda tanto como la fidelidad)

Cada entrega (diccionario, cuaderno de recogida, configuración, script, informe) la puntúa el metodólogo del 0 al 10.
Aprueba con 8 en todo; la meta es 8,75.
1. **Fiel al protocolo**: cada decisión lleva su §; lo que se aparta, con nota y decisión del usuario.
2. **Reproducible**: otra persona, con el mismo archivo y el mismo script, obtiene lo mismo.
3. **Probado**: cada cálculo con datos simulados de resultado conocido.
4. **Protege los datos**: nada identificable; resultados agregados.
5. **Se entiende**: un R1 lo lee en el móvil y sabe qué hacer; las tablas caben a 390 px; cada término técnico,
   explicado.
6. **Listo para usar**: el cuaderno se rellena sin dudas; el script corre con una orden; el informe responde la
   pregunta de investigación (§2).
