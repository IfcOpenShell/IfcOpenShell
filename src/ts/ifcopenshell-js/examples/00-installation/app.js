// This file was generated with the assistance of an AI coding tool.
const status = document.getElementById('status');
const checksEl = document.getElementById('checks');
const commandsEl = document.getElementById('commands');

const JS_CDN = 'https://cdn.jsdelivr.net/npm/ifcopenshell@latest/dist';
const JS_FILES = [
  `${JS_CDN}/index.js`,
  `${JS_CDN}/geom/index.js`,
  `${JS_CDN}/util/index.js`,
];

const WASM_CDN = 'https://cdn.jsdelivr.net/npm/@ifcopenshell/wasm@latest';
const WASM_FILES = [
  `${WASM_CDN}/browser.js`,
  `${WASM_CDN}/wasm/ifcopenshell_wasm.wasm`,
  `${WASM_CDN}/wasm/ifcopenshell_api.mjs`,
];

function fileLabel(path) {
  const parts = path.split('/');
  return parts.slice(-2).join('/');
}

async function checkUrl(label, url) {
  try {
    const response = await fetch(url, { method: 'HEAD' });
    return { label, ok: response.ok, detail: response.ok ? 'found' : `HTTP ${response.status}` };
  } catch (err) {
    return { label, ok: false, detail: String(err) };
  }
}

function renderCheck(result) {
  const li = document.createElement('li');
  li.className = result.ok ? 'ok' : 'fail';
  li.textContent = `${result.ok ? 'OK' : 'FAIL'} ${result.label} — ${result.detail}`;
  checksEl.appendChild(li);
  return result.ok;
}

async function main() {
  let allOk = true;
  for (const path of JS_FILES) {
    allOk = renderCheck(await checkUrl(`JS CDN: ${fileLabel(path)}`, path)) && allOk;
  }
  for (const path of WASM_FILES) {
    allOk = renderCheck(await checkUrl(`WASM CDN: ${fileLabel(path)}`, path)) && allOk;
  }

  if (allOk) {
    status.textContent = 'Files are in place — initializing the runtime…';
    try {
      const ifcopenshell = await import('ifcopenshell');
      const runtime = await ifcopenshell.init();
      await runtime.loadPlugin('schema', 'ifc4');
      renderCheck({
        label: 'init() and schema:ifc4',
        ok: true,
        detail: runtime.loadedPlugins().join(', '),
      });
      status.textContent = 'All checks passed — try Chapter 1 (parse).';
    } catch (err) {
      renderCheck({ label: 'Runtime init()', ok: false, detail: String(err) });
      status.textContent = 'Runtime init failed — see checks below.';
    }
  } else {
    status.textContent = 'Some checks failed — the CDN packages could not be reached. Reload to try again.';
  }

  commandsEl.textContent = [
    '# Serve the chapter pages. ifcopenshell and WASM load from jsDelivr.',
    'cd src/ts',
    'python -m http.server 4173',
    '# open http://127.0.0.1:4173/ifcopenshell-js/examples/00-installation/',
  ].join('\n');
}

main().catch((err) => {
  status.textContent = String(err);
  console.error(err);
});
