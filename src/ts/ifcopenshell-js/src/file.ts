
import { IfcOpenshellFile } from '@ifcopenshell/wasm/api';
import type { AttributeValueType, EntityInstance } from './entity_instance.js';
import { forgetFile, forgetInstance } from './entity_instance.js';
import { IfcOpenShellError, abortError, ifcopenshell } from './init.js';

/** Options controlling IFC byte-stream loading. */
export interface OpenOptions {
  /** Abort opening before native parsing begins. */
  signal?: AbortSignal;
  /** Open the native file in read-only mode when supported. */
  readonly?: boolean;
}

export interface GetInverseOptions {
  allowDuplicate?: boolean;
  withAttributeIndices?: boolean;
}

/** Open files by native pointer, so entities can return their File. */
const openFiles = new Map<number, WeakRef<File>>();

/** High-level wrapper for an IFC file and its entity graph. */
export class File extends IfcOpenshellFile {
  /** Unit cache keyed by unit type, as Python `file.units`; see `ifcopenshell/util/unit`. */
  units?: Record<string, EntityInstance>;

  /** Entities queued for removal by `ifcopenshell/util/element`, as Python `file.to_delete`. */
  to_delete: Set<EntityInstance> | null = null;

  /** @internal The File wrapping a native file pointer, if it is still open. */
  static fromPointer(pointer: number): File | null {
    return (pointer && openFiles.get(pointer)?.deref()) || null;
  }

  /** Create an empty file, or take ownership of an existing native file handle. */
  constructor(schemaOrHandle: string | IfcOpenshellFile = 'IFC4') {
    const handle = typeof schemaOrHandle === 'string'
      ? ifcopenshell.parse.newFile(schemaOrHandle, 0, '')
      : schemaOrHandle;
    if (!handle || handle.ptr === 0) throw new IfcOpenShellError('Failed to create IFC file');
    super(handle);
    openFiles.set(this.filePointer(), new WeakRef(this));
  }

  /**
   * The STEP header with Python's attribute names, as Python `file.header`: for example
   * `file.stepHeader.file_name.name = 'model.ifc'`. Reads and writes go to the native header.
   */
  get stepHeader(): StepHeader {
    const header = this.header();
    if (!header) throw new IfcOpenShellError('File has no header');
    const name = header.fileName();
    const description = header.fileDescription();
    return {
      file_name: {
        get name() { return name.name(); },
        set name(v) { name.setname(v); },
        get time_stamp() { return name.timeStamp(); },
        set time_stamp(v) { name.settimeStamp(v); },
        get author() { return name.author(); },
        set author(v) { name.setauthor([...v]); },
        get organization() { return name.organization(); },
        set organization(v) { name.setorganization([...v]); },
        get preprocessor_version() { return name.preprocessorVersion(); },
        set preprocessor_version(v) { name.setpreprocessorVersion(v); },
        get originating_system() { return name.originatingSystem(); },
        set originating_system(v) { name.setoriginatingSystem(v); },
        get authorization() { return name.authorization(); },
        set authorization(v) { name.setauthorization(v); },
      },
      file_description: {
        get description() { return description.description(); },
        set description(v) { description.setdescription([...v]); },
        get implementation_level() { return description.implementationLevel(); },
        set implementation_level(v) { description.setimplementationLevel(v); },
      },
    };
  }

  /** Copy the STEP header of another file, as Python `file.assign_header_from`. */
  assignHeaderFrom(other: File): void {
    const source = other.stepHeader;
    const target = this.stepHeader;
    for (const group of ['file_name', 'file_description'] as const) {
      for (const key of Object.keys(source[group])) {
        try {
          (target[group] as Record<string, unknown>)[key] = (source[group] as Record<string, unknown>)[key];
        } catch {
          // An invalid header value is skipped, as in Python.
        }
      }
    }
  }

  override dispose(): void {
    const pointer = this.filePointer();
    openFiles.delete(pointer);
    forgetFile(pointer);
    super.dispose();
  }

  override remove(entity: EntityInstance): void {
    forgetInstance(entity);
    super.remove(entity);
  }

