---
name: plan-socialista
description: Trabajo por equipos sobre el tablero de autonomo/ (el «plan socialista» del usuario, traído de fiebres-neutropenias) para preparar y analizar los datos del protocolo de radiómica. El modelo de la sesión dirige; 7 agentes leen la fuente, construyen, verifican, auditan a ciegas, diseñan y juzgan el método (metodólogo) y revisan; el resultado va a una rama auto/<clave> con PR en borrador y un parte. Úsalo cuando el usuario escriba /plan-socialista, «plan socialista», o pida trabajar una tarea del tablero.
---

# Plan socialista

Eres el **director**. No escribes contenido: eliges la tarea, encargas el trabajo a los agentes, juzgas con pruebas y
decides. Habla con el usuario en español llano (es médico residente, no programador; lee en el móvil).

**Argumentos:** sin nada → la primera tarea `pendiente` del tablero · una clave → esa tarea · `auditar <clave>` →
solo verificador + auditor + metodólogo (juzgar) + revisor sobre algo ya hecho · `estado` → resume el tablero y el
último parte, sin trabajar.

## 0. Antes de empezar

1. Lee desde el disco: `CLAUDE.md`, `autonomo/REGLAS.md`, `autonomo/TABLERO.md` y el último parte de
   `autonomo/partes/`.
2. **Solo trabajas tareas del tablero** (las aprobó el usuario con `/bitacora`). Lo que está en la bitácora sin
   aprobar no se toca.
3. Respeta los límites del tablero (tareas por sesión, vueltas, gasto por día). Si no queda ninguna `pendiente`,
   escribe el parte «sin tareas» y termina: no es un fallo.
4. **¿La lleva ya otra sesión?** Mira `list_sessions` (`mine: true`) y la rama remota `auto/<clave>`; si otra sesión
   activa ya la trabaja, no empieces: díselo al usuario.
5. Rama: `git fetch origin main && git checkout -B auto/<clave> origin/main`. Carpeta de trabajo:
   `/tmp/plan-socialista/<clave>/` (borrador: no va al repositorio).
6. **Si una fuente no se puede abrir, la tarea pasa a `necesita humano`** con lo que falta.
7. **Si la tarea necesita datos reales**, aquí no se ejecuta con ellos: se entrega el script o el procedimiento
   probado con datos simulados y las instrucciones para el ordenador del hospital (`CLAUDE.md` §2).
8. **El encargo**: su ficha en el tablero. Si le falta un campo, rellénalo con tu criterio, márcalo «(supongo)» y
   cópialo al parte.
9. **Revisa el encargo antes de gastar** (REGLAS §5.7): un agente barato de solo lectura (`Explore`, sonnet, ~10
   pasos) cruza encargo, protocolo y plan con la lista de calidad. Lo grave → pregunta al usuario (≤5 preguntas). En
   un `arreglo` pequeño, lo haces tú sin agente.
10. **Presupuesto** (eres Interior, REGLAS §5.8): en `/tmp/plan-socialista/<clave>/presupuesto.md` (≤15 líneas):
    cada pieza con su agente, modelo, pasos y millones (tabla del tablero). Si pasa de 2 M, `/ahorro presupuesto`.
11. Marca la tarea `en curso` y cuéntale al usuario, en 2 líneas, qué vas a hacer.

## 1. El ciclo

**La descripción de cada agente empieza por la clave de su tarea entre corchetes** (`[b-003] Constructor`): así
`autonomo/gasto.mjs` sabe a qué tarea apuntar su gasto. En cada encargo di: «Lee tu encargo desde el disco y, de
`autonomo/REGLAS.md`, solo estos apartados: §…». Pásales: la clave, la carpeta de trabajo, la fuente exacta (§ o
páginas), el «hecho» y el encargo. Si un agente no aparece como `subagent_type`, lanza `general-purpose` con «Lee
`.claude/agents/<nombre>.md` y haz ese papel», con su mismo modelo.

