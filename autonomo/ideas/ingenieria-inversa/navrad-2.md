> Copiado de `alvariitoSW/fiebres-neutropenias` (`autonomo/ideas/ingenieria-inversa/navrad-2.md`) el 30/10/2026. Se hizo para aquella app de UCI: «nuestra app» y sus rutas se refieren a ella. Lo útil para este estudio está en `autonomo/ideas/webs-radiologia.md`.

# NavRad Anatomy, segunda pasada (23/10/2026)

Probado con Playwright a 390×844 (móvil táctil). Tras abrir el usuario `*.navigatingradiology.com`, **los cortes sí cargan** (965 DICOM con 200 en una sesión, ninguno falla). Su JS, sus DICOM y sus JSON se leyeron solo en memoria; en disco solo hay capturas. Etiquetas: **visto** (comprobado), **deducido**, **no visto**.

## 1. Lo nuevo respecto a la primera pasada

- **Ahora hay imagen.** Rótulos, contornos, quiz y lección se han visto pintados sobre cortes reales.
- **Los datos van en dos sitios** (visto). Las *notas, los punteros, el árbol de grupos y las series* vienen **dentro del HTML** de la página (datos de Next.js, 0,24-0,6 MB). El JSON `/api/studies/<id>/masks` solo trae **contornos** (polígonos por serie y corte). La primera pasada lo mezclaba.
- **En la versión gratis hay más de lo que se dijo**: tórax 61 de 296 estructuras con nombre (no 15); las 60 con nota están todas `reviewed`. Las bloqueadas salen como «Sign in to view», pero su punto, su línea y, al encender «todas», **su contorno de color se pintan igual** (visto, captura 63).
- **El quiz no gasta IA**: el LLM solo elige la lista (`start_quiz`); preguntar, revelar y pasar va en el navegador.
- **La lección sí gasta IA en cada paso**: una llamada por cada «Next step». Dos peticiones iguales dieron lecciones distintas (7 y 6 pasos, otro orden).
- **Precarga agresiva**: TC cardíaco descarga ~148 MB de DICOM al abrir. Sin *service worker* ni caché propia.
- **No hay sincronía entre series**: al cambiar de axial a pulmón o a coronal, el corte vuelve a 1. Sin línea de referencia (visto).

## 2. Los 5 visores

Cortes de 512×512 salvo lo indicado. «Libres» = con nombre sin cuenta. «Notas» = notas docentes (todas `reviewed`, de 160 a 620 caracteres; media de 230-385). Los textos no se copian.

| Visor | Series (cortes) | Estructuras / libres / notas | Grupos (nº) | De interés para UCI |
|---|---|---|---|---|
| TC tórax | Axial CE (124), Pulmón axial (124, W1600/L-600), Axial 0,5 mm (592), Coronal (114), Sagital (147), Scout (2), MIP coronal 8 mm (263) | 296 / 61 / 60 | Vasos (venas 17, arterias 14, arterias pulmonares 30), Corazón 22, Vía aérea 30, Pulmón 9, Mediastino 7, Ganglios 22, Pleura 1, Cuello 4, Nervios 11, Hueso 58, Músculo 61, Abdomen 10 | VCS, VCI, yugulares, subclavias y troncos braquiocefálicos (vía central); árbol arterial pulmonar segmentario (TEP); vía aérea (tubo); ácigos |
| TC cardíaco | Angio-TC 1 mm (160), 0,5 mm (640), axial 2 mm (80), coronal (104), sagital (104), pulmón (80) | 69 / 9 / 9 | AD y entrada (libre), VD y salida, AI y venas pulmonares, VI, válvulas y raíz aórtica, coronarias 10, grandes vasos, pericardio 6 | AD, VCS/VCI, seno coronario, septo interauricular y fosa oval (libres); pericardio (derrame); cavidades derechas |
| TC abdomen-pelvis | Axial 3 mm (194) y 5 mm (187), sin contraste 5 mm (179), MPR coronal (94; 634×512), sagital (158; 1072×512), coronal y sagital sin contraste (143; 672×672) | 261 / 13 / 13 | 23 grupos: hígado 13 (libre: segmentos de Couinaud), peritoneo (espacios 9, epiplón y mesenterio 6), vía biliar, páncreas, bazo, suprarrenales, riñón 13, tubo digestivo 27, vasos (arterias 21, venas 17, porta 8), ganglios 27, hueso 40, músculo 40, bases pulmonares 4 | Espacios peritoneales (colecciones), porta, arterias viscerales, riñones y bases pulmonares (derrame) |
| TC cráneo | Cerebro axial (51 y 50), coronal (65 y 63), sagital (49), hueso axial, coronal y sagital (W2700/L350), scout | 194 / 2 / 2 | Duramadre y compartimentos (libre: hoz y tentorio), lóbulos y surcos 24, gris profunda 16, sustancia blanca 13, fosa posterior 17, **sistema ventricular 19, cisternas basales 7**, arterias 12, senos venosos 11, calcificaciones, base del cráneo 45, senos 9, órbitas 10 | Hoz y tentorio (hernias subfalcina y transtentorial), ventrículos y cisternas (HTIC, hidrocefalia), territorios arteriales (isquemia). Casi todo bloqueado |
| Angio-TC carótidas | Axial 2 mm (181), MIP coronal y sagital 10 mm (104 y 119; 776×776), 0,5 mm (1201), cerebro y hueso en 3 planos | 155 / 34 / 34 | Arterias: cayado y troncos 12, ACI 22 (C1-C7 libres), ACE 20, vertebrobasilar 17, polígono de Willis 27, «Look here for aneurysms» 5; venas: senos 15, profundas 5, cuello y tórax 24, corticales y orbitarias 8 | ACI por segmentos, cayado, yugulares (vía central), senos venosos (trombosis) |

