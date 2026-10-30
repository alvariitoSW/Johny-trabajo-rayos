# Dictamen de EDUCACIÓN y CIENCIA (metodólogo) · Consejo 30/10/2026
Fuentes: Prot = protocolo-v0 §; PyR = docstrings de pyRadiomics 3.1.0 (`fo`=firstorder.py, `sh`=shape.py, `glcm/glrlm/glszm`.py, :línea); vT = van Timmeren 2020 (Insights Imaging 11:91); KL = Koo y Li 2016 (resumen); Dic = docs/diccionario_variables.md. Datos de la prueba: SINTÉTICOS.

## 1. Asunto A: «ley» de explicación en llano
A FAVOR, con un límite. El usuario debe entender cada cifra (CLAUDE.md §1; REGLAS §8.5 «se entiende»). Pero el estudio es
descriptivo (Prot §11.4): explicar **qué mide** una característica es obligatorio; prometer **qué significa para el paciente** no
se puede, porque no son biomarcadores validados y vT avisa de «mistakes in the interpretation of the results (e.g., causation vs.
correlation)» y de la poca interpretabilidad de las texturas. Por eso la guía tiene tres niveles y solo el primero es seguro hoy:
(1) qué mide (PyR, literal); (2) qué se ve en la TC, solo con fuente radiológica primaria; (3) significado clínico: no se da.
Tres trampas que la guía debe decir siempre: GLN, SZN y superficie/volumen **dependen del tamaño** (Dic; `sh`:167); la curtosis de
PyR es la «no exceso», 3 más que IBSI (Dic); toda textura y la entropía cambian con el binWidth (Dic; 25 UH pendiente de Prot §9).
Correlaciones del tipo «entropía ↔ necrosis» o «heterogeneidad ↔ agresividad»: **necesita fuente** (p. ej. Lubner MG et al.,
RadioGraphics 2017, DOI 10.1148/rg.2017170056, no abierto aquí); hasta entonces, la columna «qué se ve» queda en blanco.

**PROPUESTA DE TEXTO (REGLAS §4, nuevo punto):**
> Toda cifra que llegue al usuario (tabla, figura, informe) va con una frase en llano: qué mide, en qué unidad y qué indica un
> valor alto, tomada de `docs/guia_interpretacion.md`. La guía separa tres niveles: qué mide (de la documentación del programa),
> qué se ve en la TC (solo con fuente radiológica citada con página) y significado clínico (no se da: el estudio es descriptivo,
> protocolo §11.4, y las características no son biomarcadores validados). Si falta la fuente, se escribe «sin fuente» y no se
> rellena. Cada estadístico (Dice, ICC con su IC 95 %, CV, mediana y RIC, Spearman) lleva su explicación de una frase y su límite.
> Las características que dependen del tamaño, del binWidth o con escala distinta a IBSI llevan su aviso. Nada de «válida/no
> válida» por un umbral de ICC (§11.3).

**ESQUEMA de la guía** (qué mide · valor alto = · qué se ve en TC · fuente)
- Primer orden: reparto de las UH dentro de la lesión, sin mirar dónde está cada vóxel · — · sin fuente · PyR `fo`:9
- Forma: tamaño y redondez del contorno dibujado; no depende de las UH · — · el contorno · PyR `sh`:13
- GLCM: con qué frecuencia dos vóxeles vecinos tienen cierto par de grises · — · sin fuente · PyR `glcm`:10
- GLRLM: rachas en línea recta de vóxeles con el mismo gris · — · sin fuente · PyR `glrlm`:8
- GLSZM: «manchas» 3D conectadas del mismo gris y su tamaño · — · sin fuente · PyR `glszm`:9
- Media (UH): atenuación media · lesión más densa · definición · Dic
- DE (UH): dispersión de las UH alrededor de la media · más variación · sin fuente · `fo`:331
- P10 / P90 (UH): UH por debajo de las que queda el 10 % / 90 % de vóxeles · cola baja / alta más densa · sin fuente · Dic
- Asimetría: si la cola larga va hacia UH altas (+) o bajas (−) · cola hacia UH altas · sin fuente · `fo`:355
- Curtosis (no exceso): masa en las colas frente a un pico en la media · más peso en colas · sin fuente · `fo`:386; Dic
- Entropía (bits): desorden de los valores del histograma · más desorden · necesita fuente (Lubner) · `fo`:164
- Volumen (mm³): volumen de la malla · lesión mayor · definición · `sh`:107
- Esfericidad (0-1): parecido a una esfera; 1 = esfera · más redonda · definición · `sh`:179-181
- Superficie/volumen (mm⁻¹): bajo = compacta; **depende del tamaño** · menos compacta o más pequeña · `sh`:167
- GLCM Contraste: diferencia de gris entre vecinos · vecinos más dispares · sin fuente · `glcm`:338
- GLCM IDM: homogeneidad local · vecinos más parecidos · sin fuente · `glcm`:611 (Idm o Id: duda abierta, Dic)
- GLCM Entropía conjunta: desorden de los pares de vecinos · más variable · sin fuente · `glcm`:468
- GLRLM SRE: peso de rachas cortas · textura más «fina» · sin fuente · `glrlm`:183
- GLRLM LRE: peso de rachas largas · textura más «gruesa» · sin fuente · `glrlm`:200
- GLRLM GLN: lo desigual de los grises; **depende del tamaño** · grises menos parecidos · sin fuente · `glrlm`:217; Dic
- GLSZM SAE: peso de zonas pequeñas · textura más fina · sin fuente · `glszm`:141
- GLSZM LAE: peso de zonas grandes · textura más gruesa · sin fuente · `glszm`:158
- GLSZM SZN: lo desigual de los tamaños de zona; **depende del tamaño** · más variedad de zonas · sin fuente · `glszm`:207
Estadísticos en llano:
- Dice (0-1): cuánto se solapan los dos contornos; 1 = idénticos (Prot §8, §11.3). Definición formal: necesita fuente (Dice 1945).
- HD95 (mm): «cuánto se separan los bordes en el peor 5 %». **No lo pide el protocolo** (§8 solo Dice): secundario, necesita fuente.
- ICC acuerdo absoluto + IC 95 %: si dos observadores dan el mismo número en cada lesión; KL: <0,5 pobre, 0,5-0,75 moderada,
  0,75-0,9 buena, >0,9 excelente, **leídos sobre el IC 95 %, no sobre el valor puntual**; decir modelo, tipo y definición (KL).
  vT: el ICC depende de lo distintas que sean las lesiones entre sí («natural variance»). Ej. sintético: P10 ICC 0,99, IC 0,18-1,00 (n = 6): no se sabe.
