// This file was generated with the assistance of an AI coding tool.

import { IfcOpenshellInstance } from '@ifcopenshell-js/wasm/api';
import type { AttributeValueType as NativeAttributeValueType } from '@ifcopenshell-js/wasm/api';

/** Values decoded by the native WASM attribute typemap. */
export type AttributeValueType = NativeAttributeValueType<entity_instance>;

/** Plain-object snapshot returned by `entity_instance.info()`. */
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
    return (typeof nameOrIndex === 'string'
      ? this.getArgumentByName(nameOrIndex)
      : this.getArgument(nameOrIndex)) as AttributeValueType;
  }

  attributes(): string[] {
    return this.getAttributeNames();
  }

  entries(): [string, AttributeValueType][] {
    return this.attributes().map((name) => [name, this.get(name)]);
  }

  /** Return the entity id, type, and decoded forward attributes. */
  info(): entity_instance_info {
    return {
      id: this.id(),
      type: this.type,
      attributes: Object.fromEntries(this.entries()),
    };
  }

  toJSON(): entity_instance_info {
    return this.info();
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