**Formato de los datos** (visto en memoria):
- Cada serie: `id`, `seriesNumber`, `description`, `imageCount`, `rows/columns`, `defaultVoi` (ventana de inicio) y la lista de URL (un `.dcm` por corte).
- Cada grupo: `id`, `name`, `parentId` (subgrupo), `color`, `order` y `locked`.
- Cada estructura: `id`, `name`, `groupId`, `parentId` (jerarquía: p. ej. ACI > C1…C7), `color`, `maskColor`, `labelSide`, `labelAnchor` (0-1: altura del rótulo), `hasLabel`, `defaultOff`, `altName`, `marker` y `annotations` por serie y corte.
- Cada anotación es un `pointer:[x,y]` con `interpolated`, o un polígono `{points:[[x,y]…], closed:true}`. Proporción en el tórax: 3.449 punteros frente a 102 polígonos en el HTML, más 8.649 polígonos en el JSON de la serie axial.
- La nota es `info:{text, status}`. Los ids `s_station_*` y `s_scaffold_*` son estructuras de puntero; las de máscara llevan `source` con el nombre de TotalSegmentator.
- Peso de `masks`: tórax 9 MB, abdomen 8 MB, cardíaco 2 MB, carótidas 0,44 MB, cráneo 0,07 MB.
- Generador por estudio: `total --fast`, `moose`, `derived_masks`, `craniofacial_structures` y `lumen`.

## 3. Lección, guía y quiz paso a paso

**Guía (panel «Anatomy Guide»)**: tres atajos («Show me…», «Quiz me», «Teach me…»), que solo enfocan una caja de texto. También hay un botón «Video Guide», sin vídeo visible (no visto). Al abrirse comprueba `GET /api/guide?study=` → `{ok, available}`. Cada turno es un `POST /api/guide` con todo el historial. Responde en JSON (sin streaming) con `messages` y `actions`. El navegador ejecuta la acción y devuelve el resultado como mensaje `tool`: nombre, serie, corte, tipo «dot and mask» y la nota.

**Lección** (visto, «Teach me the great veins of the chest»):
1. `start_lesson {title, introduction, steps:[{structureId, practice}]}`: 6-7 pasos, 1-2 marcados como práctica. Le siguen otra llamada y `show_step {index, teaching}`.
2. Cada paso salta a la serie y al corte de la estructura. La enciende y apaga el resto. Abre bajo la imagen la tarjeta con la nota (con la trampa clínica en negrita) y en el panel 2-3 frases que acaban en pregunta abierta. Abajo, «Next step · End» y la caja «Answer, or ask a question…».
3. `practice_step {index, say}`: «Where is the Azygos Vein? Click the image to place your marker, drag to adjust, then reveal». Arriba: «Scroll to find it · tap to place your marker». Botón «Skip to reveal».
4. Al poner la marca sale «Reveal». Al revelar, salta al corte de referencia y pinta tu marca (anillo blanco) y el punto de referencia unidos a su rótulo. Leyenda: «Your marker / Reference». Debajo la nota y el texto «Compare your marker with the reference». Botón «Continue».
5. `finish_lesson {say}` y botón «End lesson». **`offer_choices` no salió** en dos lecciones (no visto).

