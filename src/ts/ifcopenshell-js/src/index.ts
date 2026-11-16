/**
 * Core `ifcopenshell` API.
 *
 * @module Core
 */

import { init as initialize } from './init.js';
import type { InitOptions, WasmAssets } from './types.js';

export * from './core.js';

/**
 * Initialize the packaged or explicitly configured WASM runtime.
 *
 * Plugins are loaded lazily through {@link IfcOpenShell.loadPlugin}.
 * File and Iterator support explicit disposal; other handles use GC cleanup.
 *
 * @param options Asset locations and optional plugin-loader overrides.
 * @returns An initialized, frozen runtime facade.
 */
export function init(options: InitOptions = {}) {
  return initialize(options, async () => {
    const wasm = await import('@ifcopenshell/wasm');
    return await wasm.resolveWasmAssets() as WasmAssets;
  });
}
