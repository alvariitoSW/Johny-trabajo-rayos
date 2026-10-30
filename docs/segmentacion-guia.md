# Guía de segmentación del borde

**Versión 0 · fecha: ____** (fijar ANTES de empezar a segmentar; no se cambia tras ver los ICC)

Firma del usuario: ________  Firma del tutor: ________

Esta guía es la regla escrita para los dos observadores. Solo recoge lo que ya fija el
[protocolo](protocolo/protocolo-v0.md). Lo que el protocolo deja abierto está en **blanco**
(apartado 6): lo deciden el usuario y su tutor, no el agente.

## 1. Qué lesión se segmenta (protocolo §6)

- Una sola metástasis por paciente: la lesión índice.
- Es la de **mayor volumen** que cumpla los criterios técnicos y de lesión diana de RECIST 1.1
  (diámetro máximo ≥ 10 mm, §5) y que pueda segmentarse bien.
- La regla se aplica igual en todos los pacientes y se fija **antes** de mirar las imágenes.
- Se registra de cada lesión: segmento hepático, diámetro máximo, volumen y si se ve necrosis.

## 2. Pasos (protocolo §8)

La segmentación es en 3D, a mano o semiautomática, sobre la TC en fase portal.

1. Importar la serie DICOM en 3D Slicer.
2. Identificar la lesión índice.
3. Dibujar el contorno en los cortes axiales de la lesión.
4. Revisar el resultado en coronal y sagital.
5. Incluir **todo** el volumen visible de la lesión: parte sólida y parte necrótica.
6. Excluir el parénquima hepático de alrededor y los vasos que no son del tumor.
7. Guardar la segmentación y apuntar su identificador.

Un radiólogo con experiencia en imagen abdominal revisa la segmentación (§8).

## 3. Cuándo una lesión no sirve (protocolo §5)

- Límites tan mal definidos que no se puede segmentar de forma reproducible.
- No se distingue con seguridad la metástasis del parénquima o de estructuras vecinas.
- Artefactos importantes (movimiento, endurecimiento del haz) que impiden segmentar con fiabilidad.

## 4. Segundo observador (protocolo §8)

- Segmenta de forma independiente: **no ve el contorno del primero**.
- Segmenta una muestra de lesiones elegida **por sorteo con semilla fija**, hecho antes de empezar a segmentar.
  Se sortea el 20-30 % de las lesiones, mínimo orientativo 15 (§8).
- La lista del sorteo se queda en el hospital.

## 5. Cómo guardar (3D Slicer)

- Guardar con `Ctrl+S` como `.seg.nrrd`.
- Un observador: `mascara.seg.nrrd`.
- Dos observadores: `mascara_obs1.seg.nrrd` y `mascara_obs2.seg.nrrd`.
- El README explica la carpeta de cada caso.

## 6. Pendiente: lo deciden el usuario y su tutor

El protocolo §8 lo deja abierto. No se rellena sin su decisión.

| Punto | Decisión |
|---|---|
| Erosión sistemática del contorno | sí / no · mm: ____ |
| Ventana de visualización | centro ____ UH · anchura ____ UH |
| ¿Se puede cambiar la ventana mientras se segmenta? | sí / no |
| Herramienta de Slicer | a mano / umbral / crecimiento de región: ____ |
| Suavizado del contorno | ____ |
| Vasos que atraviesan la lesión | ____ |
| Cápsula o halo de la lesión | ____ |
| Tiempo de segmentación (cronometrado, §10) | cómo se mide: ____ |

La ventana necesita fuente: no hay cifra citada en el protocolo.

## 7. Qué pasa si una lesión no cumple

- El pipeline **marca** la lesión con una alerta. No la excluye solo.
- El **radiólogo decide** si se incluye, se excluye o se revisa.
- La decisión se anota en `data/decisiones_casos.csv`, con las columnas `id,decision,motivo`.
- Cada caso excluido se cuenta, con su motivo, en el diagrama de flujo del estudio.