**Quiz** («Quiz me on the pulmonary arteries»):
- `start_quiz {title, structureIds[12-15], say}` con estructuras de puntero.
- Luego, local y sin llamadas: «Question N of 15», poner la marca, «Reveal» y «Next structure».
- **No puntúa, no mide distancias ni dice acierto o fallo, y no repasa lo fallado.** Al revelar se ve la referencia en su corte, aunque tu marca esté en otro: no compara la altura.
- La pantalla final no se vio (se llegó a la 14 de 15).

## 4. UX móvil y rendimiento

- **Barra de modos**: Scroll · Pan · Window · Reset | Series · Anatomy · AI Guide. Un dedo hace lo que diga el modo (visto): en Scroll, arrastrar ~120 px pasó 25 cortes; en Window, el mismo gesto llevó W/L de 400/40 a 560/520; la rueda del ratón pasa un corte por paso.
- **Barra de posición**: una línea de 3 px encima de la barra de modos (role `progressbar`).
- **Contador**: abajo, «41 / 124 · W 400 · L 40». En cráneo y cardíaco, a 390 px, el nombre largo de la serie **se monta sobre el contador** (fallo suyo, capturas 50).
- **Pellizco y doble toque**: simulados por CDP, sin efecto visible. Queda «no comprobado» en un dedo real.
- **Presets de ventana**: hoja con «Drag on the image to adjust, or pick a preset» y Soft tissue 400/40, Liver 150/70, Lung 1500/-600, Bone 2000/400, Brain 80/40, Angio 600/150. Cada serie arranca con su propia ventana (pulmón 1600/-600, cerebro 80/40, hueso 2700/350, angio 450/70 o 600/80).
- **Rótulos**: punto de color sobre la estructura, línea quebrada fina del color del grupo y píldora con el nombre, en dos columnas a los lados. Con muchas estructuras se apilan por encima y por debajo del cuerpo (el tórax tiene más de 30 rótulos por corte: **satura a 390 px**).
- **Rótulo tocado**: borde blanco y línea gruesa. En la lección, el resto se atenúa.
- **Contornos**: relleno translúcido de color (aorta rosa, vasos pulmonares azul y rojo).
- **Bloqueados**: «Sign in to view» con el mismo punto y línea; «•••» indica que hay hijos.
- **Panel Anatomía**: buscador «Search anatomy…», «ALL STRUCTURES» con un interruptor, y árbol desplegable de grupos y subgrupos, cada uno con su interruptor. Debajo, el bloque «Unlock the full atlas» con NavRad y Register.
- **Buscador**: **filtra los rótulos del corte actual** («Showing matches for "azyg" · Show all»). **No salta** al corte: si la estructura no está en él, la imagen queda sin rótulos. El salto lo da la guía («Show me…») o la lección.
- **Peso al abrir** (cuerpos sin comprimir): JS: 5,5 MB (23 archivos, el mismo en todos los visores) + ~10 MB de «otros» (sin desglosar; deducido: HTML con datos y decodificadores). DICOM precargado: tórax 17 MB, cráneo 6 MB, abdomen 23 MB, carótidas 35 MB, **cardíaco 148 MB** (precarga la serie de 0,5 mm entera). De cada serie no activa baja solo el corte central, como miniatura. Tiempo hasta `networkidle`: 14-23 s (cardíaco, 75 s).
- **Sin conexión**: la serie ya precargada se sigue recorriendo. Una serie no precargada se queda en un círculo de carga. Al recargar, error del navegador. Sin *service worker* ni Cache Storage. Guarda en `localStorage` (no se inspeccionó el contenido).

## 5. Casos abiertos con licencia

