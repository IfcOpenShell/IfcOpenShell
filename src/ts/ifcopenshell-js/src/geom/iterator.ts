
import type {
  IfcOpenshellFile,
  IfcOpenshellGeomElement,
  IfcOpenshellGeomIterator,
  IfcOpenshellGeomTaxonomyPoint3,
  IfcOpenshellGeomTriangulation,
  IfcOpenshellGeomTriangulationElement,
} from '@ifcopenshell-js/wasm/api';
import type { IfcFile } from '../file.js';
import { IfcOpenShellError, abortError, type IfcOpenShell } from '../init.js';
import { HandleGuard } from '../resource.js';
import { GeomSettings } from './settings.js';
import type { Mesh, MeshPrecision } from './mesh.js';

/** Include or exclude geometry by IFC type, GlobalId, or numeric id. */
export type IteratorFilter =
  | { kind: 'types'; values: string[]; include?: boolean }
  | { kind: 'guids'; values: string[]; include?: boolean }
  | { kind: 'ids'; values: number[]; include?: boolean };

/** Progress payload emitted while geometry is loaded or iterated. */
export interface OperationProgress {
  /** Current phase, such as `plugin`, `iterate`, `write`, or `done`. */
  phase: string;
  /** Human-readable progress message. */
  message: string;
  /** Normalized progress ratio when available. */
  ratio?: number;
  /** Number of processed items when available. */
  current?: number;
}

/** Current native geometry iterator state and unit information. */
export interface IteratorMetadata {
  /** Whether native geometry initialization has completed. */
  initialized: boolean;
  /** Normalized native processing progress in the range `0..1`. */
  progress: number;
  /** Whether native element processing reported an error. */
  hadError: boolean;
  /** Name of the file's length unit. */
  unitName: string;
  /** Magnitude of the file's length unit in SI units. */
  unitMagnitude: number;
}

/** Options controlling geometry kernel, parallelism, and entity filtering. */
export interface IteratorOptions<P extends MeshPrecision = 'float32'> {
  kernel?: string;
  numThreads?: number;
  filter?: IteratorFilter;
  /**
   * Precision of detached floating geometry snapshots. Defaults to `float32`
   * for WebGL-friendly buffers; use `float64` for CPU-side analytical work.
   */
  precision?: P;
}

/** Options for collecting meshes from an asynchronous iterator. */
export interface CollectOptions {
  limit?: number;
  progressInterval?: number;
  skipEmpty?: boolean;
  /** Checked between synchronous native calls; it cannot interrupt one native call already in progress. */
  signal?: AbortSignal;
  onProgress?(progress: OperationProgress & { meshes: number }): void;
}

/** Meshes and completion metadata returned by {@link GeomIterator.collect}. */
export interface CollectResult<P extends MeshPrecision = 'float32'> {
  meshes: Mesh<P>[];
  truncated: boolean;
  metadata: IteratorMetadata;
}

/** Asynchronous geometry mesh iterator backed by a loaded IFC file. */
export class GeomIterator<P extends MeshPrecision = 'float32'> implements AsyncIterable<Mesh<P>> {
  private rawIter: IfcOpenshellGeomIterator | null = null;
  private guard: HandleGuard<IfcOpenshellGeomIterator> | null = null;
  private initialized = false;
  private initializationAttempted = false;
  private cleanlyEmpty = false;
  private exhausted = false;
  private disposed = false;
  private readonly ready: Promise<IfcOpenshellGeomIterator>;
  private readonly ownedSettings: GeomSettings | null;
  private settingsReleased = false;
  private readonly precision: P;

  constructor(
    shell: IfcOpenShell,
    file: IfcFile,
    settings: GeomSettings,
    options: IteratorOptions<P> = {},
    private readonly ownsSettings = false,
  ) {
    validateTriangulatedOutput(settings);
    this.precision = (options.precision ?? 'float32') as P;
    this.ownedSettings = ownsSettings ? settings : null;
    this.ready = createIterator(shell, file.raw, settings, options).then((raw) => {
      if (this.disposed) {
        raw.destroy();
        this.releaseSettings();
        return raw;
      }
      this.rawIter = raw;
      this.guard = new HandleGuard(this, raw, true);
      return raw;
    }, (error: unknown) => {
      this.releaseSettings();
      throw error;
    });
  }

  get raw(): IfcOpenshellGeomIterator {
    if (this.disposed || this.rawIter == null) throw new IfcOpenShellError('GeomIterator has been disposed');
    return this.rawIter;
  }

  /** Return progress, initialization, error, and unit metadata. */
  async metadata(): Promise<IteratorMetadata> {
    const raw = await this.ready;
    if (this.disposed) throw new IfcOpenShellError('GeomIterator has been disposed');
    return {
      initialized: this.initialized,
      progress: normalizeProgress(raw.progress()),
      hadError: raw.hadErrorProcessingElements(),
      unitName: raw.unitName(),
      unitMagnitude: raw.unitMagnitude(),
    };
  }

