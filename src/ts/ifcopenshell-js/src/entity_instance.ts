// This file was generated with the assistance of an AI coding tool.

import { IfcOpenshellInstance } from '@ifcopenshell/wasm/api';
import type { AttributeValueType as NativeAttributeValueType } from '@ifcopenshell/wasm/api';
import { IfcOpenShellError, downcasting, indexDeclarations } from './init.js';
import { File } from './file.js';

/** Values decoded by the native WASM attribute typemap. */
export type AttributeValueType = NativeAttributeValueType<EntityInstance>;

export type EntityInfoValue<T = never> = null | boolean | number | bigint | string | EntityInstance | EntityInstanceInfo<T> | T | EntityInfoValue<T>[];

/** Flat dictionary returned by `EntityInstance.getInfo()`. */
export interface EntityInstanceInfo<T = never> {
  id?: number;
  type: string;
  [attribute: string]: EntityInfoValue<T> | undefined;
}

export interface GetInfoOptions<T = EntityInstanceInfo> {
  includeIdentifier?: boolean;
  recursive?: boolean;
  ignore?: readonly string[];
  returnType?: (info: EntityInstanceInfo<unknown>) => T;
}

/**
 * IFC entity instance.
 *
 * Schema attributes are properties, as in Python: `wall.Name`,
 * `wall.Name = 'W1'`, and inverse attributes such as `wall.Decomposes`.
 * Unknown attributes throw instead of reading `undefined` or adding a property.
 * `get` and `set` remain for index access and computed names.
 */
export class EntityInstance extends IfcOpenshellInstance {
  /** Schema attribute or inverse, such as `Name` or `Decomposes`. */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [ifcAttribute: Capitalize<string>]: any;
  /** Value of a defined-type wrapper such as `IfcLabel`. */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  declare wrappedValue: any;

  constructor(
    handle: IfcOpenshellInstance,
  ) {
    super(handle);
  }

  override isA(name: string): boolean;
  override isA(withSchema?: boolean): string;
  override isA(nameOrSchema: string | boolean = false): string | boolean {
    return typeof nameOrSchema === 'string'
      ? super.isA(nameOrSchema)
      : this.className(nameOrSchema);
  }

  /** Read an attribute by name or index. Prefer `entity.Name`. */
  get(nameOrIndex: string | number): AttributeValueType {
    if (typeof nameOrIndex === 'string') {
      // Inverse attributes are served through the same accessor, as getattr() does in Python.
      if (this.inverseAttributes().includes(nameOrIndex)) {
        return this.inverse(nameOrIndex) as unknown as AttributeValueType;
      }
      return this.getArgumentByName(nameOrIndex) as AttributeValueType;
    }
    return this.getArgument(nameOrIndex) as AttributeValueType;
  }

  attributes(): string[] {
    return this.getAttributeNames();
  }

  /** Whether this is an entity rather than an inline typed value such as IfcLabel, as Python `entity.is_entity()`. */
  isEntity(): boolean {
    return super.declaration().asEntity() !== null;
  }

  /** Schema declaration of this entity's class, downcast as Python `entity.declaration`. */
  override declaration(): ReturnType<IfcOpenshellInstance['declaration']> {
    const declaration = super.declaration();
    indexDeclarations(declaration.schema());
    return downcasting(declaration);
  }

  /** The file containing this entity, as Python `entity.file`; null for instances outside a file. */
  override file(): File | null {
    return File.fromPointer(this.filePointer());
  }

  /** Replace values matching `f` with `g(value)`, recursing into lists, as Python `entity.walk`. */
  walk(f: (value: unknown) => boolean, g: (value: unknown) => unknown, value: unknown): unknown {
    if (Array.isArray(value)) return value.map(item => this.walk(f, g, item));
    return f(value) ? g(value) : value;
  }

  /** Forward attribute values in schema order, as iterating a Python entity. */
  *[Symbol.iterator](): IterableIterator<AttributeValueType> {
    const count = this.attributes().length;
    for (let index = 0; index < count; index++) yield this.getArgument(index) as AttributeValueType;
  }

