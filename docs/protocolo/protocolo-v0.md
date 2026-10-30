# Protocolo de investigación

Estudio observacional retrospectivo de radiómica mediante TC y LIFEx (opción B 3D Slicer + SlicerRadiomics + jamovi)

## Título: 

Caracterización del perfil radiómico de las metástasis hepáticas de origen colorrectal mediante tomografía computarizada en fase portal: estudio observacional descriptivo retrospectivo.

## 1. Justificación

La radiómica permite extraer características cuantitativas de las imágenes médicas, incluyendo parámetros de intensidad, forma y textura que describen la distribución espacial de los valores de atenuación dentro de una lesión.

Las metástasis hepáticas de origen colorrectal constituyen un modelo interesante para este tipo de investigación, ya que presentan variabilidad morfológica y de atenuación relacionada, entre otros factores, con su composición tisular, vascularización, necrosis y cambios asociados al tratamiento.

Sin embargo, las características radiómicas también están condicionadas por factores técnicos, como el grosor de corte, la reconstrucción, la fase de adquisición y el procedimiento de segmentación.

Por ello, antes de investigar aplicaciones predictivas o pronósticas, resulta razonable desarrollar un estudio inicial que describa las características radiómicas de estas lesiones bajo condiciones técnicas estandarizadas.

La finalidad de este proyecto no es desarrollar un biomarcador diagnóstico ni pronóstico, sino establecer un perfil radiómico descriptivo y evaluar la viabilidad de su obtención en la práctica radiológica.

## 2. Pregunta de investigación

¿Cuál es la distribución de las características radiómicas de primer orden, morfológicas y de textura de las metástasis hepáticas de origen colorrectal, obtenidas mediante TC en fase portal y analizadas con el software LIFEx?

## 3. Objetivos

### Objetivo principal

Caracterizar el perfil radiómico de las metástasis hepáticas de origen colorrectal mediante el análisis cuantitativo de imágenes de TC en fase portal utilizando el software LIFEx (opción B 3D Slicer + SlicerRadiomics + jamovi).

### Objetivos secundarios

1.  Describir la distribución de las características de intensidad, forma y textura de las lesiones.
2.  Cuantificar la variabilidad de los parámetros radiómicos entre las metástasis estudiadas.
3.  Evaluar la reproducibilidad interobservador de una selección de características radiómicas.
4.  Describir la factibilidad del proceso de segmentación y extracción de características radiómicas en el entorno asistencial.

## 4. Diseño del estudio

Diseño: Observacional, retrospectivo, descriptivo, transversal.

Población: Adultos con metástasis hepáticas de adenocarcinoma colorrectal

Modalidad: TC abdominal con contraste intravenoso fase de adquisición portal.

Software de análisis: LIFEx (opción B 3D Slicer + SlicerRadiomics + jamovi).

Segmentación: Volumétrica tridimensional (3D)

Unidad primaria de análisis: Una metástasis por paciente

Periodo de inclusión: Según disponibilidad de casos.

Tipo de muestreo: Consecutivo, de casos elegibles.

Análisis: Estadística descriptiva y reproducibilidad.

## 5. Criterios de selección

### Criterios de inclusión

- Pacientes de 18 años o más.
- Diagnóstico anatomopatológico de adenocarcinoma colorrectal.
- Presencia de al menos una metástasis hepática de origen colorrectal confirmada mediante el contexto clínico, seguimiento radiológico o anatomía patológica.
- Disponibilidad de TC abdominal con contraste intravenoso en fase portal diagnóstico realizado en el centro hospitalario.
- Disponibilidad de imágenes DICOM originales con calidad suficiente para segmentación y análisis radiómico.
- Lesión índice con diámetro máximo igual o superior a 10 mm, como umbral operativo inicial para reducir problemas de volumen parcial y textura inestable (criterios de lesión medible y lesión diana Recist 1.1).

### Criterios de exclusión

