# Dictamen de Justicia e Interior · Consejo 30/10/2026
Leído: CLAUDE.md, REGLAS §2, §3, §5.8-5.9, §6; protocolo §5, §6, §8, §11, §13; README; src (grep). Nada editado.
Las reglas y el protocolo son de solo lectura para el agente (REGLAS §6.1): todo cambio en ellos lo decide el usuario.

## 1. «Ley» de explicación en lenguaje llano (primer orden, forma, textura)
**Justicia: a favor, con cambios.**
- Encaja: CLAUDE.md §1 (explicar en llano) y protocolo §14 (perfil cuantitativo, sin valor de referencia universal).
- Riesgo: las frases «clínicas» («textura heterogénea = agresivo») serían una afirmación sin fuente (REGLAS §1.1, §1.7)
  y chocan con §14 y §11.4 (sin correlación pronóstica). Cada frase de significado clínico lleva fuente y página,
  o se redacta solo como «qué mide» (definición pyRadiomics/IBSI), nunca «qué predice».
- Dónde: NO en CLAUDE.md (corto a propósito). Una regla de una línea en REGLAS §4 (Redacción) —la apunta el usuario—
  y el contenido en `docs/diccionario_variables.md` (nueva columna «En llano»), fuente única. El informe PDF la lee de ahí.
**Interior: cómo.**
- Archivos: `docs/diccionario_variables.md` (+ columna), `config/features_prioritarias.yaml` (campo `en_llano` por
  característica, para que el PDF no analice Markdown), `src/06_informe.py` (nueva página «Cómo leer cada medida»
  tras la tabla 4, con `inf.tabla`; ya existe `texto` y `tabla`), `tests/test_pipeline.py` (comprueba que toda
  característica prioritaria tiene frase).
- Coste: documento con fuentes ≈1,1 M; cambio en 06 + prueba ≈0,1 M; auditor ≈0,55 M. Total ≈1,75 M.

## 2. Excluir automáticamente los casos con alertas del QC
**Justicia: en contra de la exclusión automática y silenciosa; a favor de «marcar y proponer».**
- Protocolo §5 incluye «Ø máximo ≥10 mm» como criterio de inclusión: ese caso sí es excluible por regla escrita.
- Pero «varios componentes», «máscara vacía» y «geometría» no son criterios del §5: pueden ser un error de
  segmentación (se corrige, no se descarta) o una lesión multicomponente válida. Excluir sin mirar = decisión del
  agente sobre algo que el protocolo no fija (REGLAS §1.3). Además, §6 manda elegir la lesión índice con una regla
  fijada antes; si el caso <10 mm se cae, la regla pide pasar a la siguiente lesión del paciente, no perder al paciente.
- «Cada excluido contado»: sí, con motivo (diagrama de flujo, requisito de transparencia; REGLAS §3.4).
- Con cambios: el usuario decide cada caso con alerta (excluir / corregir máscara / otra lesión) y queda escrito.
**Interior: cómo.**
- `src/03_qc.py`: ya produce `alertas`. Añadir columna `decision` leída de un `config/exclusiones.csv` que el usuario
  rellena en el hospital (id, decision, motivo; solo códigos RMH, sin datos clínicos). Solo la alerta «<10 mm» propone
  `excluir` por defecto; las demás, `revisar`.
- Pasos 4-6 filtran por `decision != excluir`; `src/06_informe.py`: página «Flujo de casos» (n evaluados → n con alerta
  → n excluidos por motivo → n analizados), como tabla de cifras agregadas (celdas <5 se informan como «<5», REGLAS §2.4).
- Coste: ≈1,1 M (script + pruebas con sintéticos) + 0,55 M auditor. Es cambio de análisis: requiere visto bueno.

## 3. Regla escrita de segmentación del borde (documento)
**Justicia: a favor, pero toca un punto abierto.** El protocolo §8 deja «¿erosión sistemática del contorno?» con
interrogante: NO lo decide el agente (CLAUDE.md §3). El documento describe el procedimiento ya fijado (§8: incluir
necrosis, excluir parénquima y vasos, revisar en coronal y sagital) y deja la erosión como duda para usuario y tutor.
Cualquier regla de borde nueva (ventana de visualización, milímetros) necesita fuente (RECIST 1.1, IBSI) o es «opinión del autor».
**Interior: dónde.** `docs/segmentacion-guia.md` (nuevo; enlazado desde README «Preparar los datos» y el diccionario).
No va a REGLAS ni al protocolo. La duda de la erosión, a `autonomo/BITACORA.md`. Coste ≈1,1 M + auditor 0,55 M.

## 4. Primer orden y GLCM con ICC bajo: cautela
**Justicia: a favor de la etiqueta, en contra del filtro.**
- §11.3: «sin utilizar exclusivamente un umbral arbitrario de ICC para declarar válida una característica». Una
  etiqueta descriptiva por tramos del IC 95 % (p. ej. «IC inferior <0,5: interpretar con cautela») no filtra ni
  declara «válida»; el filtro (quitar variables) es reservado al usuario (REGLAS §5.9) y además el README lo prohíbe
  («sin filtrar»). Los tramos de Koo y Li 2016 necesitan cita con página; el IC, no solo el punto, es lo que se etiqueta.
