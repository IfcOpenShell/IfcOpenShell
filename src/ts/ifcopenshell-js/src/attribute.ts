
import type { IfcOpenshellParseAttributeValue } from '@ifcopenshell-js/wasm/api';
import { Entity } from './entity.js';
import { IfcOpenShellError, type IfcOpenShell } from './init.js';
import { HandleGuard } from './resource.js';

/** Public IFC LOGICAL tri-state representation. */
export type IfcLogical = boolean | 'UNKNOWN';

/** Detached IDs returned for nested entity aggregates whose file ownership is not available here. */
export interface NestedEntityIds {
  readonly kind: 'entityIds';
  readonly values: number[][];
}

/** Decoded scalar or aggregate value of an IFC entity attribute. */
export type IfcValue =
  | null
  | boolean
  | number
  | string
  | Entity
  | Entity[]
  | number[]
  | number[][]
  | string[]
  | NestedEntityIds;

/** Typed view over one native IFC attribute value. */
export class AttributeValue {
  private _raw: IfcOpenshellParseAttributeValue | null;
  private readonly guard: HandleGuard<IfcOpenshellParseAttributeValue>;
  readonly type: string;
  readonly isNull: boolean;

  constructor(
    private readonly shell: IfcOpenShell,
    raw: IfcOpenshellParseAttributeValue,
    owned = true,
  ) {
    this._raw = raw;
    this.guard = new HandleGuard(this, raw, owned);
    this.type = raw.type();
    this.isNull = raw.isNull();
  }

  get raw(): IfcOpenshellParseAttributeValue {
    if (this._raw == null) throw new IfcOpenShellError('AttributeValue has been disposed');
    return this._raw;
  }

  string(): string {
    return this.raw.asString();
  }

  number(): number {
    return this.raw.asDouble();
  }

  integer(): number {
    return this.raw.asInt32();
  }

  boolean(): boolean {
    return this.raw.asBool();
  }

  logical(): IfcLogical {
    const value = this.raw.asLogical();
    return value === 1 ? true : value === 0 ? false : 'UNKNOWN';
  }

  entity(): Entity | null {
    return Entity.wrap(this.shell, this.raw.asInstance());
  }

  entities(): Entity[] {
    const list = this.raw.asInstanceList();
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

  strings(): string[] {
    return this.raw.asStringList();
  }

  numbers(): number[] {
    return this.raw.asDoubleList();
  }

  integers(): number[] {
    return this.raw.asInt32List();
  }

  numberRows(): number[][] {
    return this.raw.asDoubleListList().map((row) => [...row]);
  }

  integerRows(): number[][] {
    return this.raw.asInt32ListList().map((row) => [...row]);
  }

  nestedEntityIds(): NestedEntityIds {
    return { kind: 'entityIds', values: this.raw.asInstanceIdListList().map((row) => [...row]) };
  }

  enumeration(): string {
    return this.raw.asEnumerationValue();
  }

  enumerationIndex(): number {
    return this.raw.asEnumerationIndex();
  }

  /** Decode the attribute according to its native IFC value type. */
  value(): IfcValue {
    if (this.raw.isNull()) return null;
    const type = this.type.trim().toUpperCase().replace(/[\s_-]+/g, ' ');
    if (type === 'ENTITY INSTANCE') return this.entity();
    if (type === 'AGGREGATE OF ENTITY INSTANCE') return this.entities();
    if (type === 'AGGREGATE OF AGGREGATE OF ENTITY INSTANCE') return this.nestedEntityIds();
    if (type === 'ENUMERATION') return this.enumeration();
    if (type === 'BOOL') return this.boolean();
    if (type === 'LOGICAL') return this.logical();
    if (type === 'AGGREGATE OF STRING') return this.strings();
    if (type === 'AGGREGATE OF INT') return this.integers();
    if (type === 'AGGREGATE OF DOUBLE') return this.numbers();
    if (type === 'AGGREGATE OF AGGREGATE OF INT') return this.integerRows();
    if (type === 'AGGREGATE OF AGGREGATE OF DOUBLE') return this.numberRows();
    if (type === 'EMPTY AGGREGATE' || type === 'AGGREGATE OF EMPTY AGGREGATE') return [];
    if (type === 'INT') return this.integer();
    if (type === 'DOUBLE') return this.number();
    if (type === 'STRING' || type === 'BINARY') return this.string();
    try {
      return this.string();
    } catch {
      return this.type;
    }
  }

  size(): number {
    return this.raw.size();
  }

  /** Release the native attribute value handle. */
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
