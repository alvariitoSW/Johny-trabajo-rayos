> Copiado de `alvariitoSW/fiebres-neutropenias` (`autonomo/ideas/ingenieria-inversa/navrad-3.md`) el 30/10/2026. Se hizo para aquella app de UCI: «nuestra app» y sus rutas se refieren a ella. Lo útil para este estudio está en `autonomo/ideas/webs-radiologia.md`.

# NavRad Anatomy, pasada 3: UCI, dispositivos e HTIC (25/10/2026)

Lo previo (`navrad.md`, `navrad-2.md`) no se repite. Solo vigía + lo que falta para UCI. Playwright 390×844; los datos se leyeron en memoria (nada suyo
guardado; abajo solo nombres de estructuras y números de corte, que son hechos). Etiquetas: **visto** / **deducido** / **no visto**.

## 1. Vigía (piezas frente a lo anotado)
- JS de los visores: **23 archivos, 5.516.277 B** en `ct-chest` y en `ct-head` (antes «5,5 MB, 23 archivos»): **sin cambios** (visto). Home: 8 chunks, `/api/me` igual.
- Datos: tórax 296 estructuras, 7 series, 16 grupos; cráneo 194 estructuras, 9 series, 17 grupos: **iguales** que en la 2.ª pasada. Las rutas `/viewer/ct-chest`, `ct-head`,
  `ct-abdomen-and-pelvis`, `cardiac-ct`, `cta-carotids-2` siguen. El «Log in» ahora apunta a `app.navigatingradiology.com/anatomy/launch`; despliegue Vercel con `dpl_…` nuevo (visto).
- Precarga de DICOM: 253 `.dcm` en el tórax y 89 en el cráneo al abrir. Un bloqueo de `static.cloudflareinsights.com` por el proxy (analítica; irrelevante).
- Conclusión: nada que re-estudiar; sin novedades de producto.

## 2. Qué trae para dispositivos (visto: nombres libres en la vista gratis)
Tórax, grupos: Vessels (libres: Veins, Arteries, Pulmonary Arteries) y bloqueados «Heart, Airways, Lungs, Bones, Abdomen, Mediastinum, Neck, Nerves, Muscles, Nodes, Pleura».
**No hay ninguna estructura «dispositivo»** (ni tubo, ni catéter, ni drenaje): es anatomía normal. Pero la vía de una vía central está entera y libre:
vena yugular interna D/I → subclavia D/I → tronco braquiocefálico D/I → **vena cava superior** → (aurícula derecha, bloqueada), más **arco de la ácigos**,
tronco pulmonar, arterias pulmonares D/I (y árbol segmentario A1-A10), aorta ascendente/cayado/descendente, tronco braquiocefálico, carótidas, subclavias, vertebrales,
mamarias internas, venas pulmonares, VCI. Carina, tráquea y bronquios **existen pero bloqueados** (grupo Airways con candado; nombres no vistos). 61 de 296 con nombre y
nota (60 «reviewed»).
Cráneo: de 194 estructuras **solo 2 libres: Falx Cerebri y Tentorium Cerebelli** (grupo «Dura and Compartments»). Los grupos bloqueados dan la lista de lo que hay:
ventrículos, cisternas basales, lóbulos y surcos, ganglios, sustancia blanca, fosa posterior, vasos y senos venosos, calcificaciones fisiológicas, base del cráneo,
senos y orbitas. Nombres concretos de cisternas y ventrículos: **no vistos** (candado).

## 3. Cortes de referencia (pares de prueba del quiz: estructura → serie y corte; visto en los datos)
Corte = índice basado en 0 dentro de la serie. Sirven para que nuestro quiz «¿dónde está?» se pruebe contra el original; no son fuente clínica.
1. **Vena cava superior** → axial con contraste (124 cortes): cortes 34-58, a la derecha de la aorta ascendente (42-64); **el arco de la ácigos entra en 41-43** (por detrás).
   Es el nivel útil para la punta de una vía central: carina/arco de la ácigos, unión VCS-AD. (No visto: la ubicación exacta de la carina; está bloqueada.)
2. **Yugular interna derecha** → axial 0-22; **tronco braquiocefálico derecho** 20-34; **tronco arterial braquiocefálico** 24-34; **cayado aórtico** 34-41.
   Orden craneocaudal que recorre una vía yugular: IJ (0-22) → braquiocefálica (20-34) → VCS (34-58).