- Redactar como «reproducibilidad en esta muestra», no como veredicto; la tabla sigue mostrando todas.
**Interior: cómo.** `src/04_reproducibilidad.py` (columna `nota` ya existe en la tabla del informe: línea 238);
`src/06_informe.py` y texto «Cómo se calculó». Coste ≈0,1 M (arreglo corto) + prueba conocida (ICC=1 → sin etiqueta).

## 5. Reproducibilidad con ≥15 casos
**Justicia: a favor.** §8 lo dice orientativo y «si la muestra lo permite»; un aviso no cambia el protocolo.
Selección al azar con semilla: lo exige REGLAS §3.6 (semilla fija; la lista queda en el hospital, no en git).
**Interior: cómo.**
- `src/04_reproducibilidad.py`: tras contar `casos`, si `len(casos) < 15` o < 20 % de los analizados, imprimir y
  escribir el aviso en `reproducibilidad_segmentacion.csv`/informe («n=… < 15: IC 95 % muy anchos»). No aborta.
- Nuevo `src/seleccion_reproducibilidad.py` (`--n-total`, `--porcentaje 25`, `--minimo 15`, `--semilla`, `--salida`):
  lista de IDs en `outputs/` (ignorada por git) y semilla en `extraccion_meta.json`. Prueba: misma semilla, misma lista.
  Coste ≈1,1 M + auditor 0,55 M; el aviso solo ≈0,1 M. Con 50 pacientes: 10-15 casos; el mínimo 15 obliga a ≥15 (30 %): avisar.

## 6. Interfaz para subir datos y casos
**Justicia: (b) en contra, rotundo. (a) a favor SOLO si es local, con condiciones y decisión expresa del usuario.**
- (b) Nube, Artifact, GitHub o servidor externo: viola CLAUDE.md §2 y REGLAS §2.1 (datos solo en equipos del hospital),
  protocolo §13 (RGPD) y el repo es público. Un Artifact es una web alojada en claude.ai: ni DICOM, ni capturas con datos.
  Tampoco una app que el agente ejecute aquí con datos reales (REGLAS §2.1: ni en la carpeta temporal de un agente).
- (a) Local: no choca con §2 si nada sale del PC. Es arquitectura/software nuevo: decisión del usuario (REGLAS §5.9;
  CLAUDE.md §6: «ninguna librería más sin que el usuario la elija»). Se propone solo la biblioteca estándar.
- Condiciones: escucha en 127.0.0.1 (nunca 0.0.0.0); no escribe logs con rutas ni nombres de archivo originales;
  rechaza IDs que no cumplan `PATRON_ID`; sin tabla código↔paciente; sin analítica ni CDN externo (la página sin
  fuentes/scripts remotos); no sube nada; borra temporales al cerrar.
**Interior: opción (a), biblioteca estándar (`http.server` + HTML/JS propio), sin librerías nuevas.**
- Pantallas: (1) Inicio: comprobación del entorno (versiones, aviso «solo en el PC del hospital»). (2) Nuevo caso:
  código RMH-nnn validado, elegir carpeta DICOM (copia o mueve a `data/crudo/<ID>/imagen/`), subir máscara(s) Slicer;
  marca caso de reproducibilidad. (3) Lista de casos: estado, alertas del QC, decisión (ver asunto 2). (4) Ejecutar:
  lanza `run_pipeline.py` como proceso, muestra la salida en directo. (5) Informe: abre `outputs/informe.pdf` y
  el flujo de casos; descarga solo agregados.
- Archivos nuevos: `app/servidor.py`, `app/pagina.html`, `app/validar.py` (reutiliza `comun.comprobar_id`),
  `app/LEEME.md`, `lanzar_app.bat`, `tests/test_app.py`; `.gitignore` sin cambios (data/ y outputs/ ya bloqueadas).
- Riesgos y mitigación: temporales (subir DICOM por el navegador deja copia en %TEMP%: mejor elegir carpeta local y
  copiar sin pasar por el navegador; limpiar al cerrar); logs (silenciar `log_message` de http.server, que escribe IP
  y ruta); puerto abierto a la red (enlazar a 127.0.0.1, token aleatorio por sesión, comprobar cabecera Host contra
  ataques de rebinding); Windows sin admin (puerto >1024, sin servicio, `.bat` en el venv del usuario); navegador
  del hospital (caché: cabeceras `no-store`); subida de DICOM con nombres reales: el paso 1 ya comprueba cabeceras,
  y la app no muestra nunca nombre de archivo original.
- Coste con constructor sonnet: servidor + pantallas + validación ≈2,2 M (dos scripts nuevos + página, partible en
  2 encargos de ≈1,1 M), pruebas y `.bat` ≈1,1 M, documento de uso ≈0,3 M, auditor de seguridad ≈0,55 M, arreglos ≈0,2 M.
  Total ≈4,5 M. Recomendado: primero «Nuevo caso» + «Ejecutar» (≈2,2 M) y ampliar después.
- Alternativa mínima (≈0,3 M): crear con un script la estructura `data/crudo/<ID>/` y validar códigos por línea de
  órdenes, sin servidor. Cubre el 80 % del dolor sin abrir puertos.

## No comprobado / riesgo
No se ejecutó nada ni se probó la app en Windows; las frases clínicas del asunto 1 y los tramos de ICC (Koo y Li) están sin fuente abierta.
Riesgo mayor: excluir automático (asunto 2) y la app local (asunto 6) cambian análisis/arquitectura: no deben pasar sin «sí» expreso del usuario.
