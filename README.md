# Radiómica de metástasis hepáticas colorrectales (TC portal)

Pipeline del estudio observacional retrospectivo y **descriptivo** del perfil radiómico de las metástasis
hepáticas de origen colorrectal en TC con contraste en fase portal (protocolo: `docs/protocolo/protocolo-v0.md`).
Una lesión índice por paciente, segmentación 3D en 3D Slicer, extracción con pyRadiomics, estadística descriptiva
y reproducibilidad interobservador. **Sin modelos predictivos.**

> **Este repositorio es público y NUNCA contiene datos de pacientes.** El código se ejecuta en el PC del hospital
> y los datos se quedan allí: `data/` y `outputs/` están bloqueados en `.gitignore`, igual que `*.dcm`, `*.nii`,
> `*.nii.gz`, `*.nrrd`, `*.seg` y las tablas. Antes de subir algo: `python autonomo/jueces.py`.

**Ver un ejemplo del resultado:** [`examples/informe_ejemplo.pdf`](examples/informe_ejemplo.pdf), generado con 10
casos **sintéticos**.

## Qué hace cada paso

| Paso | Archivo | Qué hace | Sale |
|---|---|---|---|
| 1 | `src/01_convertir.py` | DICOM → NIfTI; segmentación (NRRD de Slicer o DICOM-SEG) a la rejilla de la imagen **sin interpolar**; comprueba la geometría; quita metadatos y comprueba que no queda ningún identificador | `data/casos/<ID>/`, `outputs/anonimizacion.csv` |
| 2 | `src/02_extraer.py` | Características con `config/params.yaml` + variables técnicas DICOM (fabricante, modelo, kVp, kernel, grosor, pixel spacing, mA) | `outputs/features.csv`, `extraccion_meta.json` |
| 3 | `src/03_qc.py` | Volumen, diámetro máximo axial (alerta si < 10 mm, RECIST 1.1) y 3D, máscaras vacías o con varios componentes, homogeneidad técnica | `outputs/qc_report.csv`, `qc_heterogeneidad_tecnica.csv` |
| 4 | `src/04_reproducibilidad.py` | Dice y Hausdorff 95 entre observadores; ICC(2,1) de acuerdo absoluto con IC 95 % por característica (pingouin), sin filtrar | `outputs/reproducibilidad_*.csv` |
| 5 | `src/05_descriptivo.py` | Media, DE, mediana, RIC, mín., máx., ausentes y CV del subconjunto prioritario; histogramas, cajas y Spearman | `outputs/descriptivo.csv`, `spearman.csv`, `figuras/` |
| 6 | `src/06_informe.py` | Informe PDF para leer en el móvil, con el flujo de casos y la lectura del ICC | `outputs/informe.pdf` |
| 7 | `src/07_resumen_movil.py` | Resumen de una página con **solo agregados** (recuentos de 1 a 4 como «< 5») | `outputs/resumen_movil.html` |

Los pasos 4 y 5 analizan solo los casos con decisión «incluir» (ver «Decisiones de casos»).

Configuración: `config/params.yaml` (pyRadiomics, comentado línea a línea) y `config/features_prioritarias.yaml`.
Definiciones, IBSI y diferencias: `docs/diccionario_variables.md`.

## Interfaz local

Una página para preparar los casos y anotar decisiones sin tocar archivos: `app/LEEME.md`. En Windows se abre con
`lanzar_app.bat`. Corre solo en el PC del hospital. Paso a paso para meter tus pacientes: `app/LEEME.md`.

**Desde el móvil**: con el acceso remoto del hospital (VPN o escritorio remoto) entras en ese PC y usas la app ahí.
Borrador de la petición a Informática: `docs/solicitud-acceso-remoto.md`. Para ver cómo es sin datos reales:
demo con casos sintéticos (enlace en `autonomo/BITACORA.md`).

## Antes de segmentar

Cómo segmentar y la regla del borde: `docs/segmentacion-guia.md`. El sorteo de los casos que segmentará un segundo
observador, con semilla fija y antes de segmentar:
`python src/seleccion_reproducibilidad.py --casos data/crudo`.

## Cómo leer los resultados

`docs/guia_interpretacion.md`: qué mide cada característica y cada estadístico (Dice, ICC con su IC 95 %, CV…), en
lenguaje llano. El informe repite lo esencial en cada bloque, en «Qué dicen tus datos».

## Decisiones de casos