  /** Parse IFC STEP text, as Python `ifcopenshell.file.from_string`. */
  static fromString(text: string, options: OpenOptions = {}): File {
    return File.open(new TextEncoder().encode(text), undefined, options);
  }

  /** Open IFC STEP bytes and retain ownership of the native file. */
  static open(
    bytes: Uint8Array | ArrayBuffer,
    filename?: string,
    options: OpenOptions = {},
  ): File {
    if (options.signal?.aborted) {
      throw abortError('Opening IFC file was aborted', options.signal.reason);
    }
    const handle = ifcopenshell.parse.openBytes(bytes, filename, options.readonly ?? false);
    if (options.signal?.aborted) {
      handle?.destroy();
      throw abortError('Opening IFC file was aborted', options.signal.reason);
    }
    if (!handle || handle.ptr === 0) throw new IfcOpenShellError('Failed to open IFC file');
    return new File(handle);
  }

  get maxId(): number {
    return this.getMaxId();
  }

  get ids(): number[] {
    // The C API yields entities in reverse insertion order; Python iterates by id.
    return this.entityNames().sort((a, b) => a - b);
  }

  get entityCount(): number {
    return this.ids.length;
  }

  /** Entities in id order, as iterating a Python `ifcopenshell.file`. */
  *[Symbol.iterator](): IterableIterator<EntityInstance> {
    for (const id of this.ids) yield this.byId(id) as EntityInstance;
  }

  declare byId: (id: number) => EntityInstance;
  declare byGuid: (guid: string) => EntityInstance;
  declare byType: (typeName: string) => EntityInstance[];
  declare byTypeExclSubtypes: (typeName: string) => EntityInstance[];
  declare traverse: (entity: EntityInstance, maxDepth: number) => EntityInstance[];
  declare traverseBreadthFirst: (entity: EntityInstance, maxDepth: number) => EntityInstance[];

  /**
   * Create an entity with any of its IFC attributes, by schema name, or by position when
   * given an array, as Python `file.create_entity(ifc_class, *args, **kwargs)`.
   */
  create(ifcClass: string, attributes: Record<string, AttributeValueType> | AttributeValueType[] = {}, id?: number | null): EntityInstance {
    const entity = (id ? this.createEntityByNameWithId(ifcClass, id) : this.createEntityByName(ifcClass)) as EntityInstance | null;
    if (!entity) throw new IfcOpenShellError(`Failed to create ${ifcClass}`);
    try {
      const entries = Array.isArray(attributes) ? attributes.map((value, index) => [index, value] as const) : Object.entries(attributes);
      for (const [name, value] of entries) entity.set(name, value);
      return entity;
    } catch (error) {
      this.remove(entity);
      throw error;
    }
  }

  /** Whether every entity referencing `entity` has one of `ids`, as Python `file._is_referenced_only_in`. */
  isReferencedOnlyIn(entity: EntityInstance, ids: Iterable<number>): boolean {
    const allowed = new Set(ids);
    return this.getInverseList(entity).every(inverse => allowed.has(inverse.id()));
  }

  /** The ids, of those given, referenced only by entities among them, as Python `file._ids_referenced_only_within`. */
  idsReferencedOnlyWithin(ids: Iterable<number>): number[] {
    const within = new Set(ids);
    return [...within].filter(id => this.getInverseList(this.byId(id)).every(inverse => within.has(inverse.id())));
  }

  /** General IFC schema version, without addendum or technical corrigendum suffixes. */
  schema(): string {
    return this.schemaIdentifier().replace(/(_ADD|_TC)\d+.*$/, '');
  }

  /** Add an entity, assigning a new id unless `instanceId` is given explicitly. */
  override add(entity: EntityInstance, instanceId = -1): EntityInstance {
    const added = super.add(entity, instanceId) as EntityInstance | null;
    if (!added) throw new IfcOpenShellError(`Failed to add ${entity.isA()} to file`);
    return added;
  }

