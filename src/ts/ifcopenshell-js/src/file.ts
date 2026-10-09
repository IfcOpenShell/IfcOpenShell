
import { IfcOpenshellFile } from '@ifcopenshell/wasm/api';
import type { AttributeValueType, EntityInstance } from './entity_instance.js';
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

/** High-level wrapper for an IFC file and its entity graph. */
export class File extends IfcOpenshellFile {
  /** Create an empty file, or take ownership of an existing native file handle. */
  constructor(schemaOrHandle: string | IfcOpenshellFile = 'IFC4') {
    const handle = typeof schemaOrHandle === 'string'
      ? ifcopenshell.parse.newFile(schemaOrHandle, 0, '')
      : schemaOrHandle;
    if (!handle || handle.ptr === 0) throw new IfcOpenShellError('Failed to create IFC file');
    super(handle);
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

  declare byId: (id: number) => EntityInstance;
  declare byGuid: (guid: string) => EntityInstance;

  /** Create an entity with any of its IFC attributes, using their schema names. */
  create(ifcClass: string, attributes: Record<string, AttributeValueType> = {}): EntityInstance {
    const entity = this.createEntityByName(ifcClass) as EntityInstance | null;
    if (!entity) throw new IfcOpenShellError(`Failed to create ${ifcClass}`);
    try {
      for (const [name, value] of Object.entries(attributes)) entity.set(name, value);
      return entity;
    } catch (error) {
      try { this.remove(entity); } finally { entity.dispose(); }
      throw error;
    }
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
    using list = this.getInverseList(entity);
    const entities: EntityInstance[] = [];
    for (let i = 0; i < list.size(); i++) {
      const item = list.get(i) as EntityInstance | null;
      if (item) entities.push(item);
    }
    if (withAttributeIndices) {
      const indices = this.getInverseIndices(entity);
      return entities.map((item, i) => [item, indices[i]!] as [EntityInstance, number]);
    }
    if (allowDuplicate) return entities;
    // JS Set uses object identity; native getters produce a fresh handle for each occurrence.
    const unique = new Map<number, EntityInstance>();
    for (const item of entities) {
      if (unique.has(item.identity())) item.dispose();
      else unique.set(item.identity(), item);
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
