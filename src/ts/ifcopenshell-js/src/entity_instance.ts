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

/** IFC entity instance with attribute conveniences. */
export class EntityInstance extends IfcOpenshellInstance {
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
    const release = (value: AttributeValueType): void => {
      if (value instanceof EntityInstance) value.dispose();
      else if (Array.isArray(value)) value.forEach(release);
    };
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
            try { info[name] = mapValue(value); } finally { release(value); }
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
    const list = this.getInverse(name);
    try {
      const out: EntityInstance[] = [];
      for (let i = 0; i < list.size(); i++) {
        const item = list.get(i) as EntityInstance | null;
        if (item) out.push(item);
      }
      return out;
    } finally {
      list.destroy();
    }
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

  set(nameOrIndex: string | number, value: AttributeValueType): void {
    if (typeof nameOrIndex === 'string' && this.inverseAttributes().includes(nameOrIndex)) {
      throw new IfcOpenShellError(`Cannot set inverse attribute ${nameOrIndex}`);
    }
    this.setArgument(typeof nameOrIndex === 'number' ? nameOrIndex : this.getArgumentIndex(nameOrIndex), value);
  }
}
