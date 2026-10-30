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
  1. ~~**Programa**~~: **decidido por el usuario el 30/10**: 3D Slicer + pyRadiomics. Falta pasarlo al protocolo
     (el título, §3, §4, §8, §9 y §11 aún nombran LIFEx).
  2. **Grosor de corte** (§7: vacío) y **matriz** (§7: «512 × 512???»). El pipeline ya los registra por caso.
  3. **Un solo equipo de TC** o varios (§7: «???»). `qc_heterogeneidad_tecnica.csv` dirá cuántos hay.
  4. **Contraste** (§7: «Verificar marca»).
  5. **Erosión del contorno** (§8: está en forma de pregunta). Hoy: sin erosión.
  6. ~~**Matriz de Spearman**~~: **decidido por el usuario el 30/10**: sí, exploratoria. Falta pasarlo al protocolo.
  7. **Remuestreo y discretización** (§9): el usuario fijó 1 × 1 × 1 mm y binWidth 25 UH por defecto (10 como
     opción). **El protocolo v0 pone 10 UH como ejemplo**: hay que alinear protocolo y configuración, y decidir
     con qué criterio se elige tras el piloto.
  8. **Necrosis visual** (§6, §10): ¿sí/no o escala?
  9. **«Homogeneity» del GLCM** (§10): pyRadiomics tiene dos (Idm = «Homogeneity 2», la elegida; Id =
     «Homogeneity 1»). ¿Cuál es la principal? (`docs/diccionario_variables.md`).
  10. **Interpolación de la imagen**: §9 dice lineal; el usuario dijo «BSpline o lineal». Hoy: lineal.
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

### B-003 · Diccionario de variables · apuntado 2026-10-30 · **parte radiómica hecha el 30/10**
- **Hecho** (pedido directo del usuario): `docs/diccionario_variables.md`, con las 19 características prioritarias
  (nombre exacto en pyRadiomics, definición, unidad, configuración, IBSI y desviaciones conocidas).
- **Falta**: las variables clínicas y técnicas de §10 (edad, sexo, primario, tratamiento, segmento, necrosis…) y
  **verificar los códigos IBSI** marcados (v) en el documento IBSI.

### B-004 · Cuaderno de recogida de datos y códigos de estudio · apuntado 2026-10-30
- **Cómo lo entiendo**: tipo `documento`. Plantilla **vacía** (CSV y hoja para jamovi/SPSS) con las variables
  clínicas, técnicas y de la lesión del diccionario; criterios de inclusión y exclusión (§5) como lista de
  comprobación por paciente; regla de la lesión índice (§6) escrita antes de mirar imágenes; códigos `RMH-001`…
  La tabla código ↔ paciente se crea solo en el hospital.
- **Depende de**: B-003. **Tamaño**: pequeña-mediana.

### B-005 · Procedimiento de segmentación, anonimización y extracción · apuntado 2026-10-30 · **en parte hecho el 30/10**
- **Hecho**: conversión, comprobación de geometría y anonimización (`src/01_convertir.py`), extracción con la
  configuración fija (`config/params.yaml`, `src/02_extraer.py`) e instrucciones de uso en el `README.md`.
- **Falta**: el paso a paso de la **segmentación en 3D Slicer** (§8, los 7 pasos), con capturas hechas con casos
  públicos o sintéticos, nunca de pacientes.

### B-006 · Scripts del análisis con pruebas · **hecho el 30/10** (pedido directo del usuario)
- Pasos 3-6 del pipeline (`src/03_qc.py` … `src/06_informe.py`) con 12 pruebas sobre datos sintéticos
  (`tests/`). Falta la descripción de la **muestra clínica** (§11.1), que depende de B-004.

### B-007 · Selección al azar del 20-30 % para el segundo observador · apuntado 2026-10-30
- **Cómo lo entiendo**: tipo `script`. Un script con semilla fija que, a partir de la lista de códigos, elige el
  20-30 % (mínimo 15 si se puede, §8) y lo deja registrado. Se ejecuta en el hospital.
- **Depende de**: B-004. **Tamaño**: pequeña. **Se une a B-012** (Consejo 30/10).

