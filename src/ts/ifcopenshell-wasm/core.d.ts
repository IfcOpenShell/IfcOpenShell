// This file was generated with the assistance of an AI coding tool.

import type { CoreWasmAssets, PluginManifest } from './index.js';

export const initModule: CoreWasmAssets['initModule'];
export const createIfcOpenshellModule: CoreWasmAssets['createIfcOpenshellModule'];
export const wasmUrl: string;
export const pluginBaseUrl: string;
export const pluginLoader: CoreWasmAssets['pluginLoader'];
export function resolveUrls(baseUrl: string): Promise<CoreWasmAssets & {
  manifest: PluginManifest;
  apiModuleUrl: string;
}>;
