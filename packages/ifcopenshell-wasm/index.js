
import { existsSync, readFileSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const WASM_ROOT = join(__dirname, 'wasm');

const REQUIRED_FILES = [
  'ifcopenshell_wasm.mjs',
  'ifcopenshell_wasm.node.mjs',
  'ifcopenshell_wasm.wasm',
  'ifcopenshell_api.mjs',
  'ifcopenshell_plugins.json',
];

/** Absolute path to the packaged WASM asset directory. */
export function getWasmRoot() {
  return WASM_ROOT;
}

/** Return whether all required WASM artifacts are present in the package. */
export function wasmArtifactsPresent(root = WASM_ROOT) {
  return REQUIRED_FILES.every((name) => existsSync(join(root, name)));
}

/** Read and parse `ifcopenshell_plugins.json` from the packaged assets. */
export function loadManifest(root = WASM_ROOT) {
  const manifestPath = join(root, 'ifcopenshell_plugins.json');
  if (!existsSync(manifestPath)) {
    throw new Error(`WASM plugin manifest not found at ${manifestPath}. The published @ifcopenshell-js/wasm package should include it; in a source checkout, run "npm run stage" in packages/ifcopenshell-wasm after building WASM.`);
  }
  return JSON.parse(readFileSync(manifestPath, 'utf8'));
}

/**
 * Filesystem-backed plugin loader for Node.
 *
 * @param {string} url
 * @returns {Promise<Uint8Array>}
 */
export function createNodePluginLoader() {
  return (url) => readFile(fileURLToPath(url));
}

/**
 * Build a {@link WasmAssets}-compatible descriptor for Node consumers.
 *
 * @param {string} [root]
 * @returns {Promise<import('./index.d.ts').ResolvedWasmAssets>}
 */
export async function resolveWasmAssets(root = WASM_ROOT) {
  if (!wasmArtifactsPresent(root)) {
    throw new Error(
      `IfcOpenShell WASM artifacts are missing under ${root}. ` +
        'The published @ifcopenshell-js/wasm package should include them; in a source checkout, run "npm run stage" in packages/ifcopenshell-wasm after building WASM.',
    );
  }

  const manifest = loadManifest(root);
  const wasmModulePath = join(root, 'ifcopenshell_wasm.node.mjs');
  const wasmModuleUrl = pathToFileURL(wasmModulePath).href;
  const moduleFactory = (await import(wasmModuleUrl)).default;
  const wasmPath = join(root, 'ifcopenshell_wasm.wasm');
  let wasmBinary;
  const initModule = async (options = {}) => {
    wasmBinary ??= readFile(wasmPath);
    return moduleFactory({
      ...options,
      wasmBinary: await wasmBinary,
    });
  };
  const apiModuleUrl = pathToFileURL(join(root, 'ifcopenshell_api.mjs')).href;
  const apiModule = await import(apiModuleUrl);

  return {
    initModule,
    wasmUrl: wasmPath,
    pluginBaseUrl: (() => {
      const base = pathToFileURL(root).href;
      return base.endsWith('/') ? base : `${base}/`;
    })(),
    manifest,
    apiModuleUrl,
    createIfcOpenshellModule: apiModule.createIfcOpenshellModule,
    pluginLoader: createNodePluginLoader(),
  };
}

/**
 * Return browser-friendly URLs for WASM assets served from `baseUrl`.
 *
 * @param {string} baseUrl Base URL ending with `/` that serves the wasm directory.
 * @returns {Promise<import('./index.d.ts').BrowserWasmUrls>}
 */
export async function resolveUrls(baseUrl) {
  const normalizedBase = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`;
  const manifestResponse = await fetch(new URL('ifcopenshell_plugins.json', normalizedBase));
  if (!manifestResponse.ok) {
    throw new Error(`Failed to load WASM plugin manifest: ${manifestResponse.status}`);
  }
  const manifest = await manifestResponse.json();
  const initModuleUrl = new URL('ifcopenshell_wasm.mjs', normalizedBase).href;
  const initModule = (await import(/* @vite-ignore */ /* webpackIgnore: true */ initModuleUrl)).default;

  return {
    initModule,
    wasmUrl: new URL('ifcopenshell_wasm.wasm', normalizedBase).href,
    pluginBaseUrl: normalizedBase,
    manifest,
    apiModuleUrl: new URL('ifcopenshell_api.mjs', normalizedBase).href,
  };
}