### Del Consejo del 30/10 (acta `autonomo/consejo/2026-10-30.md`) · **aplicado el 30/10** («aplica todo»)
- **Lo que dijiste**: «una ley para explicar de manera sencilla la interpretación estadística […] excluir
  automáticamente los casos con alertas del QC; definir por escrito una regla de segmentación del borde; interpretar
  con cautela primer orden y GLCM si su ICC sale bajo; reproducibilidad con 15 casos o más […] y construir la interfaz
  donde subir los datos de los pacientes y los casos»; «tendría que poder verlo en cualquier momento desde el móvil».

| Nº | Qué | Recomendación del Consejo | Coste | Orden |
|---|---|---|---|---|
| B-011 | Etiqueta de cautela por IC 95 % (Koo y Li) en la tabla de ICC + aviso si hay < 15 casos con dos observadores | aprobar; etiqueta, nunca filtro (§11.3) | ≈0,3 M | 1 |
| B-008 | **Ley** de explicar en llano (texto en el acta, va a REGLAS §4) + `docs/guia_interpretacion.md` + página «Cómo leer cada medida» en el PDF | aprobar el texto; tres niveles (qué mide · qué se ve en la TC con fuente · significado clínico: no se da) | ≈1,4 M | 2 |
| B-010 | Guía escrita de segmentación del borde, fechada antes de segmentar | aprobar; **erosión y ventana: tú y tu tutor** | ≈1,1 M | 3 |
| B-012 | Sorteo con semilla del 30 % (≥15) para el 2.º observador, antes de segmentar (une B-007) | aprobar | ≈0,9 M | 3 |
| B-009 | **Revisar y contar en vez de excluir automáticamente**: el pipeline propone, el radiólogo decide, diagrama de flujo de casos | aprobar el cambio frente a tu propuesta | ≈1,3 M | 4 |
| B-013 | Interfaz **local** en el PC del hospital (biblioteca estándar, solo 127.0.0.1); primera fase: Nuevo caso + Ejecutar | **decides tú** (arquitectura); después de probar la instalación | ≈2,2 M (todo ≈4,5 M) | 6 |
| B-014 | Ver desde el móvil: método ya en GitHub; datos por acceso remoto del hospital; resumen agregado solo con permiso del delegado de protección de datos | **decides tú** y el hospital | ≈0,8 M (el resumen) | 7 |

---

## 2. En marcha

(nada aprobado todavía)

## 3. Esperando algo tuyo

- **Tu visto bueno** a B-001, B-002, B-004, B-007 y lo que falta de B-003 y B-005.
- **Probar la instalación en el PC del hospital** (README, «Instalación»): no se ha probado en Windows.
- **Las 5 decisiones del Consejo del 30/10** (acta, «Lo que espera al usuario»): la ley, revisar en vez de excluir,
  erosión y ventana con tu tutor, la interfaz y el acceso desde el móvil.
- **Pedir a Informática** el acceso remoto (VPN o escritorio remoto) al PC del estudio, y consultar al delegado de
  protección de datos si se puede sacar un resumen agregado al móvil.
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
  con 3D Slicer (ya elegido); la metástasis se seguiría segmentando a mano o semiautomática como dice §8. Necesita
  comprobar su licencia y que corre en el ordenador del hospital.
- **Tiempo de segmentación** (§10 lo pide como variable): cronometrarlo desde el principio en el cuaderno, porque
  responde al objetivo secundario 4 (factibilidad).

## 6. Hecho esta semana

- 2026-10-30 · **Consejo aplicado** (B-008 a B-014): ley de explicar en llano (REGLAS §4.4) y guía
  `docs/guia_interpretacion.md` (página para el móvil: https://claude.ai/artifact/R39N6BzDFiV1Ps6Asfmt69); lectura
  automática en el PDF; etiqueta de fiabilidad del ICC (Koo y Li) y aviso < 15; sorteo con semilla; guía del borde
  (erosión, ventana y herramienta, en blanco para ti y tu tutor); revisar y contar con diagrama de flujo; interfaz
  local (demo: https://claude.ai/artifact/TgboL9UoqGhQD3xD3Lv5v2); resumen agregado para el móvil (paso 7).
- 2026-10-30 · **Pipeline de radiómica** (pedido directo del usuario): conversión y anonimización, extracción con
  pyRadiomics 3.1.0, control de calidad, reproducibilidad (Dice, HD95, ICC), descriptivo, informe PDF para el móvil,
  diccionario de variables, generador de datos sintéticos y 12 pruebas. Informe de ejemplo en `examples/`.
- 2026-10-30 · Montado el método de trabajo de fiebres-neutropenias en este repositorio, con el protocolo v0 y las
  webs de radiología como base.
