> Copiado de `alvariitoSW/fiebres-neutropenias` (`autonomo/ideas/ingenieria-inversa/navrad.md`) el 30/10/2026. Se hizo para aquella app de UCI: «nuestra app» y sus rutas se refieren a ella. Lo útil para este estudio está en `autonomo/ideas/webs-radiologia.md`.

# NavRad Anatomy — informe de ingeniería inversa (23/10/2026)

Sitio: https://anatomy.navigatingradiology.com · Probado con Playwright a 390×844 (móvil). REA (`rea-agents`
6.7.0) se probó: su flujo web (`analyze-web-bundle`) necesita un navegador abierto con depuración remota; con
Playwright directo bastó. Su código no se ha guardado en disco: se leyó en memoria y solo se anotan ideas.

## 1. Qué es y qué ofrece

- Atlas de anatomía radiológica sobre **estudios reales completos**, no figuras sueltas: se pasa corte a corte
  como en el PACS del hospital. «Preview version» (gratis sin cuenta) y cuenta gratuita de Navigating Radiology.
- 5 visores activos: TC de tórax (296 estructuras), abdomen-pelvis, TC cardíaco, TC de cráneo, angio-TC de
  carótidas. 6 «Coming soon» (cuello partes blandas, RM de rodilla, hombro, tobillo, columna y cerebro).
- Por estructura: contorno de color sobre la imagen, rótulo con línea, y una **nota docente corta** (2-4 frases,
  con negritas en la trampa clínica; p. ej. de la VCI: «la mezcla de contraste puede simular un trombo»). Cada nota
  tiene estado `reviewed` o `draft` (revisión por radiólogo visible en los datos).
- Varias series por estudio (axial partes blandas, pulmón, 0,5 mm, coronal, sagital, MIP coronal, scout).
- **AI Guide** (chat): «Show me…», «Quiz me», «Teach me…». Busca una estructura y salta al corte, monta quizzes y
  lecciones paso a paso.
- **Quiz «¿dónde está?»**: «Where is the Inferior Vena Cava? Click the image to place your marker, drag to adjust,
  then reveal». El alumno se desplaza por los cortes, pone su marca, y al «revelar» se pinta el contorno de
  referencia. **No puntúa**: el alumno se autoevalúa comparando su marca con el contorno.

## 2. Cómo está hecho

- **Tecnología**: Next.js (React, App Router, Vercel) + Tailwind. Visor: **Cornerstone3D** (`@cornerstonejs/core`,
  `tools`, `dicom-image-loader`, con vtk.js y WebGL). ~4 MB de JS solo para el visor.
- **Imágenes**: **DICOM reales**, un archivo `.dcm` por corte, 512×512, servidos como archivos estáticos desde
  `dicom.navigatingradiology.com/studies/<estudio>/<serie>/00000.dcm` y cargados con `wadouri` (petición HTTP
  simple, sin servidor PACS ni teselas). Anonimizados (UID con raíz de GDCM). Series de 50 a 592 cortes.
- **Ventana/nivel**: arrastrar sobre la imagen o presets: Partes blandas 400/40, Hígado 150/70, Pulmón 1500/-600,
  Hueso 2000/400, Cerebro 80/40, Angio 600/150. Como es DICOM con unidades Hounsfield, la ventana es real.
- **Móvil**: barra inferior de modos (Scroll · Pan · Window · Reset · Series · Anatomy · AI Guide); el dedo hace
  lo que diga el modo activo; contador «1 / 124» y barra de posición del corte. Sin desbordamiento a 390 px.
- **Etiquetas** (API `/api/studies/<id>/masks`, JSON de ~10 MB para el tórax): dos tipos.
  1. **Contornos**: polígonos cerrados por corte, en píxeles, trazados desde **máscaras de TotalSegmentator**
     (el JSON lo dice: `generator: "TotalSegmentator total --fast"`, `moose`, `lumen`, `craniofacial_structures`,
     `derived_masks`). Es decir: segmentación automática + revisión humana, no dibujo a mano.
  2. **Punteros**: un punto por corte (`pointer: [x, y]`, con marca de interpolado) para lo que la IA no segmenta
     (ácigos, hemiácigos, estaciones ganglionares, segmentos ICA C2-C7).
  Cada estructura: grupo jerárquico con color (Vasos > Venas…), `labelSide`/`labelAnchor` para el rótulo y
  `info.text` (la nota docente). Los grupos se encienden/apagan con interruptores; hay buscador.
