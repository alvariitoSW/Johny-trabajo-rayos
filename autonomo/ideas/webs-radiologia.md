# Webs de radiología: qué sirve para este estudio

Las dos webs que mandó el usuario para fiebres-neutropenias, releídas para el estudio de radiómica (30/10/2026).
Informes completos de ingeniería inversa (hechos el 23-30/10 para la app de UCI) en `ingenieria-inversa/`.

**Regla** (`CLAUDE.md` §5.3): sirven para **aprender y para saber qué buscar**. Sus textos e imágenes no se copian;
sus cifras no son fuente del estudio sin una referencia primaria (p. ej. RECIST 1.1 se cita por su artículo
original, no por la web).

## The Radiology Assistant (radiologyassistant.nl)

Web docente gratuita (Robin Smithuis y colaboradores, Sociedad Holandesa de Radiología). Licencia literal de su
página Disclaimer: las imágenes e ilustraciones «may be reproduced for educational purposes with due credit»; de los
textos no dice nada (no se copian). Informes: `ingenieria-inversa/radiologyassistant.md` y `-2.md`.

Páginas útiles para el protocolo, **abiertas con respuesta 200 el 30/10/2026**:

| Para qué (protocolo) | Página |
|---|---|
| Segmento hepático de la lesión (§6, §10) | Liver - Segmental Anatomy: https://radiologyassistant.nl/abdomen/liver/segmental-anatomy |
| Reconocer la metástasis y distinguirla del parénquima y de otras lesiones (§5 exclusión, §8) | Characterisation of liver masses: https://radiologyassistant.nl/abdomen/liver/characterisation-of-liver-masses · Common Liver Tumors: https://radiologyassistant.nl/abdomen/liver/common-liver-tumors |
| Lesión medible y lesión diana ≥10 mm (§5, §6) | RECIST 1.1 - the basics: https://radiologyassistant.nl/more/recist-1-1/recist-1-1-1 · RECIST 1.1 - and more: https://radiologyassistant.nl/more/recist-1-1/recist-1-1 · RECIST 1.1 - examples: https://radiologyassistant.nl/more/recist-1-1/recist-1-1-examples |
| Fase portal ≈70 s y protocolo de contraste (§7) | CT contrast injection and protocols: https://radiologyassistant.nl/more/ct-protocols/ct-contrast-injection-and-protocols |

Su truco útil aquí: la **pila de imágenes** (StackViewer) y los **pares «sin / con rótulos»** sirven de modelo para
el procedimiento de segmentación (B-005): capturas paso a paso de dónde poner el contorno, hechas con casos
públicos, nunca de pacientes del hospital.

## NavRad Anatomy (anatomy.navigatingradiology.com)

Atlas de anatomía en TC sobre estudios DICOM reales completos (visor Cornerstone3D, ventanas en UH). Tiene un visor
de **abdomen-pelvis** con los **segmentos hepáticos** rotulados gratis. Informes: `ingenieria-inversa/navrad.md`,
`-2.md`, `-3.md`. Abierta (200) el 30/10/2026.

Lo que sirve para el estudio:
- **Repasar los segmentos de Couinaud corte a corte** antes de registrar el segmento de cada lesión (§10).
- **Ventana y nivel en UH** con presets (hígado 150/70 en su visor): la radiómica trabaja con la imagen original en
  UH (§9), y la ventana solo cambia cómo se ve, no los valores que se extraen. Merece una frase en el procedimiento.
- **Sus contornos salen de TotalSegmentator** (segmentación automática + revisión humana; visto en sus datos). Idea
  para la opción B: segmentar el hígado con TotalSegmentator en 3D Slicer y la metástasis a mano o semiautomática
  (bitácora, «Lo que yo propondría»). Licencia de TotalSegmentator: por verificar en origen.
- **No sirve**: sus imágenes y contornos no tienen licencia declarada; no se usan.

## Fuentes que encontré de paso (por verificar en origen)

La red de este entorno bloquea TCIA, Zenodo, arXiv, readthedocs y la web de LIFEx: lo de abajo sale de resultados de
búsqueda y **no se ha abierto**. Va a la tarea B-002 (fuentes).

- **IBSI** (definiciones estándar de 169 características): Zwanenburg A, et al. *Radiology* 2020;295(2):328-338,
  DOI 10.1148/radiol.2020191145. Copia abierta en Cardiff: https://orca.cardiff.ac.uk/id/eprint/128432/1/128432.pdf ·
  preprint: https://arxiv.org/pdf/1612.07003v10
- **Colección pública «Colorectal-Liver-Metastases»** (TCIA; Simpson et al., DOI 10.7937/QXK2-QG03): TC
  preoperatorias en **fase portal** de 197 pacientes con metástasis hepáticas colorrectales, con segmentaciones del
  hígado, venas y cada tumor. Listada como CC BY 4.0 en terceros (licencia por verificar en la página de TCIA).
  Portal: https://portal.imaging.datacommons.cancer.gov/collections/colorectal_liver_metastases
  **Por qué importa**: permitiría hacer el **piloto de remuestreo y discretización (§9)**, probar el circuito entero
  y hacer las capturas del procedimiento **sin tocar datos del hospital**. Usarla es decisión del usuario.
