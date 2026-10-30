# Cómo se montó el proyecto

## 30/10/2026 · El método de fiebres-neutropenias, adaptado a un estudio de radiómica

El usuario pidió «aplicar la forma de trabajar de fiebres-neutropenias en este repositorio, teniendo en cuenta las
páginas web de radiología que le mandó», con el fin de «obtener y analizar los datos descritos en el protocolo de
estudio». Eligió copiar **todo, adaptado**, y subir el protocolo aunque el repositorio sea público.

**Qué se trajo y cómo se adaptó** (origen: `alvariitoSW/fiebres-neutropenias`, `main` del 30/10/2026):

| Allí | Aquí |
|---|---|
| `CLAUDE.md` de una app web de UCI | `CLAUDE.md` de un estudio: el protocolo manda, datos de pacientes fuera del repositorio, análisis solo descriptivo |
| `autonomo/REGLAS.md` (contenido clínico, app, rúbrica «sirve para estudiar») | mismas ideas de fuentes, gasto, gobierno y Consejo; la app se cambia por «datos y análisis»; rúbrica «sirve para el estudio» |
| 7 agentes con el **profesor** | 7 agentes con el **metodólogo** (diseña y juzga el método) |
| `jueces.mjs` (navegador a 390 px) | `jueces.py`: ningún dato de paciente en git + las pruebas de los cálculos |
| skills `plan-socialista`, `bitacora`, `ahorro`, `ingenieria-reversa` | las mismas, reescritas para el estudio |
| `gasto.mjs`, `AGENTS.md` (Ponytail) | copiados tal cual |
| informes de Radiology Assistant y NavRad | copiados en `autonomo/ideas/ingenieria-inversa/` + `webs-radiologia.md` con lo útil para el estudio |

**No se trajo**: la app, sus motores, Motion, la Mayéutica, los jueces de móvil, graft y sus ganchos (no aplican a un
estudio), ni las skills de anatomía, radar y mayéutica. Las skills de investigación (`claim-check`, `paper-lookup`,
`pydicom`…) se pueden copiar cuando una tarea las pida.

**Decisiones**:
- El repositorio es público: `.gitignore` bloquea imágenes y tablas, y `jueces.py` lo comprueba (prueba trampa
  `autonomo/pruebas/jueces_trampa.py`).
- Lo que el protocolo deja abierto («???») no lo decide ningún agente: B-001 de la bitácora lo lista para el usuario.
- Páginas de Radiology Assistant útiles para el estudio, abiertas con 200 el 30/10/2026 (anatomía segmentaria,
  lesiones hepáticas, RECIST 1.1, protocolos de contraste). TCIA, Zenodo, arXiv, readthedocs y lifexsoft.org están
  bloqueados en la red del entorno: la colección «Colorectal-Liver-Metastases» y el IBSI quedan «por verificar».

## 30/10/2026 · Pipeline de radiómica (pedido directo del usuario)

El usuario (radiólogo) pidió el pipeline completo: conversión y anonimización, extracción con pyRadiomics, control
de calidad, reproducibilidad, descriptivo, informe PDF, diccionario y pruebas con datos sintéticos. Decidió 3D
Slicer + pyRadiomics (no LIFEx), binWidth 25 por defecto (10 opcional) y la matriz de Spearman.

- **pyRadiomics**: en PyPI solo hay binarios hasta Python 3.9 y el paquete fuente 3.1.0 no compila (le falta
  `cmatrices.h`). El usuario autorizó instalarlo desde el repositorio oficial fijado a la etiqueta v3.1.0 (commit
  `6a761c4`). Se compila; en Windows sin administrador, la vía recomendada es llevar un wheel compilado en otro PC
  (README). La instalación en Windows no se ha probado.
- **Del código de pyRadiomics** (no de memoria): StandardDeviation está desactivada por defecto (por eso
  `params.yaml` lista firstorder entera); la curtosis no es la de exceso (+3 frente a IBSI); la discretización
  difiere de IBSI; la máscara siempre se remuestrea con vecino más próximo.
