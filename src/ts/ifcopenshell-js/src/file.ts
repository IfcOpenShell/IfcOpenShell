
import type { IfcOpenshellFile } from '@ifcopenshell-js/wasm/api';
import { Entity } from './entity.js';
import { GeomIterator, type IteratorOptions } from './geom/iterator.js';
import type { MeshPrecision } from './geom/mesh.js';
import { GeomSettings } from './geom/settings.js';
import { IfcOpenShellError, abortError, type IfcOpenShell } from './init.js';
import { HandleGuard } from './resource.js';
import { inspectEntity, type EntityInfo } from './util/inspect.js';

/** Options controlling IFC byte-stream loading. */
export interface OpenOptions {
  /** Abort opening before native parsing begins. */
  signal?: AbortSignal;
  /** Open the native file in read-only mode when supported. */
  readonly?: boolean;
}

/** Header values exposed from an IFC file's STEP header. */
export interface HeaderInfo {
  description: string[];
  implementationLevel: string;
  name: string;
  timeStamp: string;
  author: string[];
  organization: string[];
  preprocessorVersion: string;
  originatingSystem: string;
  authorization: string;
  schemas: string[];
}

/** Summary information for an opened IFC file. */
export interface FileInfo {
  schema: string;
  ids: number[];
  types: string[];
  entityCount: number;
  maxId: number;
  good: number;
  storageMode: number;
  header: HeaderInfo | null;
}

/** High-level wrapper for an IFC file and its entity graph. */
export class IfcFile {
  private _raw: IfcOpenshellFile | null;
  private readonly guard: HandleGuard<IfcOpenshellFile>;

  private constructor(
    private readonly _shell: IfcOpenShell,
    raw: IfcOpenshellFile,
    owned = true,
  ) {
    this._raw = raw;
    this.guard = new HandleGuard(this, raw, owned);
  }

  /** Open IFC STEP bytes and retain ownership of the native file. */
  static async open(
    shell: IfcOpenShell,
    bytes: Uint8Array | ArrayBuffer,
    filename?: string,
    options: OpenOptions = {},
  ): Promise<IfcFile> {
    if (options.signal?.aborted) {
      throw abortError('Opening IFC file was aborted', options.signal.reason);
    }
    const raw = shell.raw.parse.openBytes(bytes, filename, options.readonly ?? false);
    if (options.signal?.aborted) {
      raw?.destroy();
      throw abortError('Opening IFC file was aborted', options.signal.reason);
    }
    if (!raw || raw.ptr === 0) throw new IfcOpenShellError('Failed to open IFC file');
    return new IfcFile(shell, raw);
  }

  /** Create a new empty IFC file for the requested schema. */
  static async createEmpty(shell: IfcOpenShell, schema: string): Promise<IfcFile> {
    return IfcFile.create(shell, schema);
  }

  /** Create a new IFC file for the requested schema. */
  static async create(shell: IfcOpenShell, schema: string): Promise<IfcFile> {
    const raw = shell.raw.parse.newFile(schema, 0, '');
    if (!raw || raw.ptr === 0) throw new IfcOpenShellError(`Failed to create ${schema} file`);
    return new IfcFile(shell, raw);
  }

  static wrap(shell: IfcOpenShell, raw: IfcOpenshellFile | null, owned = false): IfcFile | null {
    return raw && raw.ptr !== 0 ? new IfcFile(shell, raw, owned) : null;
  }

  get shell(): IfcOpenShell {
    return this._shell;
  }

  get raw(): IfcOpenshellFile {
    if (this._raw == null) throw new IfcOpenShellError('IfcFile has been disposed');
    return this._raw;
  }

  get schemaName(): string {
    return this.raw.schemaName();
  }

  get schema(): string {
    return this.schemaName;
  }

  get maxId(): number {
    return this.raw.getMaxId();
  }

  get ids(): number[] {
    return this.raw.entityNames();
  }

  get types(): string[] {
    return this.raw.types();
  }

  get entityCount(): number {
    return this.ids.length;
  }

  get isValid(): boolean {
    return this.raw.good() !== 0;
  }

  /** Return an entity by numeric STEP id, or `null` when it is absent. */
  get(id: number): Entity | null {
    return Entity.wrap(this._shell, catchNull(() => this.raw.byId(id)));
  }

  /** Return an entity by GlobalId, or `null` when it is absent. */
  find(guid: string): Entity | null {
    return Entity.wrap(this._shell, catchNull(() => this.raw.byGuid(guid)));
  }

  /** Return all entities of a type, optionally excluding its subtypes. */
  all(typeName: string, options: { includeSubtypes?: boolean } = {}): Entity[] {
    const list = options.includeSubtypes === false
      ? this.raw.byTypeExclSubtypes(typeName)
      : this.raw.byType(typeName);
    try {
      const out: Entity[] = [];
      for (let i = 0; i < list.size(); i++) {
        const item = Entity.wrap(this._shell, list.get(i));
        if (item) out.push(item);
      }
      return out;
    } finally {
      list.destroy();
    }
  }

