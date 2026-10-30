> Copiado de `alvariitoSW/fiebres-neutropenias` (`autonomo/ideas/ingenieria-inversa/radiologyassistant.md`) el 30/10/2026. Se hizo para aquella app de UCI: «nuestra app» y sus rutas se refieren a ella. Lo útil para este estudio está en `autonomo/ideas/webs-radiologia.md`.

# The Radiology Assistant (radiologyassistant.nl): informe de ingeniería inversa (23/10/2026)

Playwright a 390×844 y `curl` en memoria; de ellos solo se guardaron capturas. Complementa `navrad.md`. Etiquetas: **visto**, **deducido**, **no visto**.
## 1. Qué es
- Web docente gratuita de radiología, en inglés, creada por Robin Smithuis (radiólogo, Alrijne, Leiden) para la
  Sociedad Holandesa de Radiología. Sin ánimo de lucro (estatus ANBI); lo de la app va a Medical Action Myanmar. **Visto** (About Us).
- Unos 150 artículos en 9 secciones: abdomen, mama, cardiovascular, tórax, cabeza-cuello, musculoesquelético,
  neurorradiología, pediatría y «more» (protocolos de contraste en TC, RECIST, cómo hacer ilustraciones). **Visto** (menú).
- Para residentes de radiología y radiólogos, centrada en problemas clínicos frecuentes. Cada artículo lleva sus autores (a menudo 2-5, de hospitales holandeses) y la fecha con sus actualizaciones
  (p. ej. Rx de tórax básica: 2013, actualizada el 15/10/2025; HRCT: 2006, 2022 y 2025). **Visto**.
## 2. Cómo está hecho
- **Tecnología** (**visto**): CMS Statamic (PHP; imágenes en `/assets/` y `/img/containers/main/`), Tailwind, jQuery 3.4.1
  y jquery-mousewheel por cdnjs, un `dist.js` propio (~97 kB) con Fancybox (caja de luz) y su visor de pilas.
  Google Analytics tras un aviso de cookies («Optimal», que además activa los vídeos de YouTube, o «Minimal»).
- **Formato del artículo** (**visto**): título, autores y centro, fecha, un recuadro «what you will learn», índice
  de anclas (de 8 a 40 enlaces), y después **bloques pareados imagen + texto**: a la izquierda la figura, a la derecha
  una tarjeta blanca de 2-6 frases con negritas y viñetas. En el móvil se apilan (figura arriba, texto debajo).
  Entre 1.800 y 7.800 palabras y entre 20 y 120 imágenes por artículo. **Sin tablas HTML**: las tablas de
  diagnóstico diferencial (p. ej. agua/pus/sangre/células en la consolidación) son **imágenes**.
- **Figuras**: casi todas son imágenes reales (Rx, TC, RM) con **rótulos y flechas dibujados encima** a mano
  (**deducido**: tienen un artículo de cómo hacerlas en Keynote), y esquemas propios muy limpios firmados «RS»: las meninges,
  el lobulillo secundario, la consolidación con broncograma… Al tocarlas se abren en una caja de luz.
- **Pilas de imágenes («StackViewer»)**, su truco principal (**visto** en el HTML y en su JS): un `<div>` con
  `data-image-set="a.jpg,b.jpg,…"`, una lista de JPG ya exportados. Se pasa de una a otra con la rueda del ratón,
  con flechas ▲▼ o con una barra lateral; en el móvil hay un botón **«Enable Scroll»** que bloquea el desplazamiento de
  la página y deja que el dedo pase las imágenes (cuántas pasa depende de lo que recorre el dedo y de la altura de la caja).
  Precarga las imágenes al activarlo. Usos: **2 imágenes = «antes / después» o «sin / con rótulos»** (la placa actual frente a la previa
  en el caso de la IC sutil); **5-35 imágenes = TC corte a corte con los segmentos pulmonares coloreados y rotulados**
  (Lung Segments: pilas de 35, 29, 19, 18, 12…; hemorragia intracraneal traumática: 12-29). No es DICOM: no hay ventana
  ni medida. Probado: las flechas cambian el corte; en el móvil, tocar la pila **también abre la caja de luz** con
  una segunda copia (fricción de uso, **visto**). El deslizamiento con el dedo no lo pude provocar en la prueba (sí está en el código).
