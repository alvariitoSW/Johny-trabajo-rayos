# App local

Una página web que corre **en el propio PC del hospital**. Sirve para preparar casos y lanzar el pipeline sin
escribir órdenes.

## Qué hace
- Copia la serie DICOM y la máscara de un caso a `data/crudo/<código>/`.
- Lista los casos, muestra las alertas de calidad y guarda tu decisión (incluir, excluir o revisar, con un motivo
  corto) en `data/decisiones_casos.csv` (columnas `id,decision,motivo`).
- Lanza `run_pipeline.py` y muestra su salida en directo.
- Abre `informe.pdf` y las figuras de la carpeta de resultados.

## Cómo se abre
- Windows: doble clic en `lanzar_app.bat`. Linux o Mac: `./lanzar_app.sh`.
- A mano: `python app/servidor.py --datos data --resultados outputs`.
- Se imprime una dirección con un código secreto (`?t=…`). Ábrela en el navegador de ese mismo PC.
  El código cambia cada vez que arrancas la app.

## Qué NO hace
- No sube nada a internet ni usa recursos externos.
- No recibe archivos por el navegador: tú escribes la ruta y la app copia desde el disco.
- No borra ni modifica tus archivos originales. No sobrescribe un caso que ya existe.
- No guarda registro de lo que haces. No muestra nombres de archivo originales.
- No analiza: el análisis sigue siendo el del pipeline (protocolo §11.4).

## Cómo se cierra
`Ctrl+C` en la ventana negra.

## Por qué no abre desde el móvil
Escucha solo en `127.0.0.1`, es decir, en el propio ordenador. Es a propósito: así nadie de la red del hospital
puede entrar, y los datos de pacientes no salen del PC.