- **AI Guide**: servidor `/api/guide` con un LLM (identificadores tipo `call_…`, estilo OpenAI) que **no habla
  libre: llama herramientas** de la app: `show_structure`, `show_section`, `start_quiz`, `start_lesson`,
  `show_step`, `practice_step`, `offer_choices`, `finish_lesson`, `end_activity`. Solo conoce los rótulos y notas
  del estudio («using the labels and notes in this study»). Ejemplo real: «Quiz me on the great veins» →
  `start_quiz` con 9 estructuras (VCI, VCS, troncos braquiocefálicos, yugulares, ácigos…). Gratis: «modelos más
  ligeros con límite diario»; con cuenta, «attending-level».
- **Cuentas**: `/api/me` → `{signedIn:false, tier:null}`. Sin cuenta: ~15 de 113 estructuras con nombre en el
  tórax (vasos), 3 en cardíaco, 10 (segmentos hepáticos) en abdomen, 0 en cráneo, 23 en carótidas; el resto
  aparece como `locked-N` y el panel dice «A free account unlocks all 296 structures, their notes, and outlines».
- **Licencias**: no hay ninguna atribución ni licencia de los casos en la página ni en los datos. Parecen casos
  propios anonimizados (descripciones de serie de equipo Siemens tipo «Body Std. Volume 3.0»), no TCIA ni
  Radiopaedia. **Para nosotros: sus imágenes no se pueden usar.**

## 3. Ellos vs nosotros

| | NavRad Anatomy | Nuestra app |
|---|---|---|
| Imagen | Estudios DICOM completos, se recorren corte a corte | Figuras sueltas (`.article-figure`, ~300 imágenes; Rx/TC del Merino Neumología: tubo ET, SDRA, neumotórax…) |
| Ventana | Real (HU), presets y arrastre | No aplica (JPG fijos) |
| Rotulado | Contornos por corte (TotalSegmentator) + punteros | Texto del pie de figura; la vista Visual rotula esquemas, no imagen real |
| Notas | 2-4 frases por estructura, revisadas | Fichas largas fieles a la fuente, con resaltes y «Ver en el texto» |
| Quiz | «Toca dónde está», autoevaluación | Mayéutica: test, piensa y destapa, encuentra el error, casos que evolucionan; `q.tocar` ya existe para modelos vivos |
| IA | LLM en servidor que maneja la app con herramientas | Ninguna (sin backend por regla) |
| Eco | No | Simulador y atlas de eco propios (nuestro punto fuerte) |
| UCI | Anatomía normal, sin dispositivos | Todo es UCI, pero nada de TC/Rx de dispositivos en formato navegable |
| Cuentas | Preview + cuenta gratis | Sin login (regla) |
| Peso | Next.js + Cornerstone (~4 MB JS) | Estático, sin build, una sola librería (Motion) |

## 4. Las mejores ideas para traer

1. **Visor de cortes propio, ligero** (pila de WebP + desplazamiento con el dedo + contador + barra de posición).
   Sin DICOM en el navegador: los cortes se exportan ya en 2-3 ventanas fijas (mediastino, pulmón, hueso) como
   WebP. Aporta «leer un TC como en el PACS» en el móvil. Esfuerzo: medio (una pieza `core/visor-cortes.js`).
   Necesita: decisión del usuario (pieza nueva; Cornerstone sería otra librería y rompe «sin build»), y vigilar
   peso (~3-6 MB por serie; el repo ya pesa 262 MB).
2. **Casos con licencia abierta + máscaras de TotalSegmentator.** Candidatos: el **conjunto de TotalSegmentator**
   (TC con máscaras, Zenodo), **Medical Segmentation Decathlon** (CC BY-SA 4.0), colecciones de **TCIA** con
   CC BY. Hay que verificar la licencia de cada caso concreto antes (en web, con URL literal, regla 7.2). Aporta
   imagen real legal y rotulada sin dibujar a mano. Esfuerzo: medio-alto (preparación fuera de la app, en Python).
3. **Rotulado por contornos guardados como datos** (polígonos simplificados por corte en `js/data/`, pintados en
   SVG encima del corte) + punteros para lo no segmentable. Encaja con «la imagen no calcula» y con la vista
   Visual (cada estructura con su «Ver en el texto»). Esfuerzo: medio.
4. **Quiz «toca la estructura»** dentro de la Mayéutica: ampliar `q.tocar` para que la respuesta sea un punto
   sobre el corte; a diferencia de NavRad, **sí puntuar** (punto dentro del polígono = acierto) y guardar en el
   progreso de siempre. Aporta lo que NavRad no tiene: corrección y repaso de lo fallado. Esfuerzo: medio.