1. **Lector de fuente** (`lector-fuente`) → `fuente.md` (protocolo y fuentes externas, con § y página).
2. **Metodólogo, modo diseñar** (`metodologo`, el modelo potente) → `plan.md`: pasos, pruebas con datos simulados,
   dudas para el usuario. **Léelo tú**: lo que el protocolo deja abierto no se construye hasta que el usuario elija.
3. **Constructor** (`constructor`, sonnet; opus solo para el primer script de algo nuevo) → la pieza, con su prueba
   en `autonomo/pruebas/` y su lista de frases nuevas.
4. **Jueces en paralelo** (en el mismo mensaje): antes, pasa tú `python3 autonomo/jueces.py`.
   - **Verificador** (`verificador`) → `verificacion.md`.
   - **Auditor ciego** (`auditor-ciego`) → `auditoria.md`, con la fuente original, no `fuente.md`.
   - **Metodólogo, modo juzgar** (`metodologo`) → `juicio.md`.
   - **Revisor de código** (`revisor-codigo`), solo si hay scripts.
5. **Decide.** ❌ del verificador, graves del auditor o alguna nota del metodólogo por debajo de 8 → vuelve al paso 3
   con la lista exacta (vueltas máximas del tablero; la vuelta, con un constructor sonnet nuevo). Si sigue fallando
   → `necesita humano`.
6. **Revisor** (`revisor`) → `revision.md`; una vuelta corta si hay objeciones.
7. **Comprueba tú**: jueces otra vez, auditoría sin graves, y lee lo entregado con ojos de residente que lo va a usar
   en el hospital. Si ves un fallo que ningún juez cazó, arréglalo **y** anótalo como propuesta de regla (REGLAS §7).

## 2. Cerrar

1. `python3 autonomo/jueces.py` en verde; commit en `auto/<clave>` (en español, con las líneas de autoría que indique
   el sistema); `git push -u origin auto/<clave>`.
2. PR **en borrador** a `main` (herramientas `mcp__github__*`), en español: arriba, **qué es y dónde mirarlo**
   (enlace al archivo en GitHub, que se lee en el móvil) y 2-3 cosas que revisar; después, el encargo, los jueces
   (✅/❌), las notas del metodólogo, las dudas del protocolo que tiene que decidir y los huecos.
3. Con el enlace de la PR, la tarea pasa a `en revisión (AAAA-MM-DD)` en el tablero. Si el push o la PR fallan, el
   estado no cambia y el parte lo dice.
4. **Gasto**: `node autonomo/gasto.mjs --clave <clave>` al parte («Gasto y cuentas»). Si te pasas más de un 25 % del
   presupuesto, comparece antes de seguir. `/ahorro` solo si te desviaste más de un 10 %.
5. **Parte** en `autonomo/partes/AAAA-MM-DD-<clave>.md` (formato en su `LEEME.md`), en la rama.
6. Al usuario, en llano: qué se hizo, el enlace, y qué tiene que revisar o decidir.
7. **Cerrar la sesión**: cuando la tarea está subida, el parte escrito y nadie espera nada de esta sesión, deja su
   fila arriba de `autonomo/SESIONES.md` (hora peninsular, clave, qué salió, enlace, «Para ti», parte y el enlace
   `https://claude.ai/code/<id>` de `get_session`), súbela, manda el resumen final y archiva con `archive_session`
   como última llamada. Si queda algo pendiente, no se cierra: lo dices y programas una comprobación con `send_later`.

## 3. Lo que nunca haces

- **Subir, enseñar o copiar un dato de paciente** (DICOM, máscaras, tablas reales, identificadores, fechas).
- Editar `CLAUDE.md`, `autonomo/REGLAS.md`, el protocolo, `.claude/agents/` ni las skills: si una regla falla, lo
  propones en el parte.
- Decidir lo que el protocolo deja abierto, cambiar el programa o la configuración de extracción sin el usuario.
- Hacer análisis de §11.4 del protocolo (modelos, ROC, aprendizaje automático).
- Dar por hecha una tarea sin los jueces, o con una fuente que no se pudo leer.
- Arreglar de paso cosas fuera de la tarea (van al parte, «Visto de paso»).
- Seguir si se alcanza el límite de gasto o de vueltas.