La red del entorno **bloquea** zenodo.org, images.radiopaedia.org, registry.opendata.aws, cancerimagingarchive.net y medicaldecathlon.com (túnel denegado o DNS). Las licencias salen de resultados de búsqueda: **ninguna verificada en origen**. Para verificarlas, el usuario tendría que abrir esos dominios en la red del entorno.

| Dataset | Qué trae | Licencia (como sale en la búsqueda) | URL | Verif. | Útil para UCI |
|---|---|---|---|---|---|
| TotalSegmentator v2 | 1.228 TC con máscaras de 117 estructuras (Basilea) | «CC-BY-4.0» solo en una copia de Hugging Face; el campo de Zenodo no se vio | https://zenodo.org/records/10047292 | No | Alta: anatomía normal rotulada, vasos de vía central, cavidades y pulmón |
| Medical Segmentation Decathlon | 10 tareas (hígado, pulmón, páncreas, bazo, colon, vasos hepáticos, corazón RM, cerebro RM…) | «All data were made available online under Creative Commons license CC-BY-SA 4.0» (artículo arXiv 1902.09063); ojo: alguna tarea de origen (LiTS) sería CC-BY-NC-SA | http://medicaldecathlon.com/ | No | Media: órganos, poca patología de UCI |
| TCIA «CT Images in COVID-19» | TC de tórax de 632 pacientes (NIfTI) + 121 TC de 29 | CC BY 4.0 según el listado de TCIA, más la «TCIA Data Usage Policy» | https://wiki.cancerimagingarchive.net/display/Public/CT+Images+in+COVID-19 | No | Alta: consolidación y vidrio deslustrado de pacientes graves (deducido: puede haber tubos y vías) |
| TCIA COVID-19-NY-SBU | Rx, TC de tórax y RM con datos clínicos (incl. UCI) | No encontrada | https://www.cancerimagingarchive.net/collection/covid-19-ny-sbu/ | No | Muy alta si la licencia lo permite (Rx de UCI con dispositivos) |
| TCIA LIDC-IDRI | ~1.010 TC de tórax con nódulos anotados | «Creative Commons Attribution 3.0 Unported» (wiki TCIA, versión archivada) | https://wiki.cancerimagingarchive.net/x/hIRXAQ | No | Baja: nódulos, no UCI |
| RSNA Intracranial Hemorrhage | TC de cráneo de 4 centros, 5 subtipos de hemorragia | «non-commercial purposes only, including academic research and education» (AWS Open Data) | https://registry.opendata.aws/rsna-intracranial-hemorrhage-detection | No | Alta para hemorragia; uso solo no comercial y cita «Copyright RSNA, 2019» |
| CQ500 (Qure.ai) | 491 TC de cráneo: hemorragia, fractura, efecto de masa, desviación de línea media | «CC BY-NC-SA 4.0» (de un artículo de terceros) | headctstudy.qure.ai/dataset | No | Muy alta: hernia y desviación de línea media |
| SIIM-ACR Pneumothorax | Rx de NIH con máscaras de neumotórax | «custom license» (Dataset Ninja); son reglas de competición de Kaggle | https://siim.org/page/pneumothorax_challenge | No | Alta, pero con licencia dudosa |
| RANZCR CLiP | 30.083 Rx (ChestX-ray14) con 11 clases de posición de tubo ET, SNG, CVC y Swan | No encontrada (Kaggle + NIH) | https://pmc.ncbi.nlm.nih.gov/articles/PMC8553862/ | No | Muy alta: exactamente la posición de dispositivos |
| Radiopaedia | Casos de toda la radiología, con dispositivos y patología de UCI | «modified Creative Commons Attribution-Non-commercial-Share Alike 3.0 Unported»; algunos casos van como CC BY 3.0 o BY-SA 3.0, caso a caso | https://images.radiopaedia.org/licence | No | Muy alta, con NC-SA: hay que citar autor, enlace al caso y licencia |

## 6. Ideas para la clínica de UCI con nuestra app

Sin backend, login ni librerías, y con texto desde nuestros PDF.