- CV (%): DE/media; solo en escalas con cero real (no UH, no asimetría) (Prot §11.2; features_prioritarias.yaml).
- Mediana y RIC: el valor del medio y dónde cae la mitad central de las lesiones (Prot §11.1-11.2).
- Spearman (−1 a 1): si dos características suben juntas por orden; solo para ver redundancia, nunca asociación clínica (Prot §11.2).

## 2. Asunto B: las 4 propuestas
**(1) Excluir automáticamente casos con alertas → EN CONTRA de lo automático; A FAVOR de revisar y contar.**
- <10 mm: es criterio de inclusión (Prot §5, §6), excluir es correcto, pero lo confirma el radiólogo en la imagen, no el script.
- Máscara vacía o geometría distinta: son fallos del proceso, no del paciente → rehacer la exportación o la segmentación.
- Varios componentes (SINT-008): Prot §6 pide UNA lesión y §8.5 todo el volumen tumoral → revisar: ¿dos lesiones (quedarse la
  índice y resegmentar) o un islote suelto (corregir)? Excluir sin mirar sesga la muestra hacia lesiones fáciles (§5 ya excluye
  las de límites mal definidos con criterio visual, no automático).
- Todo excluido se cuenta con su motivo en un diagrama de flujo: es el objetivo secundario 4, factibilidad (Prot §3).
**(2) Regla escrita del borde → A FAVOR, con cambios.** Prot §8.5-8.6 ya dice qué incluir; falta el «cómo» (ventana, plano,
  borde parcial). La erosión del contorno es «¿…?» en Prot §8: la decide el usuario con su tutor, no el agente. La regla se
  escribe y fecha **antes** de segmentar (como §6) y no se ajusta tras ver los ICC. El observador 2 no ve el contorno del 1.
  Valores de ventana: necesitan fuente; si se entrena, con casos fuera de la muestra de reproducibilidad.
**(3) Cautela con primer orden y GLCM si su ICC sale bajo → A FAVOR, con cambios.** Prot §11.3: se informan TODAS, por variable,
  con IC 95 %, sin umbral único de «válida»; no se quitan de las tablas (son las prioritarias de §10). La cautela se escribe junto
  a cada variable según SU IC real, no por familia ni por la prueba sintética (allí el sesgo lo creó la simulación).
  **Las fuentes discrepan**: vT propone «exclude non-reproducible features from further analyses»; Prot §11.3 pide informar todas.
  Manda el protocolo salvo que el usuario decida otra cosa.
**(4) 15 casos o más → A FAVOR.** Con 50 pacientes, 15 = 30 %, dentro del 20-30 % y del mínimo de 15 (Prot §8). Si tras excluir
  quedan menos de 50, mantener 15 (mínimo) y decirlo. Sorteo con semilla fija, antes de segmentar. Aviso: con n = 6 los IC salen
  inservibles (0,18-1,00); con 15 seguirán anchos. Un cálculo de precisión del ICC necesitaría fuente (no abierta aquí).

## 3. No comprobado / riesgo
Ninguna correlación radiológica o clínica está comprobada (Lubner y la definición de Dice/HD95 sin abrir); códigos IBSI (v) sin
verificar (Dic). Riesgo: que la guía en llano se lea como significado clínico y empuje a conclusiones que §11.4 no permite.
