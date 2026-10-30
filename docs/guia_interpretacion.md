# Guía para leer los resultados

Para quien lee el informe del estudio en el móvil. Explica cada cifra en llano: qué mide, qué indica un valor alto
y dónde está la trampa. Los ejemplos numéricos salen de la **prueba con datos sintéticos** (10 lesiones
inventadas, 6 con dos observadores): no describen a ningún paciente.

**Fuentes** (abreviadas en el texto):
- **Prot**: protocolo del estudio (v0), con su §.
- **PyR**: documentación dentro del código de pyRadiomics 3.1.0, `archivo:línea`
  (`fo` = firstorder.py, `sh` = shape.py, `glcm`, `glrlm`, `glszm`).
- **Dic**: diccionario de variables del estudio.
- **vT**: van Timmeren JE et al. Radiomics in medical imaging, «how-to» guide and critical reflection.
  *Insights Imaging* 2020;11:91. DOI 10.1186/s13244-020-00887-2 (acceso abierto, PMC7423816). Se cita por apartado.
- **KL**: Koo TK, Li MY. *J Chiropr Med* 2016;15(2):155-163. PMID 27330520 (resumen).
- **GM**: Ganeshan B, Miles KA. Quantifying tumour heterogeneity with CT. *Cancer Imaging* 2013;13:140-149.
  DOI 10.1102/1470-7330.2013.0015.
- **pg**: documentación de pingouin (`reliability.py`); **mpl**: documentación de matplotlib 3.10
  (`axes/_axes.py`).

---

## 1. Cómo leer este informe en 2 minutos

**Qué es la radiómica, en tres frases.**
1. Convierte la imagen en números con fórmulas matemáticas (vT, Background).
2. Dentro del contorno de la lesión mide tres cosas: cuántas UH tiene (primer orden), qué forma tiene el contorno
   (forma) y cómo se colocan los grises unos junto a otros (texturas) (PyR `fo`:9-10, `sh`:9, `glcm`:9-13).
3. Cada número sale de una fórmula concreta del programa; otro programa con un nombre parecido puede dar otro
   número (Prot §10).

**Qué se puede concluir.**
- Cómo son, en cifras, las lesiones de esta muestra (Prot §11.2).
- Si dos radiólogos que segmentan la misma lesión obtienen las mismas cifras (Prot §11.3).

**Qué NO se puede concluir.**
- Nada sobre pronóstico, respuesta ni diagnóstico. El estudio es descriptivo: sin modelos, sin curvas ROC, sin
  comparar grupos (Prot §11.4).
- Estas cifras **no son biomarcadores validados**. vT avisa de la falta de validación y del riesgo de falsos
  positivos (vT, Current limitations).
- Que dos cifras vayan juntas no quiere decir que una cause la otra. vT señala como error frecuente confundir
  correlación con causa (vT, Current limitations).

**Los tres niveles de cada explicación.**
1. **Qué mide**: sale de la documentación del programa. Es seguro.
2. **Qué se ve en la TC**: solo si una fuente radiológica lo dice. Casi siempre pone «sin fuente».
3. **Qué significa para el paciente**: no se da. Este estudio no puede contestarlo (Prot §11.4).

**Orden de lectura.** Primero, el control de calidad (¿hay casos raros?). Después, la reproducibilidad
(¿se mide igual con otro observador?). Por último, el perfil de las lesiones. Una cifra que no se reproduce entre
observadores se lee con cautela.

---

## 2. Los estadísticos

Cada uno: qué es, un ejemplo de la prueba sintética y su límite.

### Media y desviación estándar (DE)
- **Media**: la suma de los valores entre el número de lesiones.
- **DE**: cuánto se separan las lesiones de esa media, de promedio.
- Ejemplo: la atenuación media de las 10 lesiones fue 64,3 ± 7,6 UH.
- Cuándo: si los valores se reparten de forma más o menos simétrica (Prot §11.1, «según la distribución
  observada»).

