
export interface PluginEntry {
  wasm: string;
  depends?: string[];
}

export interface PluginManifest {
  schema?: Record<string, PluginEntry>;
  kernel?: Record<string, PluginEntry>;
  mapping?: Record<string, PluginEntry>;
  document?: Record<string, PluginEntry>;
  geometry_serializer?: Record<string, PluginEntry>;
  tree?: Record<string, PluginEntry>;
}

export type EmscriptenModuleFactory = (options?: Record<string, unknown>) => Promise<unknown>;

export type PluginLoader = (
  url: string,
  plugin: { kind: string; id: string; entry: PluginEntry },
) => Promise<Uint8Array | ArrayBuffer | ArrayBufferView> | Uint8Array | ArrayBuffer | ArrayBufferView;

export type IfcOpenshellApiFactory = (
  initModule: EmscriptenModuleFactory,
  wasmUrl?: string,
  opts?: {
    pluginBaseUrl?: string;
    pluginManifest?: Record<string, Record<string, PluginEntry>>;
    pluginLoader?: PluginLoader;
  },
) => Promise<unknown>;

export interface ResolvedWasmAssets {
  initModule: EmscriptenModuleFactory;
  wasmUrl: string;
  pluginBaseUrl: string;
  manifest: PluginManifest;
  apiModuleUrl?: string;
  createIfcOpenshellModule?: IfcOpenshellApiFactory;
  pluginLoader?: PluginLoader;
}

export type NodePluginLoader = (url: string) => Promise<Uint8Array>;

export function getWasmRoot(): string;
export function wasmArtifactsPresent(root?: string): boolean;
export function isFullProfile(manifest: PluginManifest): boolean;
export function loadManifest(root?: string): PluginManifest;
export function createNodePluginLoader(): NodePluginLoader;
export function resolveWasmAssets(root?: string): Promise<ResolvedWasmAssets>;
export function resolveUrls(baseUrl: string): Promise<ResolvedWasmAssets>;
