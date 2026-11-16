
import initModule from './wasm/ifcopenshell_wasm.mjs';
import { createIfcOpenshellModule } from './wasm/ifcopenshell_api.mjs';

export { createIfcOpenshellModule, initModule };
export { resolveUrls } from './urls.js';
export const wasmUrl = new URL('./wasm/ifcopenshell_wasm.wasm', import.meta.url).href;
export const pluginBaseUrl = import.meta.url;
export const pluginLoader = undefined;
