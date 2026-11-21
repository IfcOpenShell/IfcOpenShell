
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

export { resolveUrls } from './urls.js';
