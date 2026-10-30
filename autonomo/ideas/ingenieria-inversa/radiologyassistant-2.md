> Copiado de `alvariitoSW/fiebres-neutropenias` (`autonomo/ideas/ingenieria-inversa/radiologyassistant-2.md`) el 30/10/2026. Se hizo para aquella app de UCI: «nuestra app» y sus rutas se refieren a ella. Lo útil para este estudio está en `autonomo/ideas/webs-radiologia.md`.

# Radiology Assistant, pasada 3: razonamiento de UCI y megaproyecto (25/10/2026)

Lo previo (`radiologyassistant.md` del 23/10: licencia, StackViewer, ideas de bibliografía) no se repite. Esta pasada: vigía, razonamiento de 6 artículos
(leídos en memoria con Playwright, 390×844; no se guarda texto suyo) y el megaproyecto. Etiquetas: **visto** / **deducido** / **no visto**.
Todo número de RA es «para buscar fuente»: no es fuente (CLAUDE.md §7.1-7.2).

## 1. Vigía (piezas frente a lo anotado)
- `dist.js` 96.895 B (antes ~97 kB), `dist.css?v=1679433952` 33.163 B, `radiology-assistant.css` 1.473 B: **sin cambios** (visto).
- **Nuevo**: `gdpr.js` 188.977 B + `gdpr.css` 3 kB (aviso de cookies; antes no anotado) y un desafío de Cloudflare (`cdn-cgi/challenge-platform`, 302→200). Visto.
- Contenido: «Chest X-Ray – Basic Interpretation» ahora con «Update 2025» (5.994 palabras, 104 imágenes, 8 pilas); no se ha movido nada más. Otros: Cardiovascular
  devices 3.240 palabras/74 imágenes/0 pilas; Heart Failure 2.755/30/6 pilas; ICH traumática 1.784/21/8; no traumática 4.529/71/8; ictus agudo 1.937/31/0.
- Conclusión: la web es la misma; el único cambio técnico es la capa de cookies. No hay nada nuevo que estudiar de su código.

## 2. Hallazgo clave: lo que RA NO cubre de la guardia (visto en los títulos y el texto)
- **Basic Interpretation no trae sección de dispositivos de UCI** (ni tubo ET, ni vía central, ni SNG, ni drenaje torácico). Sus secciones: normal y variantes,
  diafragma, vasos y hilios, enfoque sistemático, silueta, zonas escondidas, corazón y pericardio, hilios, mediastino, pulmón, pleura, pared, abdomen. Solo hay un caso de
  neumotórax en paciente ventilado con tubo torácico posterior.
- **Cardiovascular devices** (Rx): marcapasos, TRC, DAI, válvulas, TAVR, MitraClip, cierres, stents, LVAD, Impella, balón de contrapulsación, clips de CABG,
  y bajo «ICU monitoring device» **solo el Swan-Ganz** (un caso: punta en rama lobar superior izquierda → reposicionado a arteria pulmonar izquierda).
  Sí nombra complicaciones del Swan (nudo intracardiaco, infarto pulmonar, perforación, arritmia, colocación en VCI). **No hay punta de CVC, ET ni SNG.**
- **No hay artículo de TEP** entre los leídos (no visto; RA tiene «Cardiovascular Pearls on Chest CT», sin abrir).
- Para ET/CVC/SNG la fuente tendrá que ser nuestra: Marino (acceso vascular y respiratorio), Merino Neumología (figuras 28-1, 28-2, 29-3) y el Manual UMI.

## 3. Estructura de su razonamiento (sin copiar texto)
**Rx de tórax, orden «de dentro afuera»** (visto): tráquea y vía central → mediastino y corazón → hilios → pulmón y pleura → diafragma y debajo →
pared y partes blandas → abdomen alto → **comparar siempre con la placa previa** (caso de IC sutil: «mira la actual, ahora la previa»).
Signos nombrados: signo de la silueta (borra borde = lesión en contacto), «zonas escondidas» (6 casos: detrás del corazón, bajo el diafragma, tras la 1.ª costilla,
lóbulo inferior derecho, retrocardíaco, consolidación sutil), línea ácigo-esofágica, ventana aortopulmonar, incisura cardíaca, derrame encapsulado («tumor
evanescente»), broncograma aéreo (descompensa atelectasia por derrame masivo), pliegue cutáneo como imitador de neumotórax, **signo del surco profundo**,
hemidiafragma deprimido (sugiere a tensión), aire libre subdiafragmático.
Criterios a buscar luego en nuestras fuentes: volumen mínimo visible de derrame (cifra de RA: 200-300 mL), hemitórax opaco (hasta ~5 L), neumotórax
no visto en decúbito (RA: hasta un 30 %), índice cardiotorácico >0,5 en PA.

**Insuficiencia cardíaca en Rx** (títulos vistos): estadio I redistribución → II edema intersticial → III edema alveolar; índice cardiotorácico; derrame;
**pedículo vascular** (ancho = volemia: RA da <60 mm normal, >85 mm patológico, +5 mm ≈ +1 L); dilatación de la ácigos; fallo derecho. Distingue tres edemas
(cardiogénico, sobrecarga, permeabilidad/SDRA) por el pedículo. Para buscar fuente: signos del estadio I-III (cefalización, líneas de Kerley, manguitos
peribronquiales, velo perihiliar; nombres deducidos, imágenes no leídas).

