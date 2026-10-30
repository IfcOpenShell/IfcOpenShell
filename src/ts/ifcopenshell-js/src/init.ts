import { adoptInstance } from './entity_instance.js';
import {
  IfcOpenShellError,
  IfcOpenShellErrorCode,
  IfcOpenShellErrorKind,
  abortError,
  isIfcOpenShellAbortError,
} from '@ifcopenshell/wasm/api';
import type {
  EmscriptenFS,
  EmscriptenOptions,
  IfcOpenshellApiFactory,
  IfcOpenshellModule,
  InitOptions,
  PluginKind,
  WasmAssets,
} from './types.js';

/** Initialized IfcOpenShell runtime and its ergonomic low-level API. */
export interface IfcOpenShell {
  readonly raw: IfcOpenshellModule;
  readonly fs: EmscriptenFS | null;
  loadPlugin(kind: PluginKind, id: string): Promise<void>;
  loadedPlugins(): string[];
}

export {
  IfcOpenShellError,
  IfcOpenShellErrorCode,
  IfcOpenShellErrorKind,
  abortError,
  isIfcOpenShellAbortError,
};

/**
 * Initialize the packaged or explicitly configured WASM runtime.
 *
 * Plugins are loaded lazily through {@link IfcOpenShell.loadPlugin}.
 * File and Iterator support explicit disposal; other handles use GC cleanup.
 *
 * @param options Asset locations and optional plugin-loader overrides.
 * @returns An initialized, frozen runtime facade.
 */
export function init(options: InitOptions = {}): Promise<IfcOpenShell> {
  if (initialization) {
    if (Object.keys(options).length) {
      return Promise.reject(new IfcOpenShellError('Runtime is already initializing or initialized; configure it only on the first init() call'));
    }
    return initialization;
  }
  initialization = initialize(options).then(value => {
    ifcopenshell = value.raw;
    fs = value.fs;
    return value;
  }).catch(error => {
    initialization = undefined;
    throw error;
  });
  return initialization;
}

/** Native module, available after awaiting init(). */
export let ifcopenshell: IfcOpenshellModule;
/** Retrieve the loaded schema declaration by its full identifier. */
export function schemaByName(name: string) {
  // Accept general names such as `file.schema()` returns, as Python schema_by_name does.
  const schema = ifcopenshell.parse.schemaByName(name.toUpperCase() === 'IFC4X3' ? 'IFC4X3_ADD2' : name);
  indexDeclarations(schema);
  return downcasting(schema);
}

// Native schema objects are reflected on dynamically (method names vary by declaration kind).
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Native = Record<string | symbol, any>;

/**
 * Entity hierarchy by name. Entities returned by the native `supertype()` and `subtypes()` lack the
 * base declaration's methods such as `name()`, so named declarations are returned instead,
 * with the hierarchy derived from `isA()` on named declarations.
 */
interface Hierarchy {
  byName: Map<string, Native>;
  supertype: Map<string, string | null>;
  subtypes: Map<string, string[]>;
}
const schemas = new Map<string, Native>();
const hierarchies = new Map<string, Hierarchy>();

/** @internal */
export function indexDeclarations(schema: Native | null): void {
  if (schema && !schemas.has(schema.name())) schemas.set(schema.name(), schema);
}

function hierarchy(schemaName: string): Hierarchy | undefined {
  const schema = schemas.get(schemaName);
  if (!schema) return undefined;
  let result = hierarchies.get(schemaName);
  if (result) return result;
  const entities: Native[] = (schema.declarations() as Native[]).filter(d => d.asEntity());
  const byName = new Map(entities.map(d => [d.name() as string, d]));
  const depth = new Map<string, number>();
  for (const [name, declaration] of byName) {
    let level = 0;
    for (let entity = declaration.asEntity().supertype(); entity; entity = entity.supertype()) level++;
    depth.set(name, level);
  }
  const supertype = new Map<string, string | null>();
  const subtypes = new Map<string, string[]>([...byName.keys()].map(name => [name, []]));
  for (const [name, declaration] of byName) {
    const level = depth.get(name)!;
    const parent = level ? [...byName.keys()].find(other => depth.get(other) === level - 1 && declaration.isA(other)) ?? null : null;
    supertype.set(name, parent);
    if (parent) subtypes.get(parent)!.push(name);
  }
  result = { byName, supertype, subtypes };
  hierarchies.set(schemaName, result);
  return result;
}

