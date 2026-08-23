
import type { IfcOpenshellInstance } from '@ifcopenshell-js/wasm/api';
import { AttributeValue, type IfcValue } from './attribute.js';
import { IfcOpenShellError, type IfcOpenShell } from './init.js';
import { HandleGuard } from './resource.js';

/** Values accepted by {@link Entity.set}. */
export type AttributeInput =
  | null
  | boolean
  | 'UNKNOWN'
  | number
  | string
  | Entity
  | Entity[]
  | Entity[][]
  | number[]
  | number[][]
  | string[];

/** Plain-object snapshot returned by {@link Entity.info}. */
export interface EntityInfo {
  id: number;
  type: string;
  attributes: Record<string, IfcValue>;
}

/** High-level wrapper for one IFC entity instance. */
export class Entity {
  private _raw: IfcOpenshellInstance | null;
  private readonly guard: HandleGuard<IfcOpenshellInstance>;
  readonly id: number;
  readonly type: string;

  private constructor(
    private readonly shell: IfcOpenShell,
    raw: IfcOpenshellInstance,
    owned = true,
  ) {
    this._raw = raw;
    this.guard = new HandleGuard(this, raw, owned);
    this.id = raw.id();
    this.type = raw.className(false);
  }

  static wrap(shell: IfcOpenShell, raw: IfcOpenshellInstance | null, owned = true): Entity | null {
    return raw && raw.ptr !== 0 ? new Entity(shell, raw, owned) : null;
  }

  get raw(): IfcOpenshellInstance {
    if (this._raw == null) throw new IfcOpenShellError('Entity has been disposed');
    return this._raw;
  }

  get typeName(): string {
    return this.type;
  }

  className(withSchema = false): string {
    return this.raw.className(withSchema);
  }

  isA(className: string): boolean {
    return this.raw.isA(className);
  }

  attribute(nameOrIndex: string | number): AttributeValue {
    const raw = typeof nameOrIndex === 'string'
      ? this.raw.getArgumentByName(nameOrIndex)
      : this.raw.getArgument(nameOrIndex);
    return new AttributeValue(this.shell, raw);
  }

  /** Read and decode an attribute by name or zero-based index. */
  get(nameOrIndex: string | number): IfcValue {
    using attribute = this.attribute(nameOrIndex);
    return attribute.value();
  }

  attributes(): string[] {
    return this.raw.getAttributeNames();
  }

  entries(): [string, IfcValue][] {
    return this.attributes().map((name) => [name, this.get(name)]);
  }

  /** Return the entity id, type, and decoded forward attributes. */
  info(): EntityInfo {
    return {
      id: this.id,
      type: this.type,
      attributes: Object.fromEntries(this.entries()),
    };
  }

  toJSON(): EntityInfo {
    return this.info();
  }

  inverseAttributes(): string[] {
    return this.raw.getInverseAttributeNames();
  }

  /** Return entities referenced by the named inverse attribute. */
  inverse(name: string): Entity[] {
    const list = this.raw.getInverse(name);
    try {
      const out: Entity[] = [];
      for (let i = 0; i < list.size(); i++) {
        const item = Entity.wrap(this.shell, list.get(i));
        if (item) out.push(item);
      }
      return out;
    } finally {
      list.destroy();
    }
  }

  attributeIndex(name: string): number {
    return this.raw.getArgumentIndex(name);
  }

  attributeName(index: number): string {
    return this.raw.getArgumentName(index);
  }

  attributeType(nameOrIndex: string | number): string {
    const index = typeof nameOrIndex === 'number' ? nameOrIndex : this.attributeIndex(nameOrIndex);
    return this.raw.getArgumentType(index);
  }

  attributeCategory(name: string): number {
    return this.raw.getAttributeCategory(name);
  }

  /** Set an attribute, inferring the native value kind from its IFC type. */
  set(nameOrIndex: string | number, value: AttributeInput, options: { type?: string } = {}): void {
    const index = typeof nameOrIndex === 'number' ? nameOrIndex : this.attributeIndex(nameOrIndex);
    const nativeType = this.raw.getArgumentType(index);
    if (options.type !== undefined && normalizeArgumentType(options.type) !== normalizeArgumentType(nativeType)) {
      throw new TypeError(`Attribute ${attributeLabel(this, nameOrIndex)} has native type ${nativeType}, not ${options.type}`);
    }
    setArgument(this.shell, this.raw, index, value, nativeType, attributeLabel(this, nameOrIndex));
  }

  /** Clear an attribute by name or zero-based index. */
  unset(nameOrIndex: string | number): void {
    if (typeof nameOrIndex === 'string') {
      this.raw.unsetAttributeValue(nameOrIndex);
      return;
    }
    this.raw.unsetArgument(nameOrIndex);
  }

  /** Serialize the entity as STEP text. */
  text(validSpf = false): string {
    return this.raw.toString(validSpf);
  }