  entries(): [string, AttributeValueType][] {
    return this.attributes().map((name) => [name, this.get(name)]);
  }

  /**
   * Return the entity id, type, and decoded forward attributes.
   *
   * With `recursive`, referenced entities are expanded as well.
   */
  getInfo(options?: GetInfoOptions): EntityInstanceInfo;
  getInfo<T>(options: Omit<GetInfoOptions<T>, 'returnType'> & { returnType: (info: EntityInstanceInfo<unknown>) => T }): T;
  getInfo<T = EntityInstanceInfo>(options: GetInfoOptions<T> = {}): T | EntityInstanceInfo<T> {
    const active = new Set<number>();
    const ignore = new Set(options.ignore);
    const mapValue = (value: AttributeValueType): EntityInfoValue<T> => {
      if (value instanceof EntityInstance) {
        return buildInfo(value);
      }
      if (Array.isArray(value)) {
        return value.map(mapValue);
      }
      return value;
    }
    const buildInfo = (instance: EntityInstance): T | EntityInstanceInfo<T> => {
      const identity = instance.identity();
      if (active.has(identity)) throw new RangeError('Cyclic entity reference in recursive getInfo');
      active.add(identity);
      const info: EntityInstanceInfo<T> = options.includeIdentifier ?? true
        ? { id: instance.id(), type: instance.isA() }
        : { type: instance.isA() };
      try {
        for (const name of instance.attributes()) {
          if (ignore.has(name)) continue;
          const value = instance.get(name);
          if (options.recursive) {
            info[name] = mapValue(value);
          } else {
            info[name] = value;
          }
        }
        return options.returnType ? options.returnType(info) : info;
      } finally {
        active.delete(identity);
      }
    };
    return buildInfo(this);
  }

  inverseAttributes(): string[] {
    return this.getInverseAttributeNames();
  }

  /** Return entities referenced by the named inverse attribute. */
  inverse(name: string): EntityInstance[] {
    return this.getInverse(name) as EntityInstance[];
  }

  attributeIndex(name: string): number {
    return this.getArgumentIndex(name);
  }

  attributeName(index: number): string {
    return this.getArgumentName(index);
  }

  attributeType(nameOrIndex: string | number): string {
    const index = typeof nameOrIndex === 'number' ? nameOrIndex : this.attributeIndex(nameOrIndex);
    return this.getArgumentType(index);
  }

  attributeCategory(name: string): number {
    return this.getAttributeCategory(name);
  }

  /** Set an attribute by name or index. Prefer `entity.Name = value`. */
  /**
   * Write an attribute by index. Typed values such as IfcLabel('x') created in another file are
   * recreated in this one, since they have no identity; Python accepts them the same way.
   */
  override setArgument(index: number, value: AttributeValueType): void {
    super.setArgument(index, this.ownValue(value) as never);
  }

  private ownValue(value: unknown): unknown {
    if (Array.isArray(value)) return value.map(item => this.ownValue(item));
    if (value instanceof EntityInstance && value.id() === 0 && value.filePointer() !== this.filePointer()) {
      const file = this.file();
      if (file) return file.create(value.isA(), [this.ownValue(value.wrappedValue) as AttributeValueType]);
    }
    return value;
  }

  set(nameOrIndex: string | number, value: AttributeValueType): void {
    if (typeof nameOrIndex === 'string' && this.inverseAttributes().includes(nameOrIndex)) {
      throw new IfcOpenShellError(`Cannot set inverse attribute ${nameOrIndex}`);
    }
    this.setArgument(typeof nameOrIndex === 'number' ? nameOrIndex : this.getArgumentIndex(nameOrIndex), value);
  }
}

/**
 * Rejects names that neither EntityInstance nor the native class defines. Writes are rejected
 * like Python's AttributeError; reads are rejected only for capitalized names, because promises,
 * test matchers and serializers probe lowercase names such as `then` or `toJSON`.
 * `getPrototypeOf` exposes the native prototype so `instanceof IfcOpenshellInstance` still holds.
 */