### Mediana y rango intercuartílico (RIC)
- **Mediana**: el valor del medio al ordenar las lesiones de menor a mayor.
- **RIC**: del percentil 25 al 75. Ahí cae la mitad central de las lesiones.
- Ejemplo: GLRLM LRE tuvo media 21,7 pero mediana 9,0 (RIC 6,3-12,6). Una lesión con 119 tira de la media hacia
  arriba; la mediana casi no se mueve.
- Cuándo: si hay valores extremos o la distribución está torcida (Prot §11.1 deja elegir según la
  distribución; la regla práctica de esta línea es opinión del autor, sin fuente).

### Mínimo y máximo
- El valor más bajo y el más alto de la muestra (Prot §11.1-11.2).
- Ejemplo: el volumen fue de 251 a 17.162 mm³.
- Límite: dependen de una sola lesión. Un error de segmentación se ve aquí primero.

### Ausentes
- Un campo vacío es un **dato ausente**, nunca un 0. Se cuenta y se informa (Prot §11.1).
- Ejemplo: en la prueba no faltó ningún valor (0 ausentes en las 19).

### Coeficiente de variación (CV)
- **CV** = DE / media × 100. Dice cuánto varía una cifra en proporción a su tamaño.
- Ejemplo: el volumen tuvo un CV del 74 %; la esfericidad, del 5 %.
- **No se calcula en UH**, ni en la asimetría, ni con medias cercanas a 0 (Prot §11.2). En UH el 0 es el agua,
  no la ausencia de algo: el cociente no tiene sentido (la escala de las UH con el agua en 0 consta en la
  configuración del estudio; fuente primaria de la escala, sin abrir aquí).

### Histograma y diagrama de caja
Cada característica tiene una figura con dos partes (Prot §11.2).
- **Histograma** (arriba): barras. Cada barra cuenta cuántas lesiones caen en ese tramo de valores.
- **Diagrama de caja** (abajo), según la documentación del programa que lo dibuja (mpl:3911-3917):
  - **La caja** va del percentil 25 al 75 (el RIC).
  - **La línea roja** dentro de la caja es la mediana.
  - **Los bigotes** llegan hasta el dato más lejano que esté a menos de 1,5 RIC de la caja.
  - **Los puntos sueltos** quedan más allá de los bigotes: lesiones atípicas. Se miran en la imagen; no se borran.

### Correlación de Spearman (ρ)
- Va de −1 a 1. Mide si dos características suben juntas al **ordenar** las lesiones (pandas, «Spearman rank
  correlation»).
- ρ cerca de 1: cuando una sube, la otra también. Cerca de −1: una sube y la otra baja. Cerca de 0: no van juntas.
- Ejemplo: volumen y superficie/volumen, ρ = −0,99. Dicen casi lo mismo: son **redundantes**.
- Sirve **solo** para ver redundancia entre características, nunca asociación clínica (Prot §11.2). vT usa estas
  matrices para ver grupos de características muy correlacionadas (vT, Feature selection).

### Dice
- Mide cuánto se solapan los contornos de dos observadores. Va de 0 (nada) a 1 (idénticos) (Prot §8, §11.3).
- Fórmula que usa el estudio: 2 × volumen común / (volumen 1 + volumen 2). La referencia original de Dice
  (1945) no se ha abierto: **pendiente de cita primaria**.
- Ejemplo: Dice mediano 0,88 (de 0,70 a 0,90). El más bajo fue la lesión de 8 mm.
- Límite: un Dice alto no asegura que las cifras coincidan. Muchas características cambian con pequeñas
  diferencias del contorno (vT, Image segmentation). Eso lo mide el ICC.

### HD95 (distancia de Hausdorff al 95 %)
- **Dato extra: el protocolo solo pide Dice** (Prot §8).
- En mm. Para cada punto del borde de un contorno se mide la distancia al borde del otro. Se toma el valor que deja
  por debajo el 95 % de los puntos, en los dos sentidos, y se informa el mayor. 0 = bordes idénticos.