5. **TC/Rx del paciente de UCI** (lo que ellos no hacen y a nosotros nos sobra): punta del tubo ET, SNG, CVC
   (VCS-AD), Swan, drenajes torácicos, ECMO, neumotórax, derrame, consolidación. Recorrido «comprueba la vía tras
   colocarla» enlazado con Técnicas R1 y Merino Neumología. Esfuerzo: alto. Necesita casos con licencia que
   tengan dispositivos (buscar en TCIA, p. ej. colecciones COVID de UCI) o Rx abiertas (verificar).
6. **Notas docentes cortas por estructura** con la trampa clínica en negrita y estado «revisada/borrador», pero
   escritas desde nuestras fuentes (Merino, Marino…) con su página. Esfuerzo: bajo por estructura.
7. **Barra inferior de modos en el visor** (Desplazar · Mover · Ventana · Series · Anatomía · Preguntas): un dedo,
   un modo; resuelve el conflicto gesto-scroll del móvil. Esfuerzo: bajo dentro de la idea 1.
8. **Presets de ventana con nombre y cifras** (Pulmón 1500/-600…) como contenido de estudio: una ficha que enseñe
   qué es la ventana usando el mismo corte en 3 ventanas. Esfuerzo: bajo. Cifras desde una fuente nuestra.
9. **«Muéstrame…» sin IA**: buscador dentro del visor que salta al corte donde la estructura es mayor y la
   enciende (lo que hace `show_structure`), reutilizando el buscador global. Esfuerzo: bajo-medio.
10. **Lecciones guiadas paso a paso** (`start_lesson`/`show_step`): recorridos escritos por nosotros (p. ej.
    «sistemática de lectura del TC de tórax en UCI»), sin LLM, como un `initSiNoWizard` sobre el visor.
    Pendiente del PIF: rotaciones de Radiología de tórax y Neurorradiología (BITACORA). Esfuerzo: medio.

## 5. Qué NO traer

- Sus imágenes, contornos, notas o textos (sin licencia declarada; además el JSON gratis incluye contornos de
  estructuras bloqueadas: no aprovecharlo).
- Next.js, Cornerstone3D, vtk.js ni ningún build: rompe «sin build ni dependencias» (salvo que el usuario decida).
- El AI Guide con LLM en servidor, cuentas, niveles y límites diarios: rompe «sin backend, sin login».
- DICOM crudo en el navegador: pesado y no hace falta para estudiar con ventanas fijas.
- El quiz sin corrección: nosotros puntuamos y repasamos lo fallado.
- Anatomía normal genérica sin ancla en UCI: nuestro valor es el paciente crítico.

## 6. Lo que no pude ver

- **Ninguna imagen de TC**: el proxy del entorno bloquea `dicom.navigatingradiology.com` (403). Las capturas muestran
  la interfaz, los paneles y el quiz con el visor en negro; los contornos se vieron en los datos JSON, no pintados.
- `/join` y `navigatingradiology.com` no cargaron (bloqueados): no sé precios ni condiciones de la cuenta.
- Contenido con cuenta (notas de las 296 estructuras, guía «attending-level»).
- Cómo se ven el rótulo con línea, el «revelar» y el gesto de pellizco en un móvil real.
- No se verificaron en web las licencias de TotalSegmentator, MSD y TCIA citadas en §4: hay que comprobarlas.

## Capturas (390×844, ×2)

- `/tmp/plan-socialista/rea3/navrad/01-home-390.png` — portada con los visores
- `/tmp/plan-socialista/rea3/navrad/02-ct-chest-390.png` — visor TC tórax (barra de modos, contador 1/124)
- `/tmp/plan-socialista/rea3/navrad/03-ventana-presets-390.png` — presets de ventana/nivel
- `/tmp/plan-socialista/rea3/navrad/04-lista-estructuras-390.png` — árbol de estructuras con interruptores
- `/tmp/plan-socialista/rea3/navrad/05-teaching-point-vcs-390.png` — VCS seleccionada (salta al corte 47)
- `/tmp/plan-socialista/rea3/navrad/06-ai-guide-390.png` — panel del AI Guide (aviso de preview)
- `/tmp/plan-socialista/rea3/navrad/07-quiz-toca-estructura-390.png` — quiz «¿dónde está la VCI?» (1 de 9)