Object.setPrototypeOf(EntityInstance.prototype, new Proxy(IfcOpenshellInstance.prototype, {
  getPrototypeOf(target) {
    return target;
  },
  get(target, key, receiver) {
    // entity[0] reads the first attribute, as Python entity indexing.
    if (typeof key === 'string' && /^\d+$/.test(key)) return (receiver as EntityInstance).getArgument(Number(key));
    if (typeof key === 'string' && /^[A-Z]/.test(key) && !(key in target)) throw noAttribute(receiver, key);
    return Reflect.get(target, key, receiver);
  },
  set(target, key, value, receiver) {
    if (typeof key === 'string' && /^\d+$/.test(key)) {
      (receiver as EntityInstance).set(Number(key), value);
      return true;
    }
    if (typeof key === 'string' && !(key in target)) throw noAttribute(receiver, key);
    return Reflect.set(target, key, value, receiver);
  },
}));

function noAttribute(entity: EntityInstance, name: string): IfcOpenShellError {
  return new IfcOpenShellError(`entity instance of type '${entity.className(true)}' has no attribute '${name}'`);
}

/** One generated subclass per schema-qualified IFC class, carrying its attribute accessors. */
const instanceClasses = new Map<string, typeof EntityInstance>();

/**
 * One wrapper per native instance and file, so that entities compare with `===` and work
 * as `Set` members and `Map` keys, like Python entity equality and hashing.
 */
const canonical = new Map<number, Map<number, WeakRef<EntityInstance>>>();
const collected = new FinalizationRegistry<[number, number]>(([file, identity]) => {
  const wrappers = canonical.get(file);
  if (wrappers && !wrappers.get(identity)?.deref()) wrappers.delete(identity);
});

/** @internal Drop the canonical wrapper of a removed instance. */
export function forgetInstance(entity: IfcOpenshellInstance): void {
  canonical.get(entity.filePointer())?.delete(entity.identity());
}

/** @internal Drop all canonical wrappers of a file that is being destroyed. */
export function forgetFile(filePointer: number): void {
  canonical.delete(filePointer);
}

/**
 * @internal Wrap a native instance, installing `entity.AttributeName` accessors for its class.
 * Registered as the WASM instance factory.
 */
export function adoptInstance(handle: IfcOpenshellInstance): EntityInstance {
  const file = handle.filePointer();
  const identity = file ? handle.identity() : 0;
  const cached = file ? canonical.get(file)?.get(identity)?.deref() : undefined;
  if (cached) return cached;
  const key = handle.className(true);
  let InstanceClass = instanceClasses.get(key);
  if (!InstanceClass) {
    InstanceClass = class extends EntityInstance {};
    Object.defineProperty(InstanceClass, 'name', { value: handle.className(false) });
    // Chrome labels objects by the compiled class name, ignoring the `name` override above.
    Object.defineProperty(InstanceClass.prototype, Symbol.toStringTag, { value: handle.className(false) });
    defineAttributeAccessors(InstanceClass.prototype, handle);
    instanceClasses.set(key, InstanceClass);
  }
  const entity = new InstanceClass(handle);
  if (file) {
    let wrappers = canonical.get(file);
    if (!wrappers) canonical.set(file, wrappers = new Map());
    wrappers.set(identity, new WeakRef(entity));
    collected.register(entity, [file, identity]);
  }
  return entity;
}

/** Non-enumerable, so listing an entity does not read every attribute. */
function defineAttributeAccessors(prototype: EntityInstance, handle: IfcOpenshellInstance): void {
  for (const name of handle.getAttributeNames()) {
    if (name in prototype) continue;
    const index = handle.getArgumentIndex(name);
    Object.defineProperty(prototype, name, {
      get(this: EntityInstance) {
        return this.getArgument(index);
      },
      set(this: EntityInstance, value: AttributeValueType) {
        this.setArgument(index, value);
      },
    });
  }
  for (const name of handle.getInverseAttributeNames()) {
    if (name in prototype) continue;
    Object.defineProperty(prototype, name, {
      get(this: EntityInstance) {
        return this.inverse(name);
      },
      set() {
        throw new IfcOpenShellError(`Cannot set inverse attribute ${name}`);
      },
    });
  }
}
