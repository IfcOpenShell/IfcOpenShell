
import moduleFactory from './wasm/ifcopenshell_wasm.node.mjs';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
export { createIfcOpenshellModule } from './wasm/ifcopenshell_api.mjs';
export { resolveUrls } from './urls.js';
export const wasmUrl = new URL('./wasm/ifcopenshell_wasm.wasm', import.meta.url).href;
export const pluginBaseUrl = import.meta.url;
export const pluginLoader = (url) => readFile(fileURLToPath(url));
let wasmBinary;
export async function initModule(options = {}) {
  wasmBinary ??= readFile(new URL(wasmUrl));
  return moduleFactory({ ...options, wasmBinary: await wasmBinary });
}
