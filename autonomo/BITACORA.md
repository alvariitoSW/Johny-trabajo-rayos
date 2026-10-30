# Bitácora

La lleva la skill `/bitacora` (`.claude/skills/bitacora/SKILL.md`). Aquí está **lo que se quiere hacer y aún no está
aprobado**, lo que espera algo del usuario y lo hecho en la última semana. Lo aprobado vive en `TABLERO.md`, que es
lo único que trabaja el plan socialista. Lo hecho hace más de 7 días y lo descartado pasan a
`docs/historial/bitacora.md`.

Última sincronización: 2026-10-30 (montaje del método; protocolo v0 leído entero).

---

## 1. Apuntado: espera tu visto bueno

Orden que propongo (de arriba abajo). Todo sale del protocolo v0 (`docs/protocolo/protocolo-v0.md`).

### B-001 · Cerrar las dudas abiertas del protocolo · apuntado 2026-10-30
- **Lo que dijiste**: «el fin es obtener y analizar los datos descritos en el protocolo de estudio».
- **Cómo lo entiendo**: tipo `informe`. Una página para ti y tu tutor con cada hueco del protocolo, 2-3 opciones con
  su fuente y lo que cambia cada una. No decide nada: eliges tú. Los huecos (leídos en el protocolo):
  1. **Programa**: LIFEx **o** la opción B (3D Slicer + SlicerRadiomics + jamovi). El título, §3, §4, §8, §9 y §11
     mezclan los dos; cambian los nombres y las fórmulas de las características (§10).
  2. **Grosor de corte** (§7: vacío) y **matriz** (§7: «512 × 512???»).
  3. **Un solo equipo de TC** o varios (§7: «???»).
  4. **Contraste** (§7: «Verificar marca»).
  5. **Erosión del contorno** (§8: está en forma de pregunta).
  6. **Matriz de correlaciones de Spearman** (§11.2: en forma de pregunta).
  7. **Remuestreo y discretización** (§9: «evaluar», «sujeta a evaluación piloto»): ¿quién decide tras el piloto y
     con qué criterio?
  8. **Necrosis visual** (§6, §10): ¿sí/no o escala?
- **Depende de**: nada.
- **Tamaño**: pequeña (una sesión).
- **Dudas**: ninguna para apuntarla; las dudas son el propio informe.

### B-002 · Fuentes del método en abierto · apuntado 2026-10-30
- **Cómo lo entiendo**: tipo `fuentes`. Buscar y guardar en `docs/fuentes/` (con su página) lo que el protocolo cita
  sin referencia: **IBSI** (definiciones de características y sus códigos), **RECIST 1.1** (lesión medible y diana,
  §5-6), documentación de **LIFEx** y de **PyRadiomics/SlicerRadiomics** (nombres y fórmulas), y la del **ICC**
  (modelo de acuerdo absoluto) y del **Dice**. Para entender, enlazar las páginas de Radiology Assistant de
  `autonomo/ideas/webs-radiologia.md` (RECIST 1.1, anatomía segmentaria, protocolos de contraste).
- **Depende de**: nada. **Tamaño**: pequeña.

### B-003 · Diccionario de variables · apuntado 2026-10-30
- **Cómo lo entiendo**: tipo `documento`. Una tabla con cada variable de §10: nombre, definición, unidad, tipo,
  valores posibles, origen (historia clínica, cabecera DICOM, segmentación, programa) y, en las radiómicas, nombre
  exacto en el programa elegido, configuración y código IBSI. En `analisis/config/diccionario.csv` + una versión
  legible en el móvil.
- **Depende de**: B-001 (programa) y B-002 (IBSI). **Tamaño**: mediana.
- **Lo que NO quiero (supongo)**: variables que el protocolo no pide; equivalencias entre programas sin fórmula.