- Ejemplo: HD95 mediano 2,5 mm: en la mitad de los casos, el 95 % del borde de un observador queda a ≤ 2,5 mm del
  otro.
- Referencia primaria: **sin fuente** abierta aquí.

### ICC de acuerdo absoluto, con IC 95 %
- **Qué es**: el coeficiente de correlación intraclase. Compara lo que varía la cifra de una misma lesión entre
  observadores con lo que varía entre todas las lesiones (pg:196-198). Cerca de 1: los dos observadores dan casi
  el mismo número en cada lesión.
- **Modelo del estudio**: ICC(2,1). Dos factores, efectos aleatorios, acuerdo absoluto, medida única
  (pg:211-214). KL pide decir siempre modelo, tipo y definición.
- **El IC 95 % importa más que el número.** El IC es el rango donde probablemente está el ICC real. KL lee los
  tramos sobre el IC, no sobre el valor:
  - menos de 0,5: pobre;
  - 0,5 a 0,75: moderada;
  - 0,75 a 0,9: buena;
  - más de 0,9: excelente.
- **Ejemplo sintético**: percentil 10, ICC 0,99 con IC 0,18 a 1,00 en 6 casos. El IC va de «pobre» a
  «excelente»: **no se sabe** si es reproducible.
- **Depende de lo distintas que sean las lesiones entre sí**: el ICC se apoya en la variación natural de los
  datos (vT, Feature selection). Con lesiones muy parecidas, el ICC baja aunque los observadores coincidan.
- **Con 15 casos el IC seguirá ancho.** Más casos estrechan el IC, pero cuánto con 15 hay que calcularlo; ese
  cálculo necesita una fuente que no se ha abierto aquí (**sin fuente**).
- No hay un umbral que declare «válida» una característica: se informa cada una con su IC (Prot §11.3).

---

## 3. Fichas de las 19 características prioritarias

Cada ficha: **qué mide** (nivel 1) · **valor alto** · **en la TC** (nivel 2) · **avisos**. El nivel 3
(significado clínico) no se da en ninguna (Prot §11.4).

**Nivel 2 de las texturas, como familia.** GM dice que el análisis de textura en TC puede reflejar, entre otras
cosas, hipoxia y angiogénesis del tumor (GM, resumen, p. 140). GM usa otro método (filtros e histograma, no las
matrices de pyRadiomics). Por eso **no** se traslada a ninguna característica concreta: en cada ficha pone
«sin fuente».

**Avisos que se repiten.**
- **binWidth** (anchura de intervalo): las UH se agrupan en tramos antes de calcular la entropía y las texturas.
  Otra anchura da otros valores (vT, Image processing; Dic). Por defecto 25 UH, pendiente de pasar al protocolo
  (Prot §9).
- **Depende del tamaño**: la cifra crece o baja con el volumen de la lesión, no solo con su aspecto (PyR `sh`:167;
  Dic).

### Primer orden: las UH dentro de la lesión
Describen cómo se reparten las UH de los vóxeles, sin mirar dónde está cada uno (PyR `fo`:9-10).

**1. Media** · `original_firstorder_Mean` · UH
- Mide: la atenuación media, promedio de las UH de la lesión (PyR `fo`:221).
- Alto: la lesión atenúa más de media.
- En la TC: es la atenuación media de la lesión (definición; Dic).
- Aviso: escala UH, sin CV (Prot §11.2).

**2. Desviación estándar** · `original_firstorder_StandardDeviation` · UH
- Mide: cuánto se apartan las UH de cada vóxel de la media de su lesión (PyR `fo`:331).
- Alto: las UH varían más dentro de la lesión.
- En la TC: sin fuente.
- Aviso: es la variación dentro de una lesión, no la DE entre lesiones de las tablas. Divide entre N (Dic).

