
import type { IfcOpenshellModule } from '@ifcopenshell-js/wasm/api';

export type { IfcOpenshellModule };

/** Raw pointer address in WASM linear memory. */
export type Ptr = number;

/**
 * Subset of the Emscripten MEMFS filesystem API exposed by the underlying
 * WASM runtime. Used by higher-level wrappers (for example the SVG/TTL
 * serializers) to read, write, and delete files inside the virtual
 * filesystem that the C++ layer writes to.
 */
export interface EmscriptenFS {
  /**
   * Write data to a virtual filesystem path.
   *
   * @param path - Destination path inside MEMFS.
   * @param data - String or byte view to write.
   * @param opts - Optional flags (e.g. `{ flags: 'w' }`).
   */
  writeFile(
    path: string,
    data: string | ArrayBufferView | ArrayBuffer,
    opts?: { flags?: string },
  ): void;
  /**
   * Read a virtual filesystem file.
   *
   * When `opts.encoding === 'utf8'` the file is decoded to a string;
   * otherwise a `Uint8Array` of the raw bytes is returned.
   */
  readFile(path: string, opts?: { encoding?: string; flags?: string }): string | Uint8Array;
  /** Delete a virtual filesystem entry. */
  unlink(path: string): void;
  /** Return whether a path exists in MEMFS. */
  analyzePath(path: string): { exists: boolean; object?: object };
}

/** Identifiers for the plugin kinds supported by the WASM loader. */
export type PluginKind = 'schema' | 'kernel' | 'mapping' | 'tree' | 'document' | 'geometry_serializer';

/** A single entry in the plugin manifest, describing a loadable side module. */
export interface PluginEntry {
  /** Relative path to the `.wasm` side module (resolved against `pluginBaseUrl`). */
  wasm: string;
  /** Plugin keys this entry depends on, e.g. `["kernel:occt"]`. */
  depends?: string[];
}

/** The full plugin manifest (content of `ifcopenshell_plugins.json`). */
export interface PluginManifest {
  schema?: Record<string, PluginEntry>;
  kernel?: Record<string, PluginEntry>;
  mapping?: Record<string, PluginEntry>;
  document?: Record<string, PluginEntry>;
  geometry_serializer?: Record<string, PluginEntry>;
  tree?: Record<string, PluginEntry>;
}

/** Recursive value accepted by an Emscripten module factory. */
export type EmscriptenOption =
  | null
  | boolean
  | number
  | string
  | EmscriptenOption[]
  | { [key: string]: EmscriptenOption }
  | ((path: string, prefix: string) => string);

/** Emscripten module factory option map. */
export type EmscriptenOptions = Record<string, EmscriptenOption>;

/** Emscripten module factory — the default export of `ifcopenshell_wasm.mjs`. */
export type EmscriptenModuleFactory = (options?: EmscriptenOptions) => Promise<object>;

/** Generated API factory exported by `ifcopenshell_api.mjs`. */
export type IfcOpenshellApiFactory = (
  initModule: EmscriptenModuleFactory,
  wasmUrl?: string,
  opts?: {
    pluginBaseUrl?: string;
    pluginManifest?: Record<string, Record<string, { wasm: string; depends?: string[] }>>;
    pluginLoader?: PluginLoader;
  },
) => Promise<IfcOpenshellModule>;

/**
 * Custom plugin loader function.
 *
 * Override this to change how plugin `.wasm` bytes are fetched.
 * The default loader uses `fetch()` in the browser and is filesystem-backed in Node.
 */
export type PluginLoader = (
  url: string,
  plugin: { kind: string; id: string; entry: PluginEntry },
) => Promise<Uint8Array | ArrayBuffer | ArrayBufferView> | Uint8Array | ArrayBuffer | ArrayBufferView;

/** Configuration for locating the WASM build artifacts. */
export interface WasmAssets {
  /** The Emscripten module factory (default export of `ifcopenshell_wasm.mjs`). */
  initModule: EmscriptenModuleFactory;
  /** URL or path to `ifcopenshell_wasm.wasm`. */
  wasmUrl: string;
  /** Base URL for resolving plugin `.wasm` paths from the manifest. */
  pluginBaseUrl: string;
  /** Parsed content of `ifcopenshell_plugins.json`. */
  manifest: PluginManifest;
  /** Environment-appropriate loader for plugin WASM files. */
  pluginLoader?: PluginLoader;
  /**
   * URL or module specifier for the generated `ifcopenshell_api.mjs`.
   * Required when `createIfcOpenshellModule` is not provided.
   */
  apiModuleUrl?: string;
  /**
   * Generated API factory. Bundler-friendly wasm packages should provide this
   * so app bundles do not need runtime string imports for `ifcopenshell_api.mjs`.
   */
  createIfcOpenshellModule?: IfcOpenshellApiFactory;
}

/** Options for {@link init}. */
export interface InitOptions {
  /** WASM asset configuration. */
  wasmAssets?: WasmAssets;
  /** Custom plugin loader override. Defaults to the loader supplied by the asset descriptor. */
  pluginLoader?: PluginLoader;
}