### B-004 · Cuaderno de recogida de datos y códigos de estudio · apuntado 2026-10-30
- **Cómo lo entiendo**: tipo `documento`. Plantilla **vacía** (CSV y hoja para jamovi/SPSS) con las variables
  clínicas, técnicas y de la lesión del diccionario; criterios de inclusión y exclusión (§5) como lista de
  comprobación por paciente; regla de la lesión índice (§6) escrita antes de mirar imágenes; códigos `RMH-001`…
  La tabla código ↔ paciente se crea solo en el hospital.
- **Depende de**: B-003. **Tamaño**: pequeña-mediana.

### B-005 · Procedimiento de segmentación, anonimización y extracción · apuntado 2026-10-30
- **Cómo lo entiendo**: tipo `documento`. Paso a paso para el ordenador del hospital: exportar la serie portal,
  comprobar que no quedan identificadores en las cabeceras DICOM (§13), segmentar en 3D (§8, los 7 pasos), guardar la
  máscara, y extraer con la configuración fija (§9) en un archivo (`analisis/config/`). Con capturas de pantalla
  hechas con datos públicos o simulados, nunca de pacientes.
- **Depende de**: B-001 (programa). **Tamaño**: mediana.

### B-006 · Scripts del análisis con pruebas · apuntado 2026-10-30
- **Cómo lo entiendo**: tipo `script`. Lee el CSV exportado y saca: descriptiva de la muestra (§11.1), perfil
  radiómico por característica (§11.2) e ICC de acuerdo absoluto con IC 95 % y Dice (§11.3). Cada cálculo probado con
  datos simulados de resultado conocido. Sale una tabla y gráficos agregados.
- **Depende de**: B-001 (Python, jamovi o SPSS: si eliges solo jamovi/SPSS, esto se convierte en una guía de clics) y
  B-003. **Tamaño**: mediana.
- **Dudas**: ¿puedo usar librerías de Python (numpy, pandas, scipy, matplotlib) o solo la biblioteca estándar?

### B-007 · Selección al azar del 20-30 % para el segundo observador · apuntado 2026-10-30
- **Cómo lo entiendo**: tipo `script`. Un script con semilla fija que, a partir de la lista de códigos, elige el
  20-30 % (mínimo 15 si se puede, §8) y lo deja registrado. Se ejecuta en el hospital.
- **Depende de**: B-004. **Tamaño**: pequeña.

---

## 2. En marcha

(nada aprobado todavía)

## 3. Esperando algo tuyo

- **Tu visto bueno** a B-001…B-007 (o el orden que prefieras).
- **Quién es quién**: quién segmenta (observador 1 y 2) y qué radiólogo revisa (§8). Solo los papeles, sin nombres en
  el repositorio si prefieres.
- **Comité de Ética** (§13): cuándo se presenta; el protocolo v0 aún tiene huecos (B-001).

## 4. Mejoras de lo que ya existe

(nada todavía)

## 5. 💡 Lo que yo propondría

- **Piloto con la colección pública de TCIA «Colorectal-Liver-Metastases»** (197 TC en fase portal de metástasis
  colorrectales, con tumores ya segmentados; listada como CC BY 4.0, por verificar): serviría para el piloto de
  remuestreo y discretización que pide §9, para probar todo el circuito y para hacer las capturas del procedimiento
  sin usar datos del hospital. Detalle en `autonomo/ideas/webs-radiologia.md`. Esta red bloquea TCIA: habría que
  bajarla desde otro sitio.
- **Segmentación semiautomática del hígado con TotalSegmentator** dentro de 3D Slicer, para ahorrar tiempo en la
  segmentación (idea sacada de cómo hace NavRad sus contornos; `autonomo/ideas/ingenieria-inversa/navrad.md`). Solo
  si eliges la opción B; la metástasis se seguiría segmentando a mano o semiautomática como dice §8. Necesita
  comprobar su licencia y que corre en el ordenador del hospital.
- **Tiempo de segmentación** (§10 lo pide como variable): cronometrarlo desde el principio en el cuaderno, porque
  responde al objetivo secundario 4 (factibilidad).

## 6. Hecho esta semana

- 2026-10-30 · Montado el método de trabajo de fiebres-neutropenias en este repositorio, con el protocolo v0 y las
  webs de radiología como base.