**3. Percentil 10** · `original_firstorder_10Percentile` · UH
- Mide: las UH por debajo de las que queda el 10 % de los vóxeles, la parte menos densa (PyR `fo`:187-189; Dic).
- Alto: hasta la parte menos densa tiene UH altas.
- En la TC: sin fuente.
- Aviso: escala UH, sin CV.

**4. Percentil 90** · `original_firstorder_90Percentile` · UH
- Mide: las UH por debajo de las que queda el 90 % de los vóxeles, la parte más densa (PyR `fo`:195-197; Dic).
- Alto: la parte más densa tiene más UH.
- En la TC: sin fuente.
- Aviso: escala UH, sin CV.

**5. Asimetría** · `original_firstorder_Skewness` · sin unidad
- Mide: si el histograma de UH es simétrico o tiene una cola más larga hacia un lado (PyR `fo`:355-356).
- Alto (positivo): cola larga hacia UH altas; negativo, hacia UH bajas (se deduce de la fórmula μ₃/σ³,
  `fo`:349-351; el texto de PyR no dice el sentido).
- En la TC: sin fuente.
- Aviso: puede ser negativa, sin CV. Sin variación, pyRadiomics da 0 (PyR `fo`:363-364).

**6. Curtosis (no exceso)** · `original_firstorder_Kurtosis` · sin unidad
- Mide: si las UH se agolpan en un pico junto a la media o se reparten hacia las colas (PyR `fo`:386-388).
- Alto: más vóxeles con UH lejos de la media.
- En la TC: sin fuente.
- Aviso: **pyRadiomics no resta 3**. Su valor es 3 más alto que la curtosis IBSI (PyR `fo`:399-400).

**7. Entropía (histograma)** · `original_firstorder_Entropy` · bits
- Mide: el desorden de las UH, ya agrupadas en intervalos (PyR `fo`:164-165).
- Alto: UH menos predecibles.
- En la TC: sin fuente.
- Aviso: **cambia con el binWidth**.

### Forma: el contorno dibujado
Tamaño y forma 3D de la segmentación; no dependen de las UH (PyR `sh`:9-11).

**8. Volumen (malla)** · `original_shape_MeshVolume` · mm³
- Mide: el volumen de la lesión, sobre una malla de su superficie (PyR `sh`:106).
- Alto: lesión más grande.
- En la TC: el tamaño del contorno dibujado (definición).
- Aviso: cambia si cambia la segmentación.

**9. Esfericidad** · `original_shape_Sphericity` · 0 a 1
- Mide: cuánto se parece la forma a una esfera (PyR `sh`:179-182).
- Alto: más redonda; 1 = esfera perfecta.
- En la TC: la redondez del contorno dibujado (definición).
- Aviso: ninguno.

**10. Superficie/volumen** · `original_shape_SurfaceVolumeRatio` · mm⁻¹
- Mide: la superficie entre el volumen. Bajo = forma compacta (PyR `sh`:167).
- Alto: forma menos compacta, o lesión más pequeña.
- En la TC: sin fuente.
- Aviso: **depende del tamaño** (PyR `sh`:167-168). En la prueba, ρ = −0,99 con el volumen.

### GLCM: parejas de vóxeles vecinos
Cuenta cuántas veces aparecen juntos, a un vóxel de distancia, dos niveles de gris (PyR `glcm`:9-13).

**11. GLCM Contraste** · `original_glcm_Contrast` · sin unidad
- Mide: la diferencia de gris entre vecinos (PyR `glcm`:338-339).
- Alto: vecinos más distintos entre sí.
- En la TC: sin fuente.
- Aviso: cambia con el binWidth.

