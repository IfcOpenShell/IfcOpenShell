
import { IfcOpenshellFile } from '@ifcopenshell/wasm/api';
import type { entity_instance } from './entity_instance.js';
import { IfcOpenShellError, abortError, ifcopenshell } from './init.js';
import { inspectEntity, type entity_instance_info } from './util/inspect.js';

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
export class file extends IfcOpenshellFile {
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
  ): file {
    if (options.signal?.aborted) {
      throw abortError('Opening IFC file was aborted', options.signal.reason);
    }
    const handle = ifcopenshell.parse.openBytes(bytes, filename, options.readonly ?? false);
    if (options.signal?.aborted) {
      handle?.destroy();
      throw abortError('Opening IFC file was aborted', options.signal.reason);
    }
    if (!handle || handle.ptr === 0) throw new IfcOpenShellError('Failed to open IFC file');
    return new file(handle);
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

  get isValid(): boolean {
    return this.good() !== 0;
  }

  /** Return an entity by numeric STEP id, or `null` when it is absent. */
  get(id: number): entity_instance | null {
    return catchNull(() => this.byId(id)) as entity_instance | null;
  }

  /** Return an entity by GlobalId, or `null` when it is absent. */
  find(guid: string): entity_instance | null {
    return catchNull(() => this.byGuid(guid)) as entity_instance | null;
  }

  /** Return all entities of a type, optionally excluding its subtypes. */
  all(typeName: string, options: { includeSubtypes?: boolean } = {}): entity_instance[] {
    const list = options.includeSubtypes === false
      ? this.byTypeExclSubtypes(typeName)
      : this.byType(typeName);
    try {
      const out: entity_instance[] = [];
      for (let i = 0; i < list.size(); i++) {
        const item = list.get(i) as entity_instance | null;
        if (item) out.push(item);
      }
      return out;
    } finally {
      list.destroy();
    }
  }

  /** Create an entity through the low-level file API. */
  createEntity(ifcClass: string, options: { predefinedType?: string | null; name?: string | null } = {}): entity_instance {
    const entity = this.createEntityByName(ifcClass) as entity_instance | null;
    if (!entity) throw new IfcOpenShellError(`Failed to create ${ifcClass}`);
    if (options.name != null) entity.set('Name', options.name);
    if (options.predefinedType != null) entity.set('PredefinedType', options.predefinedType);
    return entity;
  }

  /** Add an entity, assigning a new id unless `instanceId` is given explicitly. */
  override add(entity: entity_instance, instanceId = -1): entity_instance {
    const added = super.add(entity, instanceId) as entity_instance | null;
    if (!added) throw new IfcOpenShellError(`Failed to add ${entity.type} to file`);
    return added;
  }

  /** Remove an entity and the relationships referencing it. */
  override remove(entity: entity_instance): void {
    super.remove(entity);
  }

  text(): string {
    return this.toString();
  }

  /** Return schema, entity-id, validity, storage, and header summary data. */
  getInfo(): FileInfo {
    const ids = this.ids;
    return {
      schema: this.schemaName(),
      ids,
      types: this.types(),
      entityCount: ids.length,
      maxId: this.getMaxId(),
      good: this.good(),
      storageMode: this.storageMode(),
      header: this.headerInfo(),
    };
  }

  /** Read the STEP header, returning `null` when no header is available. */
  headerInfo(): HeaderInfo | null {
    const header = this.header();
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
    return this.good();
  }

  unit(unitType: string): number {
    return this.getUnit(unitType);
  }

  totalInverses(entity: entity_instance): number {
    return this.getTotalInverses(entity);
  }

  inverses(entity: entity_instance): entity_instance[] {
    const list = this.getInverse(entity);
    try {
      const out: entity_instance[] = [];
      for (let i = 0; i < list.size(); i++) {
        const item = list.get(i) as entity_instance | null;
        if (item) out.push(item);
      }
      return out;
    } finally {
      list.destroy();
    }
  }

  inverseIndices(entity: entity_instance): number[] {
    return this.getInverseIndices(entity);
  }

  traverseEntities(entity: entity_instance, options: { maxDepth?: number; breadthFirst?: boolean } = {}): entity_instance[] {
    const maxDepth = options.maxDepth ?? -1;
    const list = options.breadthFirst
      ? this.traverseBreadthFirst(entity, maxDepth)
      : this.traverse(entity, maxDepth);
    try {
      const out: entity_instance[] = [];
      for (let i = 0; i < list.size(); i++) {
        const item = list.get(i) as entity_instance | null;
        if (item) out.push(item);
      }
      return out;
    } finally {
      list.destroy();
    }
  }

  /** Return a plain-object inspection snapshot for an entity id. */
  inspect(id: number): Promise<entity_instance_info | null> {
    return inspectEntity(this, id);
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

/** Parse IFC bytes after explicitly loading their schema plugin. */
export function open(bytes: Uint8Array | ArrayBuffer, filename?: string, options?: OpenOptions): file {
  return file.open(bytes, filename, options);
}
