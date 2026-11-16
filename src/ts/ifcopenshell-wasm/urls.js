// This file was generated with the assistance of an AI coding tool.

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