const DOWNCASTS = ['asEntity', 'asTypeDeclaration', 'asSelectType', 'asEnumerationType', 'asAggregationType', 'asNamedType', 'asSimpleType'];

/**
 * Schema objects as Python returns them: declarations and parameter types are downcast to their
 * most specific class, so `declarationByName('IfcWall').isAbstract()` works without `asEntity()`.
 */
/** Names of simple types, in the order of the native data_type enumeration. */
const SIMPLE_TYPES = ['binary', 'boolean', 'integer', 'logical', 'number', 'real', 'string'];

/**
 * The text Python gives `str()` of a schema object, such as `<type IfcLabel: <string>>`;
 * some Python utilities parse it. Aggregate bounds are not exposed natively, so they are `?`.
 */
function schemaString(kind: string, specific: Native, base: Native): string {
  const text = (value: unknown) => String(downcasting(value));
  switch (kind) {
    case 'asEntity': return `<entity ${base.name()}>`;
    case 'asTypeDeclaration': return `<type ${base.name()}: ${text(specific.declaredType())}>`;
    case 'asSelectType': return `<select ${base.name()}: (${(specific.selectList() as unknown[]).map(text).join(' | ')})>`;
    case 'asEnumerationType': return `<enumeration ${base.name()}: (${(specific.enumerationItems() as string[]).join(', ')})>`;
    case 'asAggregationType': return `<${specific.typeOfAggregationString()} [?:?] of ${text(specific.typeOfElement())}>`;
    case 'asNamedType': return text(specific.declaredType());
    case 'asSimpleType': return `<${SIMPLE_TYPES[specific.declaredType() as number]}>`;
    default: return Object.prototype.toString.call(specific);
  }
}

/** @internal */
export function downcasting<T>(value: T): T {
  if (Array.isArray(value)) return value.map(downcasting) as T;
  if (value === null || typeof value !== 'object') return value;
  const base = value as Record<string | symbol, unknown>;
  let specific = base;
  let kind: string | undefined;
  for (const method of DOWNCASTS) {
    if (typeof base[method] === 'function') {
      const result = (base[method] as () => Record<string | symbol, unknown> | null).call(base);
      if (result) {
        specific = result;
        kind = method;
        break;
      }
    }
  }
  // Named entity declarations navigate the hierarchy by name; see hierarchy().
  const named = typeof base.name === 'function' && typeof base.schema === 'function' && specific !== base
    ? hierarchy((base as Native).schema().name()) : undefined;
  const name = named ? (base as Native).name() as string : undefined;
  // The WASM classes do not inherit from each other, so fall back to the base object's members.
  return new Proxy(specific, {
    get(object, key) {
      if (key === 'toString' && kind) return () => schemaString(kind!, specific as Native, base as Native);
      if (key === 'declarationByName') {
        // Python raises for unknown names, and callers rely on it.
        return (declarationName: string) => {
          const declaration = (base as Native).declarationByName(declarationName);
          if (!declaration) throw new IfcOpenShellError(`Declaration not found: ${declarationName}`);
          return downcasting(declaration);
        };
      }
      if (named && name && named.byName.has(name)) {
        if (key === 'supertype') {
          return () => {
            const parent = named.supertype.get(name);
            return parent ? downcasting(named.byName.get(parent)) : null;
          };
        }
        if (key === 'subtypes') return () => named.subtypes.get(name)!.map(child => downcasting(named.byName.get(child)));
      }
      const owner = key in object ? object : base;
      const member = Reflect.get(owner, key, owner);
      return typeof member === 'function' ? (...args: unknown[]) => downcasting(member.apply(owner, args)) : member;
    },
  }) as T;
}

/** Emscripten filesystem, available after awaiting init(). */
export let fs: EmscriptenFS | null;
let initialization: Promise<IfcOpenShell> | undefined;

