---
name: ingenieria-reversa
description: Ingeniería inversa de una web o programa ajeno de radiología o radiómica (Radiology Assistant, NavRad, LIFEx, 3D Slicer/SlicerRadiomics, PyRadiomics) para entender qué hace y cómo, y proponer qué traer al estudio, sin copiar su código, textos ni imágenes. Sale un informe-propuesta para el móvil y el usuario elige. Úsalo cuando el usuario escriba /ingenieria-reversa o pida estudiar cómo está hecha una web o un programa.
---

# Ingeniería inversa (Ministerio de Ciencia)

Estudias cómo está hecha una web o un programa ajeno y propones qué traer al estudio. **No construyes nada**: sale un
informe y una decisión del usuario. Método de fiebres-neutropenias (de leanrea y REA, MIT), ya usado con Radiology
Assistant y NavRad (`autonomo/ideas/ingenieria-inversa/`).

## 0. Antes de empezar

1. Lee `CLAUDE.md` (§2 datos, §3 protocolo, §5 fuentes) y mira si la web ya tiene informe en
   `autonomo/ideas/ingenieria-inversa/<web>.md`: **reutilízalo** y estudia solo lo que falte.
2. **Prueba antes que se abre la web y cada dominio que carga** (REGLAS de fiebres-neutropenias, 30/10/2026). Esta red
   bloquea, entre otros, TCIA, Zenodo, arXiv, readthedocs y lifexsoft.org: si no se abre, díselo al usuario con el
   dominio exacto antes de lanzar a nadie.
3. Carpeta: `/tmp/plan-socialista/rea-<clave>/` (nada de esto va al repositorio).

## 1. Presupuesto

2-4 llamadas por pregunta; como mucho 2 capturas por web (comprimidas); investigadores en sonnet; informe ≤120
líneas por web.

## 2. Qué averiguar siempre

1. **Qué enseña o qué hace** y a quién va dirigido.
2. **Cómo está hecho**: tecnología, de dónde salen los datos, qué guarda.
3. **De dónde salen sus cifras o fórmulas** (en radiómica: ¿cumple IBSI? ¿qué versión? ¿qué nombres usa?).
4. **Licencias** de cada pieza, copiadas tal cual y marcadas «sin verificar en origen» si no se abrió la fuente.
5. **Para el estudio**: qué paso del protocolo (§) mejora y qué haría falta.
6. Etiqueta cada afirmación: **visto**, **deducido** o **no visto**.

Su código se lee en memoria, nunca se guarda. Nada de sus textos, imágenes o datos al repositorio.

## 3. El informe-propuesta

Una página Artifact para el móvil: la tesis en una frase; cada web o programa (qué es, su truco, qué le falta); qué
traer, de lo barato a lo grande, con su esfuerzo y qué necesita (una fuente, una decisión del usuario, nada); lo que
no traería; lo que necesito de ti; y lo que no se pudo ver.

## 4. Cerrar

Copia el informe a `autonomo/ideas/ingenieria-inversa/<web>.md`; en la bitácora, lo que tiene que elegir el usuario;
parte en `autonomo/partes/`; commit y push. Al usuario: el enlace y lo que decide.

## Lo que nunca haces

Copiar su código, textos, imágenes o datos; usar un conjunto de datos «abierto» sin comprobar su licencia en origen y
sin la decisión del usuario; saltarte un bloqueo de red por otra vía; construir durante esta skill.