**TC de cráneo hemorrágico** (visto): primero **localizar** (extra-axial: subaracnoidea, subdural, epidural; intra-axial: contusión, lesión axonal difusa); en no
traumático «el sitio es la clave del diagnóstico»: profunda/central (ganglios basales, tálamo, protuberancia, cerebelo) = hipertensión; lobar periférica =
angiopatía amiloide, tumor, malformación, infarto venoso. Después: epidural **lenticular, no cruza suturas** (arteria meníngea media, fractura temporal),
subdural en media luna que sí cruza; **signo del remolino** (sangrado activo), herniación subfalcina y uncal, hemorragias de Duret (tronco por descenso),
SAH aneurismática (complicaciones, perimesencefálica, papel de angio-TC y arteriografía). Clínica del caso: bradicardia, hipertensión, postura anormal y pupila
midriática = herniación/HTIC.

**Ictus agudo en TC** (visto): la TC descarta hemorragia; signos precoces: **hipodensidad** (cada 1 % de agua = −2,5 UH), **borramiento del núcleo lenticular**,
**signo de la cinta insular**, **arteria cerebral media hiperdensa**, infarto hemorrágico (15 %); luego angio-TC (qué vaso) y perfusión (penumbra); RM-difusión.
Sensibilidad TC global 64 %, especificidad 85 % (RA; buscar fuente). «Hipodensidad en <6 h = mala noticia».

## 4. Pares de prueba (hallazgo → conclusión) «para buscar fuente», no son fuente
1. Surco costofrénico profundo + hemidiafragma deprimido en paciente ventilado → neumotórax a tensión; tras tubo, el diafragma sube.
2. Hemitórax derecho opaco con broncograma aéreo en bronquio principal → derrame masivo con atelectasia por compresión (no consolidación).
3. Pedículo vascular ensanchado + ácigos ancha + sin cardiomegalia → sobrecarga de volumen (edema por sobrecarga), no cardiogénico.
4. Punta de Swan en rama lobar periférica → riesgo de infarto/perforación: retirar hasta la arteria pulmonar principal.
5. Hematoma lenticular que respeta las suturas + fractura temporal + pupila dilatada → epidural con herniación.
6. Hemorragia profunda en tálamo/ganglios en hipertenso → hipertensiva; lobar en anciano → angiopatía amiloide.
7. Hipodensidad cinta insular + núcleo lenticular borroso + MCA hiperdensa → infarto de ACM precoz.

## 5. Intensivista (guardia) frente a estudio
- **Guardia**: la lista de comprobación de Rx (previa, tráquea/tubo, mediastino, pleura, diafragma, escondidas) y la de TC de cráneo (¿sangre? ¿dónde? ¿línea media, cisternas,
  surcos?). Un recorrido corto con una imagen por paso y una pregunta, sin leer 6.000 palabras.
- **Estudio**: diferenciales de patrones, tipos de hemorragia, signos de ictus y su razón fisiopatológica (cada signo con su porqué).
- **Lo nuestro**: 14 figuras de Rx/TC en `js/modules/neumologia/img` (tubo ET, intubación selectiva, neumotórax, neumotórax a tensión, SDRA, TEP en TC,
  eco pleural), sin rótulos encima; Técnicas R1 solo enlaza a Merino y Marino; PIF (`pif-rotaciones.js`: «radio-torax» y «neuro-radio») con objetivos pero sin construir.
  Ganan ellos en volumen de imágenes y en lectura sistemática; ganamos nosotros en UCI, preguntas y fuente trazable.

## 6. Megaproyecto: 6 ideas desde RA (el resto, en `navrad.md`)
1. **«Lee la placa en 30 s»**: recorrido de 7 pasos (previa → vía central y tubos → mediastino → pleura → diafragma → escondidas → patrón). Guardia: tras intubar o canalizar.
   Aporta lista en la cama y preguntas «piensa y destapa» al estudiar. Esfuerzo medio. Necesita: PDF Marino (resp./acceso vascular), Merino, y una Rx por paso (propia anonimizada o con licencia); decisión de formato.
2. **Rótulos SVG sobre las figuras que ya tenemos** (tubo ET, neumotórax, SDRA): flechas con «Ver en el texto». Guardia: reconocer el signo. Esfuerzo pequeño-medio. Necesita: nada nuevo.
3. **«¿Neumotórax tras pinchar?»**: ficha de signos (surco profundo, pliegue cutáneo imitador, línea pleural en eco) con pares con/sin rótulos y el límite del decúbito. Esfuerzo medio. Necesita: PDF (Merino 28, Marino) y 2-3 casos.
4. **TC de cráneo en 5 preguntas** (¿sangre?, ¿dónde?, ¿suturas?, ¿línea media/cisternas?, ¿hipodensidad?): árbol Sí/No (`initSiNoWizard`). Esfuerzo medio. Necesita: PDF Marino neurología caps. 45-47 y la rotación de Neurorradiología.
5. **Edema: ¿cardiogénico, sobrecarga o SDRA?** con pedículo vascular, ácigos y Kerley, enlazado a la guía ESC 2026 de IC. Esfuerzo medio. Necesita: PDF ESC/Marino y decisión.
6. **Bibliografía RA por rotación** (solo enlaces, ya propuesto el 23/10) añadiendo «Traumatic/Non-traumatic ICH» y «Acute Stroke». Esfuerzo pequeño. Necesita: nada.

## 7. Qué no traer / no visto
- No traer: texto, imágenes (solo con decisión tuya y crédito), jQuery/Fancybox, cookies.
- No visto: el contenido de las tablas en imagen (diferenciales), los vídeos, los signos del estadio I-III de IC en detalle, TEP, «Cardiovascular Pearls».
## Capturas (≤440 px): `ra-ptx.jpg` (neumotórax en decúbito), `ra-epidural.jpg` (epidural, en esta carpeta).
