// This file was generated with the assistance of an AI coding tool.
const status = document.getElementById('status');
const checksEl = document.getElementById('checks');
const commandsEl = document.getElementById('commands');

const DIST_FILES = [
  '/ifcopenshell-js/dist/index.js',
  '/ifcopenshell-js/dist/geom/index.js',
  '/ifcopenshell-js/dist/util/index.js',
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
  for (const path of DIST_FILES) {
    allOk = renderCheck(await checkUrl(`JS dist: ${fileLabel(path)}`, path)) && allOk;
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
    status.textContent = 'Some checks failed — run the commands below, then reload.';
  }

  commandsEl.textContent = [
    '# From the IfcOpenShell repository root',
    '# Build this package. WASM is loaded from the jsDelivr CDN.',
    'cd src/ts/ifcopenshell-js',
    'npm run build',
    '',
    '# Serve src/ts',
    'cd ..',
    'python -m http.server 4173',
    '# open http://127.0.0.1:4173/ifcopenshell-js/examples/00-installation/',
  ].join('\n');
}

main().catch((err) => {
  status.textContent = String(err);
  console.error(err);
});