  /** Release the native entity handle. Safe to call more than once. */
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

function setArgument(
  shell: IfcOpenShell,
  entity: IfcOpenshellInstance,
  index: number,
  value: AttributeInput,
  typeName: string,
  label: string,
): void {
  if (value === null) {
    entity.unsetArgument(index);
    return;
  }

  const type = normalizeArgumentType(typeName);
  if (type === 'BOOL') {
    requireType(value, 'boolean', label, typeName);
    entity.setArgumentBool(index, value);
  } else if (type === 'LOGICAL') {
    if (value !== true && value !== false && value !== 'UNKNOWN') invalidValue(label, typeName, value);
    entity.setArgumentLogical(index, value === true ? 1 : value === false ? 0 : -1);
  } else if (type === 'INT') {
    requireInteger(value, label, typeName);
    entity.setArgumentInt32(index, value);
  } else if (type === 'DOUBLE') {
    requireType(value, 'number', label, typeName);
    entity.setArgumentDouble(index, value);
  } else if (type === 'STRING' || type === 'BINARY') {
    requireType(value, 'string', label, typeName);
    entity.setArgumentString(index, value);
  } else if (type === 'ENUMERATION') {
    requireType(value, 'string', label, typeName);
    if (!entity.setArgumentEnumerationByName(index, value)) invalidValue(label, typeName, value);
  } else if (type === 'ENTITY INSTANCE') {
    if (!(value instanceof Entity)) invalidValue(label, typeName, value);
    requireSameFile(entity, [value], label);
    entity.setArgumentInstance(index, value.raw);
  } else if (type === 'AGGREGATE OF ENTITY INSTANCE') {
    const values = requireArray(value, (item): item is Entity => item instanceof Entity, label, typeName);
    requireSameFile(entity, values, label);
    const list = shell.raw.parse.instanceListCreateFromHandles(values.map((item) => item.raw));
    try {
      entity.setArgumentInstanceList(index, list);
    } finally {
      list.destroy();
    }
  } else if (type === 'AGGREGATE OF STRING') {
    entity.setArgumentStringList(index, requireArray(value, isString, label, typeName));
  } else if (type === 'AGGREGATE OF INT') {
    entity.setArgumentInt32List(index, requireArray(value, isInteger, label, typeName));
  } else if (type === 'AGGREGATE OF DOUBLE') {
    entity.setArgumentDoubleList(index, requireArray(value, isNumber, label, typeName));
  } else if (type === 'AGGREGATE OF AGGREGATE OF INT') {
    entity.setArgumentInt32ListList(index, requireNestedArray(value, isInteger, label, typeName));
  } else if (type === 'AGGREGATE OF AGGREGATE OF DOUBLE') {
    entity.setArgumentDoubleListList(index, requireNestedArray(value, isNumber, label, typeName));
  } else if (type === 'AGGREGATE OF AGGREGATE OF ENTITY INSTANCE') {
    const values = requireNestedArray(value, (item): item is Entity => item instanceof Entity, label, typeName);
    requireSameFile(entity, values.flat(), label);
    entity.setArgumentAsAggregateOfAggregateOfEntityInstance(index, values.map((row) => row.map((item) => item.id)));
  } else {
    throw new TypeError(`Attribute ${label} has unsupported native IFC type ${typeName}`);
  }
}

function normalizeArgumentType(type: string): string {
  return type.trim().toUpperCase().replace(/[\s_-]+/g, ' ');
}

function attributeLabel(entity: Entity, nameOrIndex: string | number): string {
  return `${entity.type}.${typeof nameOrIndex === 'number' ? entity.attributeName(nameOrIndex) : nameOrIndex}`;
}

function requireType<T extends 'boolean' | 'number' | 'string'>(
  value: AttributeInput,
  expected: T,
  label: string,
  typeName: string,
): asserts value is T extends 'boolean' ? boolean : T extends 'number' ? number : string {
  if (typeof value !== expected) invalidValue(label, typeName, value);
}

function requireInteger(value: AttributeInput, label: string, typeName: string): asserts value is number {
  if (!isInteger(value)) invalidValue(label, typeName, value);
}

function requireArray<T>(
  value: AttributeInput,
  predicate: (item: unknown) => item is T,
  label: string,
  typeName: string,
): T[] {
  if (!Array.isArray(value) || !value.every(predicate)) invalidValue(label, typeName, value);
  return value as T[];
}

function requireNestedArray<T>(
  value: AttributeInput,
  predicate: (item: unknown) => item is T,
  label: string,
  typeName: string,
): T[][] {
  if (!Array.isArray(value) || !value.every((row) => Array.isArray(row) && row.every(predicate))) {
    invalidValue(label, typeName, value);
  }
  return value as T[][];
}

function isInteger(value: unknown): value is number {
  return typeof value === 'number' && Number.isInteger(value);
}

function isNumber(value: unknown): value is number {
  return typeof value === 'number';
}

function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function requireSameFile(target: IfcOpenshellInstance, references: Entity[], label: string): void {
  const targetFile = target.filePointer();
  for (const reference of references) {
    if (reference.raw.filePointer() !== targetFile) {
      throw new TypeError(`Attribute ${label} cannot reference Entity #${reference.id} from a different IFC file`);
    }
  }
}

function invalidValue(label: string, typeName: string, value: unknown): never {
  const shape = Array.isArray(value) ? 'array' : value instanceof Entity ? 'Entity' : typeof value;
  throw new TypeError(`Attribute ${label} expects ${typeName}; received incompatible ${shape} value`);
}