El paso 3 **propone** y el radiólogo **decide**; nada se excluye en silencio. Propuesta: «excluir» si la única alerta
es el diámetro axial < 10 mm (protocolo §5); «revisar» con cualquier otra alerta; «incluir» sin alertas. La decisión
final se escribe en `data/decisiones_casos.csv` (columnas `id,decision,motivo`; `decision` = `incluir`, `excluir` o
`revisar`; la rellena la interfaz local o el radiólogo a mano). Sin fila para un caso, vale la propuesta. Un caso
«revisar» sin decidir **no se analiza** y el pipeline lo avisa. El informe cuenta todo en la página «Flujo de casos».
Tras decidir: `python run_pipeline.py --input data --output outputs --desde 3`.

## Resumen para el móvil

`outputs/resumen_movil.html` (paso 7): una página con solo agregados, sin códigos de caso y con los recuentos de 1 a 4
como «< 5». **No se publica en ningún sitio.** Antes de sacarlo del PC del hospital hay que pedir permiso al delegado
de protección de datos (protocolo §13).

## Instalación en un Windows del hospital, sin permisos de administrador

Probado con **Python 3.11** (en Linux; la instalación en Windows **no se ha probado**). Python 3.10 y 3.12 deberían
funcionar con `requirements.txt`, pero `requirements-lock.txt` es la lista exacta de 3.11.

### 1. Python 3.11, solo para tu usuario

Del instalador de python.org (Windows installer 64-bit, versión 3.11): marca **«Add python.exe to PATH»**,
desmarca **«Use admin privileges when installing py.exe»** y elige la instalación normal (para el usuario
actual). No pide permisos de administrador. Alternativa: **Miniforge** (instalación «Just Me»), que tampoco los pide.

### 2. El proyecto y su entorno

Descarga el proyecto (botón «Code → Download ZIP» de GitHub, o `git clone` si tienes Git) y descomprímelo, por
ejemplo, en `Documentos\radiomica`. En una ventana de **Símbolo del sistema** (`cmd`), dentro de esa carpeta:

```bat
py -3.11 -m venv venv
venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

- Si usas PowerShell y no deja activar el entorno: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (no
  necesita administrador) y `venv\Scripts\Activate.ps1`. O usa `cmd`.
- Si el hospital sale a internet por un proxy: `python -m pip install --proxy http://usuario:clave@proxy:puerto -r requirements.txt`.
- Si el PC no tiene internet: en otro ordenador con Python 3.11 para Windows, `pip download -r requirements.txt -d paquetes`,
  copia la carpeta `paquetes` y en el hospital `pip install --no-index --find-links paquetes -r requirements.txt`.

### 3. pyRadiomics (el único paso delicado)

En PyPI, pyRadiomics 3.1.0 solo tiene binarios hasta **Python 3.9**, y su paquete fuente no compila (le falta un
archivo). Por eso se instala la **versión 3.1.0 desde su repositorio oficial**, fijada a un commit
(`requirements-pyradiomics.txt`). Eso **compila código en C**. Tres formas, de la más directa a la más segura:

**A. Si el PC tiene compilador** (Microsoft C++ Build Tools) **y Git**:
```bat
python -m pip install -r requirements-pyradiomics.txt
```
Build Tools suele necesitar administrador: si no lo tienes, B.

**B. Compilarlo en otro PC y llevarse el archivo** (recomendada en el hospital). En un Windows **con** Python 3.11 y
Build Tools (tu portátil, por ejemplo):
```bat
python -m pip wheel -r requirements-pyradiomics.txt --no-deps -w ruedas
```
Sale un archivo `ruedas\pyradiomics-…-cp311-cp311-win_amd64.whl`. Cópialo al PC del hospital e instálalo **sin
compilador**:
```bat
python -m pip install ruedas\pyradiomics-*.whl --no-deps
```
(Tiene que ser la misma versión de Python, 3.11, y Windows de 64 bits.)

**C. Con Miniforge y conda-forge**: `conda install -c conda-forge pyradiomics`, y después el paso 2 con `pip`
dentro de ese entorno. **No he podido comprobar** qué versión de pyRadiomics ofrece conda-forge para Windows; si no
es la 3.1.0, anótalo: cambia la extracción (la versión queda registrada en `outputs/extraccion_meta.json`).

### 4. Comprobar la instalación

```bat
python -c "import radiomics; from radiomics import cMatrices; print(radiomics.__version__)"
python -m pytest tests -q
```

- La primera orden debe imprimir `3.1.0a2.post8+g6a761c4`. Es la etiqueta v3.1.0 (commit `6a761c4`): el número
  raro lo genera la herramienta de versiones de pyRadiomics a partir del historial de git.