async function initialize(options: InitOptions): Promise<IfcOpenShell> {
  let assets: WasmAssets;
  if (options.wasmAssets) {
    assets = options.wasmAssets;
  } else {
    try {
      assets = await resolveRuntime();
    } catch (error) {
      throw new IfcOpenShellError('Failed to resolve packaged WASM assets', error);
    }
  }
  const loader = options.pluginLoader ?? assets.pluginLoader;

  validateAssets(assets);

  let fs: EmscriptenFS | null = null;
  const initModule = (opts?: EmscriptenOptions) =>
    Promise.resolve(assets.initModule(opts)).then((mod) => {
      fs = readFs(mod);
      return mod;
    });

  const createModule = await resolveApiFactory(assets);
  let raw: IfcOpenshellModule;
  try {
    raw = await createModule(initModule, assets.wasmUrl, {
      pluginBaseUrl: assets.pluginBaseUrl,
      pluginManifest: assets.manifest as Record<string, Record<string, { wasm: string; depends?: string[] }>>,
      pluginLoader: loader,
    });
  } catch (error) {
    throw new IfcOpenShellError('Failed to instantiate IfcOpenShell WASM', error);
  }

  const runtime: IfcOpenShell = {
    raw,
    fs,
    loadPlugin: (kind, id) => loadPlugin(raw, kind, id),
    loadedPlugins: () => raw.loadedPlugins(),
  };
  raw.setInstanceFactory(adoptInstance);
  return Object.freeze(runtime);
}

async function resolveRuntime(): Promise<WasmAssets> {
  const wasm = await import('@ifcopenshell/wasm');
  return await wasm.resolveWasmAssets() as WasmAssets;
}

async function resolveApiFactory(assets: WasmAssets): Promise<IfcOpenshellApiFactory> {
  if (typeof assets.createIfcOpenshellModule === 'function') return assets.createIfcOpenshellModule;

  const specifier = assets.apiModuleUrl!;
  try {
    const mod = await import(/* @vite-ignore */ /* webpackIgnore: true */ specifier);
    if (typeof mod.createIfcOpenshellModule !== 'function') {
      throw new IfcOpenShellError(`${specifier} does not export createIfcOpenshellModule`);
    }
    return mod.createIfcOpenshellModule as IfcOpenshellApiFactory;
  } catch (error) {
    throw new IfcOpenShellError(
      `Failed to load IfcOpenShell API module from ${specifier}`,
      error,
    );
  }
}

function validateAssets(assets: WasmAssets | undefined): asserts assets is WasmAssets {
  if (typeof assets?.initModule !== 'function') {
    throw new IfcOpenShellError('wasmAssets.initModule must be the ifcopenshell_wasm.mjs module factory');
  }
  if (typeof assets.wasmUrl !== 'string' || assets.wasmUrl.length === 0) {
    throw new IfcOpenShellError('wasmAssets.wasmUrl must point to ifcopenshell_wasm.wasm');
  }
  if (typeof assets.pluginBaseUrl !== 'string' || assets.pluginBaseUrl.length === 0) {
    throw new IfcOpenShellError('wasmAssets.pluginBaseUrl must point to the plugin directory');
  }
  if (!assets.manifest || typeof assets.manifest !== 'object') {
    throw new IfcOpenShellError('wasmAssets.manifest must be a plugin manifest object');
  }
  if (
    typeof assets.createIfcOpenshellModule !== 'function' &&
    (typeof assets.apiModuleUrl !== 'string' || assets.apiModuleUrl.length === 0)
  ) {
    throw new IfcOpenShellError(
      'wasmAssets must provide createIfcOpenshellModule or apiModuleUrl',
    );
  }
}

function readFs(mod: unknown): EmscriptenFS | null {
  const fs = (mod as { FS?: unknown } | null)?.FS;
  if (
    fs &&
    typeof fs === 'object' &&
    typeof (fs as { writeFile?: unknown }).writeFile === 'function' &&
    typeof (fs as { readFile?: unknown }).readFile === 'function'
  ) {
    return fs as EmscriptenFS;
  }
  return null;
}

async function loadPlugin(raw: IfcOpenshellModule, kind: PluginKind, id: string): Promise<void> {
  try {
    await raw.loadPlugin(kind, id);
  } catch (error) {
    const key = `${kind}:${id}`;
    const suffix = error instanceof Error && error.message ? `: ${error.message}` : '';
    throw new IfcOpenShellError(`Failed to load plugin ${key}${suffix}`, error);
  }
}
