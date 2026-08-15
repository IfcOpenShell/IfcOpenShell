
import {
  createIfcOpenshellModule,
  initModule,
  manifest,
  pluginBaseUrl,
  wasmUrl,
} from './asset-manifest.js';

function nodeOnly(name) {
  throw new Error(`${name} is only available in Node. Browser apps should serve the wasm/ directory and call resolveUrls(baseUrl).`);
}

export function getWasmRoot() {
  nodeOnly('getWasmRoot()');
}

export function wasmArtifactsPresent() {
  return false;
}

export function isFullProfile(manifest) {
  return manifest?.kernel?.opencascade !== undefined;
}

export function loadManifest() {
  nodeOnly('loadManifest()');
}

export async function resolveWasmAssets() {
  return {
    initModule,
    wasmUrl,
    pluginBaseUrl,
    manifest,
    createIfcOpenshellModule,
  };
}

export async function resolveUrls(baseUrl) {
  const normalizedBase = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`;
  const manifestResponse = await fetch(new URL('ifcopenshell_plugins.json', normalizedBase));
  if (!manifestResponse.ok) {
    throw new Error(`Failed to load WASM plugin manifest: ${manifestResponse.status}`);
  }
  const manifest = await manifestResponse.json();
  const initModuleUrl = new URL('ifcopenshell_wasm.mjs', normalizedBase).href;
  const apiModuleUrl = new URL('ifcopenshell_api.mjs', normalizedBase).href;
  const [wasmModule, apiModule] = await Promise.all([
    import(/* @vite-ignore */ /* webpackIgnore: true */ initModuleUrl),
    import(/* @vite-ignore */ /* webpackIgnore: true */ apiModuleUrl),
  ]);

  return {
    initModule: wasmModule.default,
    wasmUrl: new URL('ifcopenshell_wasm.wasm', normalizedBase).href,
    pluginBaseUrl: normalizedBase,
    manifest,
    apiModuleUrl,
    createIfcOpenshellModule: apiModule.createIfcOpenshellModule,
  };
}