  /** Create an entity through the low-level file API. */
  create(ifcClass: string, options: { predefinedType?: string | null; name?: string | null } = {}): Entity {
    const entity = Entity.wrap(this._shell, this.raw.createEntityByName(ifcClass));
    if (!entity) throw new IfcOpenShellError(`Failed to create ${ifcClass}`);
    if (options.name != null) entity.set('Name', options.name);
    if (options.predefinedType != null) entity.set('PredefinedType', options.predefinedType);
    return entity;
  }

  text(): string {
    return this.raw.toString();
  }

  /** Return schema, entity-id, validity, storage, and header summary data. */
  info(): FileInfo {
    const ids = this.ids;
    return {
      schema: this.schemaName,
      ids,
      types: this.types,
      entityCount: ids.length,
      maxId: this.raw.getMaxId(),
      good: this.raw.good(),
      storageMode: this.raw.storageMode(),
      header: this.header(),
    };
  }

  /** Read the STEP header, returning `null` when no header is available. */
  header(): HeaderInfo | null {
    const header = this.raw.header();
    if (!header || header.ptr === 0) return null;
    try {
      const description = header.fileDescription();
      const name = header.fileName();
      const schema = header.fileSchema();
      try {
        return {
          description: description.description(),
          implementationLevel: description.implementationLevel(),
          name: name.name(),
          timeStamp: name.timeStamp(),
          author: name.author(),
          organization: name.organization(),
          preprocessorVersion: name.preprocessorVersion(),
          originatingSystem: name.originatingSystem(),
          authorization: name.authorization(),
          schemas: schema.schemaIdentifiers(),
        };
      } finally {
        schema.destroy();
        name.destroy();
        description.destroy();
      }
    } finally {
      header.destroy();
    }
  }

  status(): number {
    return this.raw.good();
  }

  storageMode(): number {
    return this.raw.storageMode();
  }

  unit(unitType: string): number {
    return this.raw.getUnit(unitType);
  }

  totalInverses(entity: Entity): number {
    return this.raw.getTotalInverses(entity.raw);
  }

  inverses(entity: Entity): Entity[] {
    const list = this.raw.getInverse(entity.raw);
    try {
      const out: Entity[] = [];
      for (let i = 0; i < list.size(); i++) {
        const item = Entity.wrap(this._shell, list.get(i));
        if (item) out.push(item);
      }
      return out;
    } finally {
      list.destroy();
    }
  }

  inverseIndices(entity: Entity): number[] {
    return this.raw.getInverseIndices(entity.raw);
  }

  traverse(entity: Entity, options: { maxDepth?: number; breadthFirst?: boolean } = {}): Entity[] {
    const maxDepth = options.maxDepth ?? -1;
    const list = options.breadthFirst
      ? this.raw.traverseBreadthFirst(entity.raw, maxDepth)
      : this.raw.traverse(entity.raw, maxDepth);
    try {
      const out: Entity[] = [];
      for (let i = 0; i < list.size(); i++) {
        const item = Entity.wrap(this._shell, list.get(i));
        if (item) out.push(item);
      }
      return out;
    } finally {
      list.destroy();
    }
  }

  /** Create an asynchronous geometry iterator for this file. */
  meshes(settings: GeomSettings | undefined, options: IteratorOptions<'float64'> & { precision: 'float64' }): GeomIterator<'float64'>;
  meshes<P extends MeshPrecision>(settings: GeomSettings | undefined, options: IteratorOptions<P>): GeomIterator<P>;
  meshes(settings?: GeomSettings, options?: IteratorOptions<'float32'>): GeomIterator<'float32'>;
  meshes<P extends MeshPrecision = 'float32'>(settings?: GeomSettings, options?: IteratorOptions<P>): GeomIterator<P> {
    const ownedSettings = settings === undefined;
    return new GeomIterator<P>(this._shell, this, settings ?? new GeomSettings(this._shell), options, ownedSettings);
  }

  async bounds(settings?: GeomSettings, options?: IteratorOptions): Promise<{
    min: [number, number, number] | null;
    max: [number, number, number] | null;
  }> {
    await using iterator = this.meshes(settings, options);
    await iterator.computeBounds(true);
    return iterator.bounds();
  }

  /** Return a plain-object inspection snapshot for an entity id. */
  inspect(id: number): Promise<EntityInfo | null> {
    return inspectEntity(this, id);
  }

  /** Release the native file handle. Safe to call more than once. */
  dispose(): void {
    if (this._raw == null) return;
    this.guard.destroy();
    this._raw = null;
  }

  [Symbol.dispose](): void {
    this.dispose();
  }

  async [Symbol.asyncDispose](): Promise<void> {
    this.dispose();
  }
}

function catchNull<T>(fn: () => T): T | null {
  try {
    const value = fn();
    return value && typeof value === 'object' && 'ptr' in value && value.ptr === 0 ? null : value;
  } catch {
    return null;
  }
}