- Metástasis hepáticas sometidas previamente a ablación, radioterapia, embolización u otro tratamiento locorregional.
- Tratamiento sistémico previo a la TC seleccionada, para la cohorte basal principal.
- Estudios sin fase portal adecuada o con protocolo técnico incompatible con el predefinido.
- Artefactos significativos de movimiento, endurecimiento del haz u otros que impidan una segmentación fiable.
- Lesiones de límites insuficientemente definidos para su segmentación reproducible.
- Lesiones en las que no sea posible distinguir de forma fiable la metástasis del parénquima hepático o de estructuras adyacentes.

## 6. Selección de la lesión índice

Para simplificar el estudio y evitar la dependencia estadística entre múltiples lesiones de un mismo paciente, se seleccionará una única metástasis hepática por paciente.

Se tratará de elegir la lesión de mayor volumen que cumpla todos los criterios técnicos (criterios de lesión medible y lesión diana Recist 1.1), siempre que pueda segmentarse adecuadamente. Esta regla deberá aplicarse sistemáticamente y quedar establecida antes de analizar las imágenes.

Se registrarán el segmento hepático, el diámetro máximo y el volumen de la lesión. También se documentará la presencia visual de necrosis, aunque no se realizarán comparaciones estadísticas entre lesiones necróticas y no necróticas como objetivo principal.

## 7. Protocolo de adquisición de TC

Se utilizarán exclusivamente las imágenes de TC abdominal adquiridas en fase portal, preferiblemente con los siguientes criterios de homogeneidad:

Fase de adquisición: Portal, aproximadamente 70 segundos tras iniciar la inyección, según protocolo local.

Contraste: Yodado intravenoso (Verificar marca)

Grosor de corte:

Algoritmo de reconstrucción: Partes blandas

Matriz: Habitualmente 512 × 512???

Orientación: Axial

Formato: DICOM original

Equipos: modelo y serie de TC (usar solo los hecho en uno solo TC para más homogeneidad???)

## 8. Segmentación de las metástasis mediante LIFEx

Se realizará segmentación tridimensional manual o semiautomática sobre la TC en fase portal.

### Procedimiento

1.  Importar la serie DICOM en LIFEx o 3D Slicer .
2.  Identificar la lesión índice.
3.  Delimitar el contorno de la lesión en los cortes axiales correspondientes.
4.  Revisar la segmentación en los planos coronal y sagital.
5.  Incluir la totalidad del volumen tumoral visible, tanto componentes sólidos como necróticos.
6.  Excluir el parénquima hepático adyacente y las estructuras vasculares extratumorales.
7.  Guardar la segmentación y registrar su identificador.

¿No se aplicará erosión sistemática del contorno, salvo que se decida y justifique previamente?. La segmentación será revisada por un radiólogo con experiencia en imagen abdominal.

### Reproducibilidad

Se propone seleccionar aleatoriamente el 20–30 % de las lesiones para una segunda segmentación independiente por otro observador, con un mínimo operativo orientativo de 15 casos si la muestra lo permite.

Se calcularán el coeficiente Dice para la concordancia espacial y el ICC de acuerdo absoluto para las características radiómicas seleccionadas, especificando el modelo estadístico empleado.

## 9. Preprocesamiento y extracción en LIFEx o 3D Slicer

Antes del análisis se fijará una configuración única de extracción, documentada para que pueda reproducirse.

Tipo de imagen: TC original en UH

Dimensionalidad: 3D

Remuestreo: Evaluar 1 × 1 × 1 mm como configuración piloto

Interpolación: Lineal para imagen; vecino más próximo para máscara, si se realiza externamente

Discretización: Anchura fija de intervalo de intensidad, por ejemplo 10 UH, sujeta a evaluación piloto

Filtros adicionales: Ninguno en el análisis principal

Extracción: Características originales de primer orden, forma y textura.

Nota: Son parámetros estándar y pueden variar según del programa y versión final utilizada

## 10. Variables 

### Variables clínicas y técnicas

Demográficas: Edad y sexo

Oncológicas: Localización del primario, fecha de diagnóstico, confirmación de enfermedad metastásica.

Tratamiento: Situación basal previa a tratamiento (Si/No).

Lesión: Segmento hepático, diámetro máximo, volumen y necrosis visual.

TC: Equipo, kVp, grosor, kernel, espaciado y protocolo de contraste.

