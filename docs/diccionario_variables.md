# Diccionario de variables radiómicas

Características prioritarias del estudio (`config/features_prioritarias.yaml`; protocolo §10), extraídas con
**pyRadiomics v3.1.0** (repositorio oficial, commit `6a761c4`) y `config/params.yaml`.

## Cómo leer esta tabla

- **Columna**: nombre exacto en `outputs/features.csv` (`original_<clase>_<característica>`).
- **Definición y desviaciones**: leídas en el **código y la documentación de pyRadiomics instalados**
  (docstrings de `radiomics/firstorder.py`, `shape.py`, `glcm.py`, `glrlm.py`, `glszm.py` e
  `imageoperations.py`, comprobados el 30/10/2026).
- **IBSI**: Zwanenburg A, et al. *Radiology* 2020;295(2):328-338, DOI 10.1148/radiol.2020191145
  (PMID 32154773). **El documento de referencia de IBSI no se pudo abrir desde este entorno** (la red bloquea
  arXiv, readthedocs y la web del editor). Por eso los **códigos IBSI** van con **(v)**: son los que conozco del
  documento IBSI y **hay que comprobarlos** en él antes de publicar. Los nombres IBSI que da la propia
  documentación de pyRadiomics van marcados «(pyRadiomics)».
- **LIFEx**: no se asume ninguna equivalencia con LIFEx. Que dos características se llamen parecido (p. ej.
  «Homogeneity», «GLZLM ZLNU») no significa que tengan la misma fórmula, discretización ni agregación entre
  direcciones (protocolo §10). Para comparar con LIFEx hace falta su documentación, que no se ha consultado.

## Configuración común (params.yaml)

| Ajuste | Valor | Afecta a |
|---|---|---|
| Imagen | original, UH, sin filtros, sin normalizar | todas |
| Dimensión | 3D (`force2D: false`) | todas |
| Remuestreo | 1 × 1 × 1 mm; imagen con interpolación lineal (`sitkLinear`); máscara con vecino más próximo (fijo en pyRadiomics) | todas |
| Discretización | anchura fija (`binWidth`), 25 UH por defecto (o 10 con `--binwidth 10`) | entropía del histograma, uniformidad y todas las texturas |
| GLCM | distancia 1 (13 direcciones en 3D), matriz simétrica | GLCM |
| Agregación | GLCM y GLRLM: la característica se calcula en cada dirección y se promedia | GLCM, GLRLM |
| GLSZM | zonas conectadas en 26-vecindad, una sola matriz 3D | GLSZM |

**Desviaciones generales de pyRadiomics respecto a IBSI** (de su documentación):
1. **Discretización de anchura fija**: pyRadiomics usa división entera hacia abajo (y suma 1), no hacia arriba, y
   los límites de los intervalos están **equiespaciados desde 0**, no desde el mínimo de la lesión. Ejemplo de su
   documentación: UH de 54 a 166 con anchura 25 → límites 50, 75, 100, 125, 150 y 175. Afecta a todo lo
   discretizado.
2. **Rejilla de remuestreo**: pyRadiomics la alinea con el origen de la imagen de entrada y remuestrea solo la caja
   de la lesión más un margen (`padDistance`). Cómo alinea la rejilla IBSI: **por verificar** en el documento IBSI.
3. **ε en los logaritmos**: las entropías usan log₂(p + ε), con ε ≈ 2,2 × 10⁻¹⁶. Diferencia despreciable.

## Primer orden (sobre las UH remuestreadas y SIN discretizar, salvo la entropía)

| Característica | Columna | Definición (pyRadiomics) | Unidad | IBSI | Desviaciones conocidas |
|---|---|---|---|---|---|
| Media | `original_firstorder_Mean` | media de las UH de los vóxeles de la lesión | UH | Mean (intensidad), Q4LE (v) | ninguna descrita |
| Desviación estándar | `original_firstorder_StandardDeviation` | √(Σ(X − media)² / N): DE **poblacional** (divide entre N, no N − 1) | UH | **No está en IBSI** (pyRadiomics); IBSI define la varianza (ECT3 (v)) | pyRadiomics la marca «deprecated» y **no la calcula si no se nombra**; por eso `params.yaml` lista firstorder entera |
| Percentil 10 | `original_firstorder_10Percentile` | percentil 10 de las UH (`numpy.nanpercentile`, interpolación lineal) | UH | 10th percentile, QG58 (v) | método de interpolación del percentil: por verificar frente a IBSI |
| Percentil 90 | `original_firstorder_90Percentile` | percentil 90, igual que el anterior | UH | 90th percentile, 8DWT (v) | igual que P10 |
| Asimetría | `original_firstorder_Skewness` | μ₃ / σ³ (momentos con divisor N) | — | Skewness, KE2A (v) | en una lesión sin variación (σ = 0) pyRadiomics devuelve 0 |
| Curtosis | `original_firstorder_Kurtosis` | μ₄ / σ⁴ (momentos con divisor N) | — | Kurtosis, IPH6 (v) | **IBSI usa la curtosis en exceso (− 3). pyRadiomics no resta 3: su valor es 3 más alto que el IBSI** (documentado por pyRadiomics) |
| Entropía | `original_firstorder_Entropy` | −Σ p(i) log₂(p(i) + ε) sobre el **histograma discretizado** | bits | Intensity histogram entropy (pyRadiomics), TLU2 (v) | depende de `binWidth` y de la discretización (desviación general 1) |

