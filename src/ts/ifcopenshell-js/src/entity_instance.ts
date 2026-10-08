// This file was generated with the assistance of an AI coding tool.

import { IfcOpenshellInstance } from '@ifcopenshell/wasm/api';
import type { AttributeValueType as NativeAttributeValueType } from '@ifcopenshell/wasm/api';
import { IfcOpenShellError } from './init.js';

/** Values decoded by the native WASM attribute typemap. */
export type AttributeValueType = NativeAttributeValueType<entity_instance>;

/** Plain-object snapshot returned by `entity_instance.getInfo()`. */
export interface entity_instance_info {
  id: number;
  type: string;
  attributes: Record<string, AttributeValueType>;
}

/** IFC entity instance with attribute conveniences. */
export class entity_instance extends IfcOpenshellInstance {
  readonly type: string;

  constructor(
    handle: IfcOpenshellInstance,
  ) {
    super(handle);
    this.type = this.className(false);
  }

  get typeName(): string {
    return this.type;
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
   * With `recursive`, referenced entities are expanded as well. Entities that
   * were already visited are replaced by their id, as Python's get_info() does.
   */
  getInfo(options: { recursive?: boolean } = {}): entity_instance_info {
    return this.buildInfo(options.recursive ? new Set([this.id()]) : null);
  }

  toJSON(): entity_instance_info {
    return this.getInfo();
  }

  private buildInfo(ignore: Set<number> | null): entity_instance_info {
    const attributes: Record<string, AttributeValueType> = {};
    for (const [name, value] of this.entries()) {
      attributes[name] = ignore ? this.expand(value, ignore) : value;
    }
    return { id: this.id(), type: this.type, attributes };
  }

  private expand(value: AttributeValueType, ignore: Set<number>): AttributeValueType {
    if (value instanceof entity_instance) {
      if (ignore.has(value.id())) return value.id();
      ignore.add(value.id());
      return value.buildInfo(ignore) as unknown as AttributeValueType;
    }
    if (Array.isArray(value)) {
      return (value as AttributeValueType[]).map((item) => this.expand(item, ignore)) as AttributeValueType;
    }
    return value;
  }

  inverseAttributes(): string[] {
    return this.getInverseAttributeNames();
  }

  /** Return entities referenced by the named inverse attribute. */
  inverse(name: string): entity_instance[] {
    const list = this.getInverse(name);
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

  /** Clear an attribute by name or zero-based index. */
  unset(nameOrIndex: string | number): void {
    this.set(nameOrIndex, null);
  }

  /** Serialize the entity as STEP text. */
  text(validSpf = false): string {
    return this.toString(validSpf);
  }
}
