#!/usr/bin/env node
// Gasto de tokens del plan socialista, por tarea y por agente.
// Lee las transcripciones de la sesión que guarda Claude Code (~/.claude/projects/<proyecto>/):
// la del director (<sesion>.jsonl) y la de cada agente (<sesion>/subagents/agent-*.jsonl + .meta.json).
//
// La tarea de cada agente sale de su descripción: el director la empieza por «[clave]»
// (p. ej. «[b3] Constructor 3A»). El gasto del propio director se reparte por tiempo: lo que gastó
// entre el primer agente y el último de una tarea cuenta para esa tarea (aproximado).
//
// Uso:
//   node autonomo/gasto.mjs                    la sesión más reciente, todas las tareas
//   node autonomo/gasto.mjs --clave b3         solo una tarea
//   node autonomo/gasto.mjs --desde 2026-10-23 solo lo gastado desde esa fecha (ISO)
//   node autonomo/gasto.mjs --sesion <ruta.jsonl>
//   node autonomo/gasto.mjs --json             salida en JSON
//
// «Equivalente» suma los cuatro tipos de token con su peso en el precio de la API, en tokens de entrada:
// entrada nueva ×1, escritura en la caché ×1,25, lectura de la caché ×0,1, salida ×5. No mezcla modelos:
// un token del modelo potente cuesta más que uno del barato, por eso cada fila dice su modelo.

import { readdirSync, readFileSync, statSync, existsSync } from 'node:fs';
import { join, basename } from 'node:path';
import { homedir } from 'node:os';

const PESO = { entrada: 1, cacheEscrita: 1.25, cacheLeida: 0.1, salida: 5 };

const args = process.argv.slice(2);
const opcion = nombre => { const i = args.indexOf(nombre); return i >= 0 ? args[i + 1] : undefined; };
const comoJson = args.includes('--json');
const soloClave = opcion('--clave');
const desde = opcion('--desde') ? Date.parse(opcion('--desde')) : -Infinity;

function sesionMasReciente() {
    const carpeta = join(homedir(), '.claude', 'projects', process.cwd().replace(/[^A-Za-z0-9]/g, '-'));
    if (!existsSync(carpeta)) return null;
    const jsonl = readdirSync(carpeta).filter(f => f.endsWith('.jsonl')).map(f => join(carpeta, f));
    jsonl.sort((a, b) => statSync(b).mtimeMs - statSync(a).mtimeMs);
    return jsonl[0] ?? null;
}

// Cada mensaje del modelo aparece varias veces (una por bloque) y no todas las copias traen la salida final:
// de cada id vale la copia con más salida. Aun así, a veces solo queda la cifra inicial: la salida puede
// quedarse corta (en la práctica pesa poco frente a la caché leída).
function leerUso(ruta) {
    const porId = new Map();
    let herramientas = 0;
    for (const linea of readFileSync(ruta, 'utf8').split('\n')) {
        if (!linea.includes('"usage"')) continue;
        let o;
        try { o = JSON.parse(linea); } catch { continue; }
        const m = o.message;
        // «<synthetic>» son los avisos de error (límite de uso), no respuestas del modelo.
        if (o.type !== 'assistant' || !m?.usage || m.model === '<synthetic>') continue;
        const t = Date.parse(o.timestamp);
        if (t < desde) continue;
        herramientas += (m.content ?? []).filter(b => b.type === 'tool_use').length;
        const previo = porId.get(m.id);
        if (!previo || (m.usage.output_tokens ?? 0) >= (previo.u.output_tokens ?? 0)) {
            porId.set(m.id, { t, modelo: m.model, u: m.usage });
        }
    }
    return { mensajes: [...porId.values()], herramientas };
}

function sumar(mensajes) {
    const s = { entrada: 0, cacheEscrita: 0, cacheLeida: 0, salida: 0 };
    for (const { u } of mensajes) {
        s.entrada += u.input_tokens ?? 0;
        s.cacheEscrita += u.cache_creation_input_tokens ?? 0;
        s.cacheLeida += u.cache_read_input_tokens ?? 0;
        s.salida += u.output_tokens ?? 0;
    }
    s.equivalente = Math.round(Object.keys(PESO).reduce((a, k) => a + s[k] * PESO[k], 0));
    return s;
}

const claveDe = descripcion => descripcion?.match(/^\s*\[([^\]]+)\]/)?.[1] ?? '(sin clave)';
const modeloCorto = m => (m ?? '?').replace(/^claude-/, '').replace(/-\d{8}$/, '');

const sesion = opcion('--sesion') ?? sesionMasReciente();
if (!sesion || !existsSync(sesion)) {
    console.error('No encuentro la transcripción de la sesión. Pásala con --sesion <ruta.jsonl>.');
    process.exit(1);
}
const carpetaAgentes = join(sesion.replace(/\.jsonl$/, ''), 'subagents');