- **IBSI**: el documento de referencia no se pudo abrir (red bloqueada); los códigos van marcados (v).
- **Decisiones técnicas**: la máscara de Slicer (recortada a su extensión) se recoloca en la rejilla de la imagen
  sin interpolar, y si el espaciado u orientación no coinciden, el paso 1 para. El criterio de ≥ 10 mm se aplica
  al diámetro axial (como RECIST 1.1). HD95 = el mayor de los dos percentiles 95 dirigidos. ICC = «ICC2» de pingouin.
- **Pruebas**: 12 (pytest) sobre 10 casos sintéticos con UH, ruido y tamaño conocidos, identificadores falsos en las
  cabeceras, segmentaciones tipo Slicer y DICOM-SEG, y dos casos trampa (lesión de 8 mm y dos componentes).

## 30/10/2026 · Consejo de Ministros aplicado («aplica todo»)

Acta: `autonomo/consejo/2026-10-30.md`. Cuatro constructores en paralelo (cada uno en su copia del repositorio) y
una segunda tanda que tocó los archivos compartidos.
- **Ley de explicar en llano** (REGLAS §4.4) y `docs/guia_interpretacion.md`: tres niveles (qué mide, qué se ve en la TC
  con fuente, significado clínico: no se da). Fuentes abiertas nuevas: van Timmeren 2020, Koo y Li 2016 (resumen),
  Ganeshan y Miles 2013 (`docs/fuentes/LEEME.md`). El PDF lleva «Cómo leer…» y párrafos «Qué dicen tus datos».
- **Revisar y contar** (no excluir en silencio): `decision_propuesta` en el QC, `data/decisiones_casos.csv` del
  radiólogo, solo se analizan los incluidos y `flujo_casos.csv` + página «Flujo de casos». Una lesión < 10 mm sin
  decisión queda «excluir (propuesta)» hasta que el radiólogo la confirme; §6 (pasar a la siguiente lesión) no está
  automatizado.
- **ICC**: etiqueta de fiabilidad por IC 95 % (Koo y Li; fronteras 0,5/0,75/0,9 como decisión de implementación),
  nunca filtro; aviso si hay < 15 casos; `src/seleccion_reproducibilidad.py` (sorteo con semilla).
- **Interfaz local** (`app/`, biblioteca estándar, solo 127.0.0.1, token, sin registros) y **resumen agregado para el
  móvil** (paso 7; recuentos 1-4 como «< 5»). Riesgo anotado: por diferencia entre recuentos se pueden deducir
  números pequeños; lo valora el delegado de protección de datos.
- Pruebas: 67.

## 30/10/2026 · Modo móvil de la app

El usuario pidió usar la app en el navegador del móvil, no solo en el PC (Informática le dio permiso, sin herramienta
concreta). Se añadió `--movil`: escucha en la IP de red interna del PC (solo direcciones privadas; una pública,
0.0.0.0 o 127.x no arrancan), clave de 16 caracteres por arranque, `--permitir` para limitar a ciertos aparatos y TLS
opcional con certificado de Informática. Sin certificado la conexión no va cifrada dentro de la red: queda como aviso
en pantalla y en `app/LEEME.md`. No se abre nunca a internet (túneles o puertos): sacaría datos de pacientes de los
equipos autorizados (protocolo §13). 72 pruebas.

**Vídeo explicativo y arreglo de rutas de la app (30/10/2026).** Para el vídeo de cómo funciona la app (hecho con
capturas reales y 10 casos sintéticos; no se sube al repositorio) se vio un fallo: si la app se abría con una ruta
relativa (`--datos data`) desde otra carpeta, «Ejecutar» no encontraba los casos, porque el pipeline arranca desde
la carpeta del proyecto. `app/servidor.py` convierte ahora las rutas en rutas completas al arrancar. 73 pruebas.