**12. GLCM Homogeneidad (IDM)** · `original_glcm_Idm` · sin unidad
- Mide: la homogeneidad local, cuánto se parecen los vecinos (PyR `glcm`:611-613).
- Alto: vecinos más parecidos.
- En la TC: sin fuente.
- Aviso: cambia con el binWidth. **Pendiente**: Idm o Id como homogeneidad principal (Dic).

**13. GLCM Entropía conjunta** · `original_glcm_JointEntropy` · bits
- Mide: el desorden de las parejas de grises vecinos (PyR `glcm`:468).
- Alto: parejas más variadas.
- En la TC: sin fuente.
- Aviso: cambia con el binWidth.

### GLRLM: rachas en línea recta
Una racha es un tramo recto de vóxeles seguidos con el mismo gris (PyR `glrlm`:8-11).

**14. GLRLM SRE** · `original_glrlm_ShortRunEmphasis` · sin unidad
- Mide: el peso de las rachas cortas (PyR `glrlm`:183-184).
- Alto: más rachas cortas, textura más fina (PyR).
- En la TC: sin fuente.
- Aviso: cambia con el binWidth.

**15. GLRLM LRE** · `original_glrlm_LongRunEmphasis` · sin unidad
- Mide: el peso de las rachas largas (PyR `glrlm`:200-201).
- Alto: más rachas largas, textura más gruesa (PyR).
- En la TC: sin fuente.
- Aviso: cambia con el binWidth.

**16. GLRLM GLN** · `original_glrlm_GrayLevelNonUniformity` · sin unidad
- Mide: lo distintos que son los grises entre sí, contados por rachas (PyR `glrlm`:217-218).
- Alto: grises menos parecidos.
- En la TC: sin fuente.
- Aviso: **depende del tamaño**: no está normalizada (Dic; la versión normalizada es otra columna, PyR
  `glrlm`:228-235). Cambia con el binWidth.

### GLSZM: manchas del mismo gris
Una zona es un grupo de vóxeles unidos (también en diagonal) con el mismo gris (PyR `glszm`:9-11).

**17. GLSZM SAE** · `original_glszm_SmallAreaEmphasis` · sin unidad
- Mide: el peso de las zonas pequeñas (PyR `glszm`:141-142).
- Alto: más zonas pequeñas, textura más fina (PyR).
- En la TC: sin fuente.
- Aviso: cambia con el binWidth.

**18. GLSZM LAE** · `original_glszm_LargeAreaEmphasis` · sin unidad
- Mide: el peso de las zonas grandes (PyR `glszm`:158-159).
- Alto: más zonas grandes, textura más gruesa (PyR).
- En la TC: sin fuente.
- Aviso: cambia con el binWidth.

**19. GLSZM SZN** · `original_glszm_SizeZoneNonUniformity` · sin unidad
- Mide: lo variados que son los tamaños de las zonas (PyR `glszm`:207-208).
- Alto: tamaños de zona más variados.
- En la TC: sin fuente.
- Aviso: **depende del tamaño** (Dic). Cambia con el binWidth.

---

## 4. Errores típicos al leer radiómica

1. **Leer una cifra como diagnóstico o pronóstico.** El estudio es descriptivo y las características no están
   validadas (Prot §11.4; vT, Current limitations).
2. **Confundir correlación con causa.** Que la entropía y otra cifra suban juntas no dice por qué (vT, Current
   limitations).
3. **Fiarse del ICC sin mirar su IC.** Un 0,99 con IC 0,18-1,00 no informa de nada (KL).
4. **Creer que dos programas miden lo mismo** porque la característica se llama igual (Prot §10; Dic).
5. **Comparar texturas calculadas con distinto binWidth.** Cambian los valores (vT, Image processing; Dic).
6. **Leer como «aspecto» lo que es tamaño.** GLN, SZN y superficie/volumen dependen del volumen (PyR `sh`:167;
   Dic).
7. **Dar por reproducible una característica porque el Dice es alto.** Muchas cambian con pequeñas diferencias de
   contorno (vT, Image segmentation).