const agentes = [];
if (existsSync(carpetaAgentes)) {
    for (const f of readdirSync(carpetaAgentes).filter(f => /^agent-.*\.jsonl$/.test(f))) {
        const ruta = join(carpetaAgentes, f);
        const rutaMeta = ruta.replace(/\.jsonl$/, '.meta.json');
        const meta = existsSync(rutaMeta) ? JSON.parse(readFileSync(rutaMeta, 'utf8')) : {};
        const { mensajes, herramientas } = leerUso(ruta);
        if (!mensajes.length) continue;
        const tiempos = mensajes.map(m => m.t);
        agentes.push({
            id: basename(f, '.jsonl'),
            clave: claveDe(meta.description),
            papel: meta.agentType ?? '?',
            descripcion: meta.description ?? '',
            modelo: modeloCorto(mensajes.at(-1).modelo),
            inicio: Math.min(...tiempos),
            fin: Math.max(...tiempos),
            herramientas,
            ...sumar(mensajes),
        });
    }
}

// El director: su gasto entre el primer y el último agente de cada tarea va a esa tarea.
const director = leerUso(sesion).mensajes;
const ventanas = new Map();
for (const a of agentes) {
    if (a.clave === '(sin clave)') continue;
    const v = ventanas.get(a.clave) ?? { inicio: Infinity, fin: -Infinity };
    ventanas.set(a.clave, { inicio: Math.min(v.inicio, a.inicio), fin: Math.max(v.fin, a.fin) });
}
const directorPorClave = new Map();
for (const m of director) {
    let clave = '(fuera de tareas)';
    for (const [k, v] of ventanas) if (m.t >= v.inicio && m.t <= v.fin) { clave = k; break; }
    if (!directorPorClave.has(clave)) directorPorClave.set(clave, []);
    directorPorClave.get(clave).push(m);
}
for (const [clave, mensajes] of directorPorClave) {
    agentes.push({
        id: 'director', clave, papel: 'director (aprox.)', descripcion: 'la sesión que dirige',
        modelo: modeloCorto(mensajes.at(-1).modelo), herramientas: null, ...sumar(mensajes),
    });
}

const filas = agentes.filter(a => !soloClave || a.clave === soloClave);
if (comoJson) {
    console.log(JSON.stringify({ sesion, pesos: PESO, filas }, null, 2));
    process.exit(0);
}

const miles = n => n >= 1e6 ? `${(n / 1e6).toFixed(1)} M` : n >= 1e3 ? `${Math.round(n / 1e3)} k` : String(n);
const porClave = new Map();
for (const f of filas) {
    if (!porClave.has(f.clave)) porClave.set(f.clave, []);
    porClave.get(f.clave).push(f);
}
const total = lista => lista.reduce((a, f) => a + f.equivalente, 0);
const claves = [...porClave.entries()].sort((a, b) => total(b[1]) - total(a[1]));

console.log(`# Gasto de tokens · ${basename(sesion)}\n`);
console.log('Equivalente = entrada ×1 + caché escrita ×1,25 + caché leída ×0,1 + salida ×5 (en tokens de entrada).\n');
for (const [clave, lista] of claves) {
    console.log(`## ${clave} · ${miles(total(lista))} equivalentes\n`);
    console.log('| Agente | Papel | Modelo | Herram. | Entrada | Caché escrita | Caché leída | Salida | Equivalente |');
    console.log('|---|---|---|---|---|---|---|---|---|');
    for (const f of lista.sort((a, b) => b.equivalente - a.equivalente)) {
        console.log(`| ${f.descripcion.replace(/\|/g, '/')} | ${f.papel} | ${f.modelo} | ${f.herramientas ?? '—'} | ` +
            `${miles(f.entrada)} | ${miles(f.cacheEscrita)} | ${miles(f.cacheLeida)} | ${miles(f.salida)} | ` +
            `**${miles(f.equivalente)}** |`);
    }
    console.log();
}

// Resumen por papel: dónde se va el gasto.
const porPapel = new Map();
for (const f of filas) {
    const k = `${f.papel} · ${f.modelo}`;
    const v = porPapel.get(k) ?? { n: 0, eq: 0 };
    porPapel.set(k, { n: v.n + 1, eq: v.eq + f.equivalente });
}
const todo = total(filas);
console.log('## Por papel\n');
console.log('| Papel · modelo | Lanzados | Equivalente | % | Media por agente |');
console.log('|---|---|---|---|---|');
for (const [k, v] of [...porPapel.entries()].sort((a, b) => b[1].eq - a[1].eq)) {
    console.log(`| ${k} | ${v.n} | ${miles(v.eq)} | ${Math.round(100 * v.eq / todo)} % | ${miles(Math.round(v.eq / v.n))} |`);
}