  /** Initialize the native iterator and report whether initialization succeeded. */
  async initialize(): Promise<boolean> {
    if (this.disposed) throw new IfcOpenShellError('GeomIterator has been disposed');
    if (this.initializationAttempted) return this.initialized;
    const raw = await this.ready;
    const ok = raw.initialize();
    this.initializationAttempted = true;
    this.initialized = ok;
    this.cleanlyEmpty = !ok && !raw.hadErrorProcessingElements();
    return ok;
  }

  /** Compute geometry bounds, optionally forcing full geometry creation. */
  async computeBounds(withGeometry = true): Promise<void> {
    if (this.disposed) throw new IfcOpenShellError('GeomIterator has been disposed');
    if (!await this.initialize()) {
      const raw = await this.ready;
      if (!raw.hadErrorProcessingElements()) return;
      throw new IfcOpenShellError(
        'Failed to initialize GeomIterator before computing bounds; verify the IFC has supported geometry and the selected kernel is available',
      );
    }
    (await this.ready).computeBounds(withGeometry);
  }

  /** Return the computed minimum and maximum points. */
  async bounds(): Promise<{ min: [number, number, number] | null; max: [number, number, number] | null }> {
    const raw = await this.ready;
    if (this.disposed) throw new IfcOpenShellError('GeomIterator has been disposed');
    if (this.cleanlyEmpty) return { min: null, max: null };
    return { min: readPoint3(raw.boundsMin()), max: readPoint3(raw.boundsMax()) };
  }

  async boundsMin(): Promise<[number, number, number] | null> {
    return (await this.bounds()).min;
  }

  async boundsMax(): Promise<[number, number, number] | null> {
    return (await this.bounds()).max;
  }

  /** Advance to the next mesh, returning `null` after exhaustion. */
  async nextMesh(): Promise<Mesh<P> | null> {
    return this.nextWithOptions();
  }

  next(): Promise<Mesh<P> | null> {
    return this.nextMesh();
  }

  /** Consume meshes until exhaustion, a limit, or cancellation. */
  async collect(options: CollectOptions = {}): Promise<CollectResult<P>> {
    const meshes: Mesh<P>[] = [];
    const limit = options.limit ?? Number.POSITIVE_INFINITY;
    const progressInterval = Math.max(1, options.progressInterval ?? 24);
    let seen = 0;

    while (meshes.length < limit) {
      throwIfAborted(options.signal);
      const mesh = await this.nextWithOptions(options);
      if (!mesh) break;
      seen++;
      if (!options.skipEmpty || (mesh.vertices.length > 0 && mesh.faces.length > 0)) meshes.push(mesh);
      if (seen % progressInterval === 0) {
        const metadata = await this.metadata();
        options.onProgress?.({
          phase: 'iterate',
          message: 'Iterating geometry',
          ratio: metadata.progress,
          current: seen,
          meshes: meshes.length,
        });
      }
    }

    const metadata = await this.metadata();
    const truncated = meshes.length >= limit && !this.exhausted;
    options.onProgress?.({
      phase: 'done',
      message: 'Geometry iteration complete',
      ratio: truncated ? metadata.progress : 1,
      current: seen,
      meshes: meshes.length,
    });
    return { meshes, truncated, metadata };
  }

  async *[Symbol.asyncIterator](): AsyncIterableIterator<Mesh<P>> {
    while (true) {
      const mesh = await this.nextMesh();
      if (!mesh) return;
      yield mesh;
    }
  }

  /** Stop iteration and release the native iterator and owned settings. */
  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    if (this.rawIter == null) return;
    this.guard?.destroy();
    this.guard = null;
    this.rawIter = null;
    this.releaseSettings();
  }

  [Symbol.dispose](): void {
    this.dispose();
  }

  async [Symbol.asyncDispose](): Promise<void> {
    await this.ready.catch(() => undefined);
    this.dispose();
  }

  private releaseSettings(): void {
    if (!this.ownsSettings || this.settingsReleased) return;
    this.settingsReleased = true;
    this.ownedSettings?.dispose();
  }

  private async nextWithOptions(options: { signal?: AbortSignal } = {}): Promise<Mesh<P> | null> {
    throwIfAborted(options.signal);
    if (this.disposed) throw new IfcOpenShellError('GeomIterator has been disposed');
    if (this.exhausted) return null;
    const raw = await this.ready;
    if (!await this.initialize()) {
      this.exhausted = true;
      if (!raw.hadErrorProcessingElements()) return null;
      throw new IfcOpenShellError(
        'Failed to initialize GeomIterator; verify the IFC has supported geometry and the selected kernel is available',
      );
    }
    const mesh = extractMesh(raw, this.precision);
    this.exhausted = !raw.next();
    return mesh;
  }
}

