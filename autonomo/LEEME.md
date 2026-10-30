# Plan socialista: guía para el usuario

Es la misma forma de trabajar que en `fiebres-neutropenias`: un equipo de agentes que trabaja por tareas, con
reglas, jueces y un parte al final. Aquí no se hace una app: se preparan y analizan los datos del **protocolo de
radiómica** (`docs/protocolo/protocolo-v0.md`). No hace falta saber programar: basta con saber qué pedir y revisar
lo que entrega.

## Las piezas, en una frase cada una

| Pieza | Dónde está | Qué es |
|---|---|---|
| **El director** | `.claude/skills/plan-socialista/SKILL.md` | Se activa con `/plan-socialista`. No escribe: elige la tarea, reparte el trabajo, juzga y decide. |
| **Los 7 trabajadores** | `.claude/agents/*.md` | Lector de fuente, constructor, verificador, auditor ciego, revisor de código, **metodólogo** (diseña y juzga el análisis; el modelo más potente) y revisor. |
| **Los jueces** | `autonomo/jueces.py` | Comprobador automático: que no se suba ningún dato de paciente y que las pruebas de los cálculos (ICC, Dice…) den lo que deben. `python3 autonomo/jueces.py`. |
| **Las reglas** | `autonomo/REGLAS.md` | Lo que nadie se salta: no inventar, fidelidad al protocolo, datos protegidos, análisis solo descriptivo. |
| **La bitácora** | `autonomo/BITACORA.md` + `/bitacora` | Tu cuaderno: le cuentas lo que hay que hacer, lo convierte en tareas que esperan tu visto bueno y te dice «a dónde nos dirigimos». |
| **El tablero** | `autonomo/TABLERO.md` | Las tareas **aprobadas**, en orden, y qué significa «hecho». Es lo único que trabaja el plan. |
| **El Consejo** | `autonomo/consejo/` | Reunión por escrito de los «ministerios» para atajar dudas de un plan sin pararte a ti cada vez. |
| **El contador de gasto** | `autonomo/gasto.mjs` | Cuenta los tokens de cada tarea y agente. |
| **Los partes** | `autonomo/partes/` | Uno por sesión: qué se hizo, qué falló, qué te deja para revisar. |
| **Las sesiones** | `autonomo/SESIONES.md` | Cada sesión cerrada, con su resultado y lo que te toca. |
| **Las webs de radiología** | `autonomo/ideas/` | Lo que se sacó de Radiology Assistant y NavRad, y qué páginas sirven para este estudio. |

## Cómo se usa

1. `/bitacora apunta: …` → lo convierte en tarea con número (`B-001`…) y dudas.
2. `/bitacora aprueba B-00N` → pasa al tablero.
3. `/plan-socialista` (la siguiente pendiente) o `/plan-socialista <clave>` → el equipo la hace y deja una PR en
   borrador y un parte.
4. `/bitacora` sin nada → el rumbo: qué está en marcha, qué espera tu visto bueno y qué espera algo tuyo.

## Lo que nunca va a pasar

- **Ningún dato de paciente se sube a GitHub** (el repositorio es público). Los datos reales se trabajan solo en
  los ordenadores del hospital; aquí solo hay datos simulados para probar los scripts.
- Nadie cambia el protocolo, el programa (LIFEx o 3D Slicer) ni la configuración de extracción sin que lo decidas tú.
- Nada de modelos predictivos, curvas ROC ni aprendizaje automático: el estudio es descriptivo (§11.4).

## Qué esperar

- Va más lento que una conversación normal: cada cosa la hacen y la revisan varios.
- Cuando no puede, no lo inventa: marca la tarea como «necesita humano» y te dice qué falta (un PDF, una decisión
  tuya, un dato que solo está en el hospital).
