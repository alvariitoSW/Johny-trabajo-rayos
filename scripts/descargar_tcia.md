# Casos públicos de prueba: colección «Colorectal-Liver-Metastases» (TCIA)

**Opcional.** Sirve para probar el pipeline con TC reales **públicas**, hacer el piloto de remuestreo y
discretización (protocolo §9) o preparar capturas del procedimiento **sin tocar datos del hospital**.
**No son casos del estudio** ni sustituyen a la cohorte del hospital.

> No se ha descargado nada desde este proyecto, y la red donde se escribió esta guía bloquea TCIA: lo marcado
> «(sin verificar)» hay que comprobarlo antes de usarlo.

## Qué es

- TC preoperatorias en **fase portal** de **197 pacientes** con metástasis hepáticas colorrectales, con
  segmentaciones en **DICOM-SEG** del hígado, el remanente hepático, las venas hepáticas y portal, y cada tumor
  («Tumor_1», «Tumor_2»…).
- Cita de los datos: Simpson AL, et al. Colorectal-Liver-Metastases (versión 2). The Cancer Imaging Archive.
  DOI 10.7937/QXK2-QG03. Hay que citar también TCIA y respetar su política de uso de datos.
- Licencia: **CC BY 4.0 según fuentes secundarias (sin verificar)**. Compruébala en la página de la colección
  (https://wiki.cancerimagingarchive.net/x/wQWwC) o en el portal de IDC
  (https://portal.imaging.datacommons.cancer.gov/collections/colorectal_liver_metastases) antes de usar nada.
- Ojo con el protocolo: la cohorte basal excluye tratamiento sistémico previo a la TC (§5). En esta colección
  muchos pacientes pudieron recibir quimioterapia antes de la cirugía (sin verificar: mira su descripción). Para
  una **prueba técnica** no importa; para cualquier análisis que se parezca al del estudio, sí.

## Descarga con `idc-index` (herramienta oficial de NCI Imaging Data Commons)

Funciona sin cuenta ni permisos de administrador. Usa **otro** entorno, no el del pipeline, y una carpeta fuera
del repositorio:

```bash
python -m venv venv-idc
venv-idc\Scripts\activate            # Windows   (Linux/macOS: source venv-idc/bin/activate)
pip install idc-index==0.13.4
```

Listar las series de unos pocos pacientes (consulta SQL sobre el índice de IDC):

```python
from idc_index import IDCClient

cliente = IDCClient.client()
series = cliente.sql_query("""
    SELECT PatientID, StudyInstanceUID, SeriesInstanceUID, Modality, SeriesDescription, series_size_MB
    FROM index
    WHERE collection_id = 'colorectal_liver_metastases'
    ORDER BY PatientID
    LIMIT 20
""")
print(series)
```

Descargar esas series (empieza por 3-5 pacientes: cada TC ocupa decenas de MB):

```python
cliente.download_dicom_series(seriesInstanceUID=series['SeriesInstanceUID'].tolist(),
                              downloadDir='../tcia_crlm')     # fuera del repositorio
```

El identificador `colorectal_liver_metastases` sale de la dirección del portal de IDC. Los nombres de columna son
los del ejemplo oficial de `idc-index` (sin verificar con esta colección).

## Pasarlo al formato del pipeline

Para cada paciente, con un **código nuevo** (no uses su PatientID de TCIA como nombre de carpeta):

```
data/crudo/CRLM-001/imagen/        ← los .dcm de la serie de TC (Modality = CT)
data/crudo/CRLM-001/mascara.dcm    ← el DICOM-SEG (Modality = SEG) de ese estudio
```

Y ejecútalo eligiendo como lesión índice **el tumor de mayor volumen**:

```bash
python run_pipeline.py --input data --output outputs --segmento mayor:Tumor
```

`--segmento mayor:Tumor` elige, entre los segmentos cuyo nombre contiene «Tumor», el de más vóxeles. Es una
aproximación automática a la regla del protocolo (§6: la de mayor volumen que cumpla RECIST 1.1); en el estudio,
la lesión índice la elige el radiólogo.

Limitaciones: el lector de DICOM-SEG del paso 1 está probado con DICOM-SEG sintéticos, no con los de esta
colección. Si sus segmentaciones no ocupan el corte entero o no caen exactamente en los cortes de la TC, el paso 1
avisará con un error en lugar de interpolar.

Estos datos son públicos, pero **tampoco se suben al repositorio** (el `.gitignore` bloquea `data/` y `*.dcm`).