3. **Tronco pulmonar** → 46-55; **arteria pulmonar derecha** 48-53 (nivel de la ventana aortopulmonar bajo el cayado 34-41). Útil para TEP y para el Swan.
4. **Hoz del cerebro** → cráneo, axial de cerebro (51 cortes): 4-28; coronal (65 cortes): 13-49. Su nota (paráfrasis): se mide el desplazamiento de la línea media respecto a la hoz,
   y herniación subfalcina es cerebro desplazado bajo su borde libre; mirar sangre fina junto a la hoz.
5. **Tentorio del cerebelo** → axial 26-32; coronal 14-25. Nota: herniación transtentorial hacia abajo (o hacia arriba) por su apertura alrededor del mesencéfalo; la sangre subdural
   fina aquí se escapa en axial y se ve mejor en coronal.
Formato de cada nota (visto): 2-4 frases, con la trampa clínica en negrita; la de la VCS avisa de que la mezcla de contraste simula un trombo.

## 4. Lo que falta (no visto) y límites
- No hay series de **Rx de tórax** ni dispositivos; no hay TC con hemorragia, hernia ni TEP (anatomía normal de un solo paciente). Ver HTIC con ellos es imposible; solo los compartimentos.
- Las estructuras clave de HTIC (ventrículos, cisternas, surcos, senos) están tras el login: **no se pueden estudiar** sin cuenta (y no las usaríamos).
- Licencia de casos: ninguna declarada (ya anotado): sus imágenes no se pueden usar. Vigía de pruebas: no se miró el contenido de `localStorage`.

## 5. Guardia frente a estudio
- **Guardia**: NavRad no sirve en la cama (anatomía normal, sin dispositivos, ~150 MB de precarga). Su valor es la **idea**: saltar a «el corte donde está la unión VCS-AD» y compararlo.
- **Estudio**: orientarse en un TC de tórax (nivel de la carina, ácigos, tronco pulmonar) y de cráneo (hoz, tentorio) con corte-referencia puntuado, que NavRad no puntúa.
- **Lo nuestro**: 14 figuras de Rx/TC de Merino Neumología (sin rótulos encima, sin pila); Técnicas R1 con enlaces; objetivos de PIF vacíos. Falta la pieza de «corte con corrección».

## 6. Megaproyecto: 2 ideas más desde NavRad (6 en `radiologyassistant.md`)
7. **«¿Dónde está la punta?»** puntuado: se toca la punta de la vía en una Rx/TC y se compara con una zona (polígono) de la referencia (zona VCS-AD u otra, solo con la cifra de nuestro PDF).
   Guardia: «¿está bien colocada?» a pie de cama con la figura al lado. Estudio: Mayéutica con `q.tocar` ampliado (punto en polígono = acierto) y repaso de fallos. Esfuerzo medio.
   Necesita: PDF Marino (acceso vascular, caps. 1-4) y Merino para las zonas correctas; 2-3 Rx con licencia (RANZCR/Radiopaedia, sin verificar) o propias anonimizadas; decisión de fuente de imágenes.
8. **Visor de cortes ligero «tórax/cráneo en 3 ventanas»** con barra de modos y buscador que salta al corte (nuestra mejora a su buscador). Guardia: «¿hernia/desviación?»
   comparando normal y patológico con contornos SVG sobre hoz y tentorio. Estudio: orientación y ventanas (mediastino, pulmón, hueso, cerebro). Esfuerzo grande (pieza nueva `core`).
   Necesita: decisión de arquitectura, casos con licencia (CQ500 no comercial, TotalSegmentator, ya listados en `navrad-2.md §5`, sin verificar) y un PDF de neurocríticos.
(Prioridad sugerida del megaproyecto: 6 → 2 → 3 → 1 → 4 → 7 → 5 → 8: de lo barato y ya posible a lo que exige imágenes con licencia.)

## 7. Qué no traer
Sus imágenes, contornos, notas; Cornerstone/Next.js; la guía con LLM; precargar 150 MB; las cuentas.
## Captura (≤440 px): `nr-head.jpg` (visor de cráneo en móvil: barra Scroll/Pan/Window/Reset/Series/Anatomy/AI Guide, «1/51 · W80 L40»).
