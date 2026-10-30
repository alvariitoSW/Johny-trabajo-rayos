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

## Cómo meter tus pacientes (paso a paso)
1. Exporta del PACS la **serie portal** de cada paciente a una carpeta de este PC (p. ej. `D:\estudio\export\p1\`).
2. Segmenta la **lesión índice** en 3D Slicer siguiendo `docs/segmentacion-guia.md` y guárdala como `.seg.nrrd`.
3. Abre la app (`lanzar_app.bat`) y, en **Nuevo caso**, escribe el **código de estudio** (`RMH-001`; nunca el nombre ni
   el NHC), la ruta de la carpeta DICOM y la ruta de la máscara (o las dos de los observadores).
4. Repite con cada paciente; en **Casos**, decide los que tengan alerta; en **Ejecutar**, lanza el pipeline.
5. La tabla que une cada código con su paciente la guardas tú, en el hospital, fuera de esta carpeta.

## Usarla desde el móvil: con el acceso remoto del hospital
La app escucha solo en `127.0.0.1` (el propio ordenador): así nadie de la red puede entrar y los datos de pacientes no
salen del PC. Para usarla desde el móvil (decisión del usuario del 30/10/2026), entra en este PC con el **acceso
remoto que dé Informática** (VPN o escritorio remoto) y abre la app ahí, como si estuvieras delante: la página se
adapta a la pantalla. Borrador de la petición a Informática: `docs/solicitud-acceso-remoto.md`.

No abras la app a la red ni a internet (túneles, redirección de puertos, servicios en la nube): sacaría datos de
pacientes de los equipos autorizados (protocolo §13).