## Forma (sobre la máscara remuestreada; no depende de la discretización)

| Característica | Columna | Definición (pyRadiomics) | Unidad | IBSI | Desviaciones conocidas |
|---|---|---|---|---|---|
| Volumen | `original_shape_MeshVolume` | volumen encerrado por la malla triangular de la superficie (suma de tetraedros con signo) | mm³ | Volume (mesh) (pyRadiomics), RNU0 (v) | ninguna descrita. El volumen por recuento de vóxeles es otra columna (`original_shape_VoxelVolume`, IBSI «Approximate volume») |
| Esfericidad | `original_shape_Sphericity` | ∛(36 π V²) / A, con V y A de la malla; 1 = esfera | — | Sphericity, QCFX (v) | ninguna descrita |
| Superficie/volumen | `original_shape_SurfaceVolumeRatio` | A / V (superficie de la malla entre volumen de la malla). **Depende del tamaño** de la lesión | mm⁻¹ | Surface to volume ratio, 2PR5 (v) | ninguna descrita |

Para el control de calidad se usa además `original_shape_Maximum3DDiameter` (mayor distancia entre vértices de la
malla; IBSI «Maximum 3D diameter», L0JK (v)). El criterio de ≥ 10 mm de RECIST 1.1 se aplica en `03_qc.py` sobre el
**diámetro axial**, no sobre el 3D.

## GLCM: matriz de co-ocurrencia (discretizada; distancia 1; 13 direcciones; simétrica; media de las direcciones)

| Característica | Columna | Definición (pyRadiomics) | Unidad | IBSI | Desviaciones conocidas |
|---|---|---|---|---|---|
| Contraste | `original_glcm_Contrast` | Σ (i − j)² p(i,j) | — | Contrast, ACUI (v) | agregación entre direcciones: media de las 13 (en IBSI, por verificar cuál de sus métodos equivale) |
| Homogeneidad | `original_glcm_Idm` | IDM = Σₖ p₍ₓ₋ᵧ₎(k) / (1 + k²). pyRadiomics la llama también «Homogeneity 2» | — | Inverse difference moment, WF0Z (v) | **Ambigüedad**: el protocolo dice «Homogeneity». pyRadiomics tiene dos: **Idm** («Homogeneity 2», la elegida) e **Id** = Σₖ p₍ₓ₋ᵧ₎(k) / (1 + k) («Homogeneity 1», columna `original_glcm_Id`, IBSI Inverse difference, IB1Z (v)). Las dos se extraen; hay que decidir cuál se informa como principal |
| Entropía conjunta | `original_glcm_JointEntropy` | −Σ p(i,j) log₂(p(i,j) + ε) | bits | Joint entropy (pyRadiomics), TU9B (v) | ε (desviación general 3) |

## GLRLM: longitud de series (discretizada; 13 direcciones; media de las direcciones)

N_r(θ) = número de series en la dirección θ.

| Característica | Columna | Definición (pyRadiomics) | Unidad | IBSI | Desviaciones conocidas |
|---|---|---|---|---|---|
| SRE | `original_glrlm_ShortRunEmphasis` | Σ P(i,j\|θ) / j², dividido entre N_r(θ) | — | Short runs emphasis, 22OV (v) | agregación: media de las direcciones |
| LRE | `original_glrlm_LongRunEmphasis` | Σ P(i,j\|θ) · j², dividido entre N_r(θ) | — | Long runs emphasis, W4KF (v) | igual |
| GLN | `original_glrlm_GrayLevelNonUniformity` | Σᵢ (Σⱼ P(i,j\|θ))², dividido entre N_r(θ). **Depende del tamaño** de la lesión (no normalizada) | — | Grey level non-uniformity (GLRLM), R5YN (v) | igual; la versión normalizada es `original_glrlm_GrayLevelNonUniformityNormalized` |

## GLSZM: tamaño de zonas (discretizada; zonas en 26-vecindad; una matriz 3D)

N_z = número de zonas. En LIFEx esta familia se llama **GLZLM**; no se asume que las fórmulas coincidan.

| Característica | Columna | Definición (pyRadiomics) | Unidad | IBSI | Desviaciones conocidas |
|---|---|---|---|---|---|
| SAE | `original_glszm_SmallAreaEmphasis` | Σ P(i,j) / j², dividido entre N_z | — | Small zone emphasis, 5QRC (v) | ninguna descrita |
| LAE | `original_glszm_LargeAreaEmphasis` | Σ P(i,j) · j², dividido entre N_z | — | Large zone emphasis, 48P8 (v) | ninguna descrita |
| SZN | `original_glszm_SizeZoneNonUniformity` | Σⱼ (Σᵢ P(i,j))², dividido entre N_z. Es el equivalente pyRadiomics de la «Zone Length Non-Uniformity» que pide el protocolo para LIFEx. **Depende del tamaño** de la lesión | — | Zone size non-uniformity, 4JP3 (v) | ninguna descrita; la normalizada es `original_glszm_SizeZoneNonUniformityNormalized` |

## Pendiente

1. Comprobar cada código IBSI marcado (v) en el documento de referencia IBSI (copia abierta citada en
   `autonomo/ideas/webs-radiologia.md`) y comprobar cómo alinea IBSI la rejilla de remuestreo.
2. Decidir **Idm o Id** como «homogeneidad» principal (hoy: Idm).
3. Si alguna vez se compara con LIFEx: sacar sus fórmulas de su documentación y escribir aquí las diferencias.