1. **«¿Dónde está la punta?»** sobre una Rx o un corte (tubo ET, CVC, SNG, drenaje): se toca, se compara con la zona correcta (polígono) y **sí se puntúa**, con repaso de fallos en la Mayéutica (`q.tocar` ampliado). Pie de cama: comprobar el dispositivo tras colocarlo. Esfuerzo medio. Necesita casos con licencia (RANZCR CLiP o Radiopaedia caso a caso) y la fuente de las referencias (Merino Neumología, Técnicas R1).
2. **Visor de pila ligero** (WebP en 2-3 ventanas, arrastre vertical, contador y barra de 3 px; sin DICOM). Evita su fallo: precargar 148 MB. Mejor perezoso, con unos 60 cortes por caso. Esfuerzo medio. Necesita decisión de arquitectura del usuario (pieza `core/visor-cortes.js`) y vigilar el peso del repositorio.
3. **Recorridos clínicos fijos, sin IA**: «sistemática de la Rx de UCI», «TC de cráneo en el coma» (cisternas, ventrículos, hoz, tentorio, línea media), «TEP en angio-TC». Paso → salta al corte, enciende la estructura, nota con la trampa en negrita y una pregunta. Es su `start_lesson/show_step`, escrito a mano desde Marino o Merino. Esfuerzo medio. Necesita PDF de neurorradiología o tórax.
4. **Buscador que salta al corte de mayor tamaño** de la estructura (su buscador no salta: lo mejoramos). Esfuerzo bajo dentro de la idea 2.
5. **Casos que evolucionan con imagen** («día 1: Rx tras intubar; día 3: atelectasia; día 5: neumotórax tras CVC»), con caso clínico de REGLAS §8 y preguntas de «encuentra el error» sobre la imagen. Esfuerzo medio-alto. Necesita 2-3 casos Radiopaedia con licencia verificada.
6. **Lo mismo en tres ventanas** (mediastino, pulmón, hueso) para enseñar qué se ve en cada una: derrame frente a consolidación, neumotórax en ventana de pulmón. Esfuerzo bajo. Las cifras W/L, de una fuente nuestra.
7. **Hernias y HTIC en dos cortes**: normal frente a desviación de línea media o borramiento de cisternas, con contornos SVG encima. Esfuerzo medio. Necesita CQ500 o RSNA (no comerciales: encajan con una app de estudio, pero decide el usuario) y un PDF de neurocríticos.
8. **Notas por estructura con «Ver en el texto»** que enlazan a nuestras fichas (VCS → vía central en Técnicas R1; ácigos → colaterales). Esfuerzo bajo por estructura. Necesita el PDF de cada nota.
9. **Contornos ligeros**: guardar polígonos simplificados y punteros como en su formato (punteros donde no hay máscara). Ellos usan 3.449 punteros frente a ~100 polígonos en el HTML: el puntero basta para enseñar. Esfuerzo bajo-medio. Necesita preparar los datos fuera de la app.

## 7. Lo no visto

- Contenido con cuenta: nombres y notas de las estructuras bloqueadas y la guía «attending-level». Precio y condiciones de la cuenta.
- `offer_choices`, `show_section` y `end_activity` en uso; la pantalla final del quiz; qué hace la IA si escribes una respuesta en la caja.
- El «Video Guide» (sin vídeo ni iframe visibles).
- Pellizco y doble toque en un dedo real; el contenido de `localStorage`.
- Las licencias en origen (dominios bloqueados, §5) y si NavRad declara la procedencia de sus casos (no se encontró).

## Capturas (`/tmp/plan-socialista/rea-navrad2/`, 390×844 ×2)

Tórax: `30-torax-rotulos-por-defecto` (rótulos y «Sign in to view»), `61-torax-ventana-pulmon-rotulos`, `60-presets-ventana`, `25-serie-pulmon`, `26-serie-coronal`, `40-svc-seleccionada`, `63-arbol-vessels` (contornos bloqueados pintados), `31-panel-anatomia`, `32-buscar-azyg`, `41-buscar-trunk`. Otros visores: `50-<visor>-corte-medio` (cráneo, cardíaco, abdomen, carótidas, tórax). Lección: `12-leccion-inicio`, `13-leccion-paso0..8` (paso 3: VCS encendida con nota), `16-practica-marca`, `17-practica-revelada`. Quiz: `44-quiz-pregunta1`, `45-quiz-revelado-0/1/11/12`, `47-quiz-final`. Sin conexión: `51`, `52`, `53`. Guía: `10`, `11`. Gestos: `21-pellizco`, `22-doble-toque`. (Todas `.png`.)
