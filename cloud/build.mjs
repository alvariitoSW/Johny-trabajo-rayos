// Genera dist/bitacora.html: una sola página para publicar en claude.ai
// (artifact con base de datos). Uso: npm run build:cloud
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';

const read = (p) => readFileSync(new URL(`../${p}`, import.meta.url), 'utf8');

const html = read('public/index.html');
const body = html.slice(html.indexOf('<body>') + '<body>'.length, html.indexOf('</body>')).trim();
const css = read('public/styles.css');
const core = read('public/core.js').replace(/^export /gm, '');
const script = [core, read('cloud/cloud-api.js'), read('public/app.js')].join('\n');

if (script.includes('</script')) throw new Error('El código contiene </script>');

const page = `<title>Bitácora</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
${css}
</style>
${body}
<script type="module">
${script}
</script>
`;

mkdirSync(new URL('../dist/', import.meta.url), { recursive: true });
writeFileSync(new URL('../dist/bitacora.html', import.meta.url), page);
console.log(`dist/bitacora.html (${(page.length / 1024).toFixed(1)} KB)`);