- **Casos** narrados en el texto («mira esta placa… ahora mira la previa»). **Ni quiz ni preguntas** en lo leído.
- **Vídeos**: en algunos artículos (sobre todo de abdomen: «closed-loop obstruction with video», «Bowel ischemia - Video
  Lectures») hay vídeos de YouTube incrustados y algún `.mp4` propio. Ninguno en los 11 artículos de tórax y neuro que miré.
- **«4-pattern approach»** (Rx de tórax, enfermedad pulmonar): todo lo que se ve se clasifica en 4 patrones
  (consolidación, intersticial, atelectasia, nódulos y masas; se añade «densidad disminuida o lucencias») y cada uno
  tiene sus hallazgos clave en viñetas, su diagnóstico diferencial (en imagen) y su versión en HRCT. En HRCT: patrón
  reticular, nodular (con un **algoritmo en flujograma** perilinfático / centrolobulillar / aleatorio), alta y baja
  atenuación, y después la distribución (superior/inferior, central/periférica) y los hallazgos asociados.
- **App** «Radiology Assistant 2.0» (iPhone/iPad, W. Veldhuis): gratis con suscripción por categoría, sin conexión,
  contenido que se actualiza dentro. **No vista por dentro** (https://apps.apple.com/app/id1173853906).
- **Licencia, literal** (página Disclaimer, https://radiologyassistant.nl/disclaimer, **visto**):
  > «The information given on this site is for educational purposes only. We can not accept responsilbility for the
  > acts of any physicians or any other individual who receive information on any medical procedures acquired through
  > this website. We accept no legal responsibility for any injury or damage to persons or property from any of the
  > suggestions or material discussed herein. The images and illustrations on this site may be reproduced for
  > educational purposes with due credit being given to the original author and the Radiology Assistant.»
  - No hay licencia formal (ni CC) ni © en los artículos. **De los textos no dice nada**: no se copian.
  - Lectura: las **imágenes e ilustraciones** se pueden reproducir con fines docentes **citando al autor y a RA**. No
    aclara si se pueden modificar (p. ej. traducir los rótulos) ni el uso comercial. Por nuestra regla (§7.9 y el encargo),
    lo seguro es **enlazar**; meter alguna figura suya con crédito sería una **decisión tuya** caso a caso.
## 3. Ellos frente a nosotros
| | Radiology Assistant | Nuestra app |
|---|---|---|
| Para quién | Residente y adjunto de radiología | R1 de UCI a pie de cama |
| Formato | Bloques figura + 2-6 frases, índice de anclas | Cuaderno de campo: fichas, acordeones, resaltes, «Ver en el texto» |
| Imagen | Rx/TC reales con rótulos y flechas encima; esquemas propios | `.article-figure` sueltas (Merino Neumología: 16 figuras con pie, sin rótulos encima) |
| Pilas | StackViewer: lista de JPG que se pasa con el dedo o la rueda | No hay |
| Tablas | Diferenciales como imagen (no se buscan ni se leen bien en el móvil) | `.data-table` nativas |
| Algoritmos | Flujogramas en imagen | Asistente Sí/No (`initSiNoWizard`), recreados |
| Preguntas | Ninguna; casos narrados | Quiz, Mayéutica (piensa y destapa, encuentra el error, casos que evolucionan) |
| Simulación | Ninguna | Modelos vivos, eco, vista Visual |
| UCI | Dispositivos (Swan, BCIA, Impella, LVAD) en una sola página; el resto es radiología general | Todo UCI, pero el PIF de Radiología está vacío |
| Licencia | Imágenes reproducibles con crédito; textos sin permiso | Contenido propio desde PDF |
## 4. Ideas para traer
**PIF de Radiología** (rotaciones vacías en `js/data/pif-rotaciones.js`: «Radiología — tórax», objetivos semiología de la Rx,
patrones, técnicas UMI y sus complicaciones, eco torácica, TC/TCAR; «Neuro-Radiología»: técnicas, ACV isquémico frente a
hemorrágico, HTIC, epidural/subdural, hipoxia, catéteres intracraneales, HSA):
1. **Bibliografía enlazada de cada rotación** con los artículos de RA (lista abajo), como `.biblio-link` + `.biblio-nota`
   en una línea: «para qué sirve» y «qué mirar». Es útil ya, aunque falten los PDF. Esfuerzo pequeño. Necesita: nada (solo enlaces).
2. **Pieza «pila de imágenes» propia** (`core/pila-imagenes.js`): lista de WebP, dedo o flechas, contador «3/12», y un
   modo **«con / sin rótulos»** (2 imágenes) para el ejercicio «mira, piensa, destapa». Arregla su fricción: un solo gesto
   claro y sin caja de luz duplicada. Encaja con la idea 1 de `navrad.md` (visor de cortes) en versión ligera: sin DICOM ni
   ventana. Esfuerzo medio. Necesita: tu decisión (pieza nueva) e imágenes con licencia (casos propios anonimizados según
   §7.8, o abiertos y comprobados; las de RA, solo si decides reproducirlas con crédito).
3. **Sistemática de la Rx de tórax en la UCI** como recorrido paso a paso (`initSiNoWizard` o Mayéutica): dispositivos →
   «zonas escondidas» → silueta → 4 patrones → compara con la placa previa. Su orden de lectura es la idea; el contenido,
   de nuestra fuente. Esfuerzo medio. Necesita: el PDF de la rotación (o capítulos del Marino/Merino con Rx).
4. **Los 4 patrones como modelo de estudio**: una ficha por patrón con «hallazgos clave» en `.term-chips`, el diferencial
   en `.data-table` nativa (no en imagen) y preguntas «encuentra el error» («consolidación con pérdida de volumen» → es
   atelectasia). Esfuerzo medio. Necesita: PDF de fuente (sus cifras y listas no son fuente).
5. **Algoritmo de nódulos en HRCT** (perilinfático / centrolobulillar / aleatorio) y el **lobulillo secundario** como vista
   Visual recreada en SVG: es un mecanismo de manual para la vista Visual. Esfuerzo medio. Necesita: PDF (TC/TCAR de la rotación).
6. **Neuro: espacios meníngeos** (epidural frente a subdural frente a HSA) como esquema recreado y animado (Motion): la
   capa que se llena y por qué cruza o no las suturas. Enlaza con la calculadora de Marshall del Manual UMI. Esfuerzo medio.
   Necesita: PDF de la rotación de Neurorradiología.
**Resto de la app**
7. **Rótulos encima de las figuras** de Merino Neumología (tubo ET, neumotórax a tensión, SDRA): capa SVG con flechas y
   rótulo que se enciende con «Ver en el texto», recreada, sin tocar la imagen. Esfuerzo pequeño-medio. Necesita: nada.
8. **«Compara con la placa previa»** en los casos de la Mayéutica (pila de 2). Pequeño, tras la idea 2.
9. **Enlaces cruzados desde fichas existentes**: «Cardiovascular devices» (Swan, BCIA, Impella) desde Técnicas R1 y la guía de IC;
   «Acute Aortic Syndrome», «CT in Abdominal Trauma», «Acute Pancreatitis», «Bowel ischemia» desde donde toque. Esfuerzo
   pequeño. Necesita: nada.

**Artículos de RA más útiles para un R1 de UCI** (todas las URL abiertas con respuesta 200 el 23/10/2026):
- Chest X-Ray - Basic Interpretation: https://radiologyassistant.nl/chest/chest-x-ray/basic-interpretation · Chest X-Ray - Lung disease (4 patrones): https://radiologyassistant.nl/chest/chest-x-ray/lung-disease
- Chest X-Ray - Heart Failure: https://radiologyassistant.nl/chest/chest-x-ray/heart-failure · Cardiovascular devices (Rx: Swan, BCIA, Impella, LVAD, MP, DAI): https://radiologyassistant.nl/cardiovascular/devices/cardiovascular-devices
- HRCT - Basic Interpretation: https://radiologyassistant.nl/chest/hrct/basic-interpretation · HRCT - Common diagnoses: https://radiologyassistant.nl/chest/hrct/common-diseases
- Lung Segments and Bronchi: https://radiologyassistant.nl/chest/lung-anatomy/lung-segments · Cardiovascular Pearls on Chest CT: https://radiologyassistant.nl/chest/pearls/cardiovascular-pearls-on-chest-ct-2
- Acute Aortic Syndrome: https://radiologyassistant.nl/cardiovascular/thoracic-aorta/acute-aortic-syndrome · Traumatic Intracranial Hemorrhage: https://radiologyassistant.nl/neuroradiology/hemorrhage/traumatic-intracranial-haemorrhage
- Non-traumatic Intracranial Hemorrhage: https://radiologyassistant.nl/neuroradiology/hemorrhage/non-traumatic-intracranial-hemorrhage · Imaging in Acute Stroke: https://radiologyassistant.nl/neuroradiology/brain-ischemia/imaging-in-acute-stroke
- Vascular territories of the Brain: https://radiologyassistant.nl/neuroradiology/brain-ischemia/vascular-territories · Cerebral Venous Sinus Thrombosis: https://radiologyassistant.nl/neuroradiology/sinus-thrombosis/cerebral-venous-thrombosis
- Cervical injury: https://radiologyassistant.nl/neuroradiology/spine/cervical-injury · CT in Abdominal Trauma: https://radiologyassistant.nl/abdomen/acute-abdomen/ct-in-trauma
- Acute Pancreatitis: https://radiologyassistant.nl/abdomen/pancreas/acute-pancreatitis
## 5. Qué NO traer
- Sus textos (sin permiso); sus imágenes, solo con tu decisión expresa; sus diferenciales en imagen (nosotros, `.data-table`).
- jQuery, Fancybox, Statamic, Analytics, YouTube incrustado (cookies) ni la suscripción de su app; tampoco el doble toque de su pila.
- Artículos largos sin preguntas. Sus cifras (p. ej. índice cardiotorácico o medidas de la aorta): sirven para saber qué buscar, no son fuente (§7.1).
## 6. Lo no visto
- La app de iOS por dentro (de pago por categorías). Los vídeos (no los reproduje; YouTube depende de aceptar cookies).
- El deslizamiento con el dedo en la pila en un móvil real (sí las flechas; el gesto, solo leído en su código).
- El proxy bloqueó cdnjs y Google en la prueba (jQuery no cargó; pila y caja de luz sí iban).
- Musculoesquelético, pediatría, mama y cabeza-cuello (fuera del encargo). «Guidelines for authors» da 404; no hay más licencia que el Disclaimer.
## Capturas (390×844, ×2) en /tmp/plan-socialista/rea-ra/radiologyassistant/
01-cxr-portada-indice · 02-cxr-caso-placa-previa · 03-cxr-signo-silueta · 04-4patrones-portada · 05-4patrones-consolidacion
· 06-hrct-reticular · 07-hrct-tabla-dd (diferencial en imagen) · 09-segmentos-pila-corte1 (pila rotulada con «Enable Scroll»)
· 10-segmentos-pila-tras-deslizar (caja de luz duplicada) · 11-neuro-hemorragia-portada · 12-neuro-meninges (esquema RS)
· 13-neuro-realce-intro · 14-dispositivos-swan · 15-disclaimer · 16-portada