Segmentación: Observador, método y tiempo de segmentación.

### Variables radiómicas principales

Se priorizará un conjunto reducido de características que cubra los distintos dominios:

- Primer orden: media, desviación estándar, percentiles 10 y 90, skewness, kurtosis y entropía discretizada.
- Forma: volumen, esfericidad y relación superficie/volumen.
- Textura: 1. GLCM: Contrast, Homogeneity, Entropy. 2. GLRLM :Short Run Emphasis, Long Run Emphasis, Gray-Level Non-Uniformity. 3. GLZLM: Short Zone Emphasis, Long Zone Emphasis, Zone Length Non-Uniformity

El diccionario definitivo incluirá para cada variable su nombre exacto en LIFEx o Slice 3D, definición, unidad, configuración de cálculo y correspondencia IBSI, cuando exista. No se asumirán equivalencias entre características que compartan nombres parecidos pero tengan fórmulas diferentes.

## 11. Plan de análisis estadístico

El análisis se realizará mediante SPSS, Python, SlicerRadiomics o jamovi después de exportar los resultados de LIFEx o Slice 3D a formato CSV.

### 11.1. Descripción de la muestra

Las variables categóricas se expresarán como frecuencias absolutas y porcentajes.

Las variables cuantitativas se describirán mediante media y desviación estándar o mediana y rango intercuartílico, según la distribución observada. Se presentarán además valores mínimos, máximos y datos ausentes.

### 11.2. Perfil radiómico

Para cada característica se calcularán:

- Media, mediana, desviación estándar y rango intercuartílico.
- Valores mínimo y máximo.
- Distribución mediante histogramas y/o diagramas de caja.
- Coeficiente de variación cuando resulte apropiado, evitando su uso para variables con medias cercanas a cero o escalas que no lo admitan.

¿Se podrá presentar una matriz de correlaciones de Spearman como análisis descriptivo exploratorio para identificar redundancia entre características, sin interpretarla como evidencia de asociación clínica?.

### 11.3. Reproducibilidad

Para las lesiones segmentadas por dos observadores se calcularán ICC de acuerdo absoluto con intervalos de confianza del 95 % y coeficientes Dice.

Se informarán los resultados por variable, sin utilizar exclusivamente un umbral arbitrario de ICC para declarar que una característica es válida.

### 11.4. Análisis no incluidos

Por tratarse de un estudio exclusivamente descriptivo, no se realizarán modelos de clasificación, regresión pronóstica, curvas ROC, aprendizaje automático ni selección de características basada en desenlaces.

Tampoco se efectuarán contrastes de hipótesis entre subgrupos como análisis principal.

## 12. Tamaño muestral

Se propone una muestra inicial de 50 pacientes y 50 lesiones, ampliable según disponibilidad de casos.

Esta cifra constituye un objetivo pragmático de factibilidad, no un tamaño muestral estadísticamente calculado.

## 13. Consideraciones éticas

El estudio se someterá a evaluación por el Comité de Ética de la Investigación correspondiente, junto con las autorizaciones institucionales necesarias.

Se utilizarán datos codificados y se eliminarán los identificadores personales de las copias de imágenes destinadas al análisis. ***Se comprobará que no permanezcan identificadores en metadatos DICOM ni en otros campos exportados.***

El procesamiento se realizará en equipos y entornos autorizados por el hospital, conforme al RGPD y a la normativa aplicable. La necesidad de consentimiento informado o su dispensa será determinada por el comité correspondiente.

## 14. Resultados esperados y limitaciones

Se espera obtener una descripción de las distribuciones de intensidad, morfología y textura de las metástasis hepáticas colorrectales de la cohorte estudiada, junto con información sobre la reproducibilidad y factibilidad del procedimiento.

Las principales limitaciones previstas son el carácter retrospectivo y unicéntrico, la selección de una sola lesión por paciente, la variabilidad técnica residual de las TC y la ausencia de correlación histopatológica o pronóstica de las características radiómicas.

Por tanto, los resultados se interpretarán como un perfil cuantitativo de la muestra estudiada, sin asumir que representa valores de referencia universales ni que permite establecer el comportamiento biológico de las lesiones.