  getInverse(entity: EntityInstance, options: { allowDuplicate?: false; withAttributeIndices?: false }): Set<EntityInstance>;
  getInverse(entity: EntityInstance, options: { allowDuplicate: true; withAttributeIndices: true }): [EntityInstance, number][];
  getInverse(entity: EntityInstance, options: { allowDuplicate: true; withAttributeIndices?: false }): EntityInstance[];
  getInverse(entity: EntityInstance): Set<EntityInstance>;
  getInverse(entity: EntityInstance, options: GetInverseOptions): Set<EntityInstance> | EntityInstance[] | [EntityInstance, number][];
  getInverse(entity: EntityInstance, options: GetInverseOptions = {}): Set<EntityInstance> | EntityInstance[] | [EntityInstance, number][] {
    const { allowDuplicate = false, withAttributeIndices = false } = options;
    if (withAttributeIndices && !allowDuplicate) {
      throw new IfcOpenShellError('withAttributeIndices requires allowDuplicate to be true');
    }
    const entities = this.getInverseList(entity) as EntityInstance[];
    if (withAttributeIndices) {
      const indices = this.getInverseIndices(entity);
      return entities.map((item, i) => [item, indices[i]!] as [EntityInstance, number]);
    }
    if (allowDuplicate) return entities;
    // JS Set uses object identity; native getters produce a fresh handle for each occurrence.
    const unique = new Map<number, EntityInstance>();
    for (const item of entities) {
      if (!unique.has(item.identity())) unique.set(item.identity(), item);
    }
    return new EntityInstanceSet(unique.values());
  }


}

/** Set membership follows IFC identity, like Python entity equality. */
class EntityInstanceSet extends Set<EntityInstance> {
  private readonly byIdentity = new Map<number, EntityInstance>();

  constructor(values: Iterable<EntityInstance>) {
    super();
    for (const value of values) this.add(value);
  }

  override add(value: EntityInstance): this {
    const identity = value.identity();
    if (!this.byIdentity.has(identity)) {
      this.byIdentity.set(identity, value);
      super.add(value);
    }
    return this;
  }

  override has(value: EntityInstance): boolean {
    return this.byIdentity.has(value.identity());
  }

  override delete(value: EntityInstance): boolean {
    const identity = value.identity();
    const member = this.byIdentity.get(identity);
    if (!member) return false;
    this.byIdentity.delete(identity);
    return super.delete(member);
  }

  override clear(): void {
    this.byIdentity.clear();
    super.clear();
  }
}

/** Parse IFC bytes after explicitly loading their schema plugin. */
export function open(bytes: Uint8Array | ArrayBuffer, filename?: string, options?: OpenOptions): File {
  return File.open(bytes, filename, options);
}

const resources = new Map<string, Uint8Array>();

/**
 * Provide the bytes of a file that generated code opens by path, such as the property set
 * templates of `ifcopenshell/util/pset`. Browsers have no file system to read them from.
 * The key is the file name or a suffix of its path or URL.
 */
export function registerResource(path: string, bytes: Uint8Array | ArrayBuffer): void {
  resources.set(path.replace(/\\/g, '/'), bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes));
}

/** Open an IFC file by path or file URL, as Python `ifcopenshell.open(path)`; see {@link registerResource}. */
export function openPath(path: string, options?: OpenOptions): File {
  return File.open(readResource(path), String(path).replace(/\\/g, '/'), options);
}

/**
 * Read a data file by path or file URL: bytes given to {@link registerResource} for a matching
 * path, else the file system (Node). Used for data files that Python modules read next to themselves.
 */
export function readResource(path: string): Uint8Array {
  const normalized = String(path).replace(/\\/g, '/');
  for (const [key, bytes] of resources) {
    if (normalized === key || normalized.endsWith(`/${key}`)) return bytes;
  }
  const fs = (globalThis as { process?: { getBuiltinModule?(name: string): unknown } }).process?.getBuiltinModule?.('node:fs') as
    | { readFileSync(path: string | URL): Uint8Array }
    | undefined;
  if (!fs) throw new IfcOpenShellError(`No file system to read ${path}; provide it with registerResource()`);
  return fs.readFileSync(normalized.startsWith('file:') ? new URL(normalized) : normalized);
}

/** The STEP header of a file with Python's attribute names; see {@link File.stepHeader}. */
export interface StepHeader {
  file_name: {
    name: string;
    time_stamp: string;
    author: string[];
    organization: string[];
    preprocessor_version: string;
    originating_system: string;
    authorization: string;
  };
  file_description: { description: string[]; implementation_level: string };
}
