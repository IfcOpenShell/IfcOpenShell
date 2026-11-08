// This file was generated with the assistance of an AI coding tool.

import { IfcOpenshellInstance } from '@ifcopenshell/wasm/api';
import type { AttributeValueType as NativeAttributeValueType } from '@ifcopenshell/wasm/api';
import { IfcOpenShellError } from './init.js';

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
    if (typeof key === 'string' && /^[A-Z]/.test(key) && !(key in target)) throw noAttribute(receiver, key);
    return Reflect.get(target, key, receiver);
  },
  set(target, key, value, receiver) {
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
 * @internal Wrap a native instance, installing `entity.AttributeName` accessors for its class.
 * Registered as the WASM instance factory.
 */
export function adoptInstance(handle: IfcOpenshellInstance): EntityInstance {
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
  return new InstanceClass(handle);
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