- La segunda genera 10 casos **sintéticos** en una carpeta temporal, ejecuta el pipeline entero y comprueba los
  resultados frente a los valores conocidos. Debe terminar en `12 passed`.

## Preparar los datos (en el PC del hospital)

Una carpeta por caso con el **código de estudio** como nombre (`RMH-001`, `RMH-002`…). Nunca el nombre, el NHC ni
otro dato del paciente: el pipeline para si el nombre no parece un código.

```
data/
  crudo/
    RMH-001/
      imagen/                 la serie DICOM de la TC en fase portal (solo esa serie)
      mascara.seg.nrrd        la segmentación de la lesión índice (un observador)
    RMH-002/
      imagen/
      mascara_obs1.seg.nrrd   o, en los casos de reproducibilidad, las de los dos observadores
      mascara_obs2.seg.nrrd
```

- **Desde 3D Slicer**: guarda la segmentación (`Ctrl+S`, «Save») como `.seg.nrrd` y renómbrala `mascara.seg.nrrd`.
  Valen también un labelmap `.nrrd` o un DICOM-SEG (`.dcm`).
- Si la segmentación tiene varios segmentos, el paso 1 usa el segmento 1. Para elegir otro:
  `--segmento <número o nombre>`, o `--segmento mayor:<texto>` (el de más volumen cuyo nombre contenga el texto).
- La segmentación tiene que estar hecha **sobre esa misma serie**: si su espaciado u orientación no coinciden, el
  paso 1 para en lugar de interpolar la máscara.

## Ejecutar

```bat
venv\Scripts\activate.bat
python run_pipeline.py --input data --output outputs
python run_pipeline.py --input data --output outputs_bw10 --binwidth 10
python run_pipeline.py --input data --output outputs --desde 2      (si los NIfTI ya están en data\casos; --desde admite 1 a 7)
```

Las rutas son relativas a la carpeta desde la que ejecutas: no hay ninguna ruta absoluta en el código.

**Antes de mirar los resultados, revisa:**
1. `outputs/anonimizacion.csv`: todos los casos en `OK`. Lista qué identificadores tenía el DICOM original (solo el
   nombre del atributo, nunca su valor) y confirma que no llegaron a los NIfTI ni a `tecnicas.json`. Si un caso no
   está limpio, el pipeline **para**.
2. `outputs/qc_report.csv`: la columna «alertas» (lesiones < 10 mm, varios componentes, máscaras vacías).

**Qué sale de `outputs/`** son tablas con una fila por caso codificado: **no lo subas a GitHub ni lo compartas**
fuera del entorno autorizado. Lo único compartible son resultados agregados (`descriptivo.csv`, `informe.pdf`).

## Probar con datos sintéticos

```bat
python tests\generar_sinteticos.py --salida data_sintetica --casos 10
python run_pipeline.py --input data_sintetica --output outputs_sintetico
```

Genera TC DICOM de un «hígado» con lesiones de atenuación, ruido y tamaño conocidos, con identificadores **falsos**
en las cabeceras (para comprobar que no pasan), segmentaciones como las de Slicer y un DICOM-SEG, dos
observadores en 6 casos y dos casos trampa para el control de calidad. Para probar con TC públicas reales:
`scripts/descargar_tcia.md`.

## Reproducibilidad del propio análisis

- `outputs/features.csv` lleva en cada fila el `binwidth`, la versión de pyRadiomics y el **hash SHA-256 de
  `params.yaml`**: si cambia la configuración, cambia el hash.
- `outputs/extraccion_meta.json` guarda la fecha de ejecución, los ajustes efectivos y la versión de Python, pyRadiomics,
  NumPy, SimpleITK, pydicom y pandas.

## Limitaciones conocidas

- La instalación en Windows no se ha probado (solo Linux con Python 3.11).
- Los códigos IBSI del diccionario están **por verificar** en el documento IBSI (no se pudo abrir desde aquí).
- El lector de DICOM-SEG está probado con DICOM-SEG sintéticos, no con los de un PACS ni con los de TCIA.
- El diámetro del control de calidad se mide entre centros de vóxel del borde (≈1 vóxel por debajo del real).
- La matriz de Spearman y la elección de Idm como «homogeneidad» siguen abiertas en el protocolo (bitácora B-001).

## Forma de trabajar

Este proyecto sigue el «plan socialista» de `fiebres-neutropenias`: reglas en `CLAUDE.md` y `autonomo/REGLAS.md`,
tareas en `autonomo/BITACORA.md` y `autonomo/TABLERO.md`. Guía: `autonomo/LEEME.md`.