async function createIterator(
  shell: IfcOpenShell,
  file: IfcOpenshellFile,
  settings: GeomSettings,
  options: IteratorOptions<MeshPrecision>,
): Promise<IfcOpenshellGeomIterator> {
  const kernel = options.kernel ?? 'passthrough';
  await loadGeometry(shell, file, kernel);
  const raw = createFilteredIterator(shell, kernel, settings, file, options.numThreads ?? 1, options.filter);
  if (!raw || raw.ptr === 0) throw new IfcOpenShellError('Failed to create GeomIterator');
  return raw;
}

function createFilteredIterator(
  shell: IfcOpenShell,
  kernel: string,
  settings: GeomSettings,
  file: IfcOpenshellFile,
  threads: number,
  filter?: IteratorFilter,
): IfcOpenshellGeomIterator | null {
  const include = filter?.include ?? true;
  if (filter?.kind === 'types') {
    return shell.raw.geom.createIteratorWithIncludeExclude(kernel, settings.raw, file, filter.values, include, threads);
  }
  if (filter?.kind === 'guids') {
    return shell.raw.geom.createIteratorWithIncludeExcludeGlobalid(kernel, settings.raw, file, filter.values, include, threads);
  }
  if (filter?.kind === 'ids') {
    return shell.raw.geom.createIteratorWithIncludeExcludeId(kernel, settings.raw, file, filter.values, include, threads);
  }
  return shell.raw.geom.createIterator(kernel, settings.raw, file, threads);
}

export async function loadGeometry(shell: IfcOpenShell, file: IfcOpenshellFile, kernel: string): Promise<void> {
  const schema = schemaPluginId(file.schemaName());
  await shell.loadPlugin('kernel', kernel);
  await shell.loadPlugin('mapping', schema);
}

export function schemaPluginId(schemaName: string): string {
  const normalized = schemaName.toLowerCase().replace(/[^a-z0-9]/g, '_');
  if (normalized.includes('ifc2x3')) return 'ifc2x3';
  if (normalized.includes('ifc4x3')) return 'ifc4x3_add2';
  if (normalized.includes('ifc4')) return 'ifc4';
  throw new IfcOpenShellError(
    `Unsupported geometry mapping schema "${schemaName}"; supported mappings are IFC2X3, IFC4, and IFC4X3`,
  );
}

function extractMesh<P extends MeshPrecision>(iter: IfcOpenshellGeomIterator, precision: P): Mesh<P> | null {
  let tri: IfcOpenshellGeomTriangulationElement | null = null;
  let geom: IfcOpenshellGeomTriangulation | null = null;
  let element: IfcOpenshellGeomElement | null = null;
  try {
    tri = iter.getAsTriangulationElement();
    if (!tri || tri.ptr === 0) return null;
    geom = tri.geometry();
    if (!geom || geom.ptr === 0) return null;
    element = iter.get();
    if (!element || element.ptr === 0) return null;
    const vertices = precision === 'float64' ? geom.vertsBuffer(Float64Array) : geom.vertsBuffer(Float32Array);
    const normals = precision === 'float64' ? geom.normalsBuffer(Float64Array) : geom.normalsBuffer(Float32Array);
    const uvs = precision === 'float64' ? geom.uvsBuffer(Float64Array) : geom.uvsBuffer(Float32Array);
    const colors = precision === 'float64' ? geom.colorsBuffer(Float64Array) : geom.colorsBuffer(Float32Array);
    return {
      id: element.id(),
      guid: element.guid(),
      type: element.type(),
      name: element.name(),
      vertices,
      faces: geom.facesBuffer(Uint32Array),
      normals: normals.length > 0 ? normals : null,
      transform: element.transformationBuffer(Float64Array),
      edges: geom.edgesBuffer(Uint32Array),
      materialIds: geom.materialIdsBuffer(Int32Array),
      itemIds: geom.itemIdsBuffer(Int32Array),
      edgeItemIds: geom.edgesItemIdsBuffer(Int32Array),
      uvs,
      colors,
    } as Mesh<P>;
  } finally {
    release(element);
    release(geom);
    release(tri);
  }
}

function readPoint3(point: IfcOpenshellGeomTaxonomyPoint3 | null): [number, number, number] | null {
  if (!point || point.ptr === 0) return null;
  try {
    const data = point.getData();
    return data && data.length >= 3 ? [data[0]!, data[1]!, data[2]!] : null;
  } finally {
    point.destroy();
  }
}

function release(handle: { destroy(): void } | null | undefined): void {
  handle?.destroy();
}

function validateTriangulatedOutput(settings: GeomSettings): void {
  if (settings.getInt('iterator-output') !== 0) {
    throw new IfcOpenShellError(
      'IfcFile.meshes() requires triangulated geometry; set "iterator-output" to 0 (TRIANGULATED)',
    );
  }
}

function throwIfAborted(signal: AbortSignal | undefined): void {
  if (signal?.aborted) throw abortError('IfcOpenShell operation was cancelled', signal.reason);
}

function normalizeProgress(progress: number): number {
  if (!Number.isFinite(progress)) return 0;
  if (progress > 1) return Math.max(0, Math.min(1, progress / 100));
  return Math.max(0, Math.min(1, progress));
}
