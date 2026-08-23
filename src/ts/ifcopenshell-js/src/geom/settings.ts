
import type { IfcOpenshellGeomSettings } from '@ifcopenshell-js/wasm/api';
import { IfcOpenShellError, type IfcOpenShell } from '../init.js';
import { HandleGuard } from '../resource.js';

/** Value accepted by a geometry setting setter. */
export type SettingInput = boolean | number | string | number[] | string[];
type SettingType = 'bool' | 'double' | 'int' | 'string' | 'intSet' | 'doubleList' | 'stringSet';

/** Owned wrapper for native geometry interpretation settings. */
export class GeomSettings {
  private _raw: IfcOpenshellGeomSettings | null;
  private readonly guard: HandleGuard<IfcOpenshellGeomSettings>;

  constructor(shell: IfcOpenShell) {
    this._raw = shell.raw.geom.createSettings();
    this.guard = new HandleGuard(this, this._raw, true);
  }

  get raw(): IfcOpenshellGeomSettings {
    if (this._raw == null) throw new IfcOpenShellError('GeomSettings has been disposed');
    return this._raw;
  }

  setBool(name: string, value: boolean): void {
    this.raw.setBool(name, value);
  }

  setDouble(name: string, value: number): void {
    this.raw.setDouble(name, value);
  }

  setInt(name: string, value: number): void {
    this.raw.setInt(name, value);
  }

  setString(name: string, value: string): void {
    this.raw.setString(name, value);
  }

  setIntSet(name: string, value: number[]): void {
    this.raw.setIntSet(name, value);
  }

  setDoubleList(name: string, value: number[]): void {
    this.raw.setDoubleList(name, value);
  }

  setStringSet(name: string, value: string[]): void {
    this.raw.setStringSet(name, value);
  }

  /** Set a named setting using the native setting type when available. */
  set(name: string, value: SettingInput): void {
    if (typeof value === 'boolean') this.setBool(name, value);
    else if (typeof value === 'string') this.setString(name, value);
    else if (Array.isArray(value)) {
      if (value.every((item): item is string => typeof item === 'string')) this.setStringSet(name, value);
      else if (normalizeSettingType(catchString(() => this.getType(name), 'intSet')) === 'doubleList') {
        this.setDoubleList(name, value);
      } else {
        this.setIntSet(name, value);
      }
    } else if (normalizeSettingType(catchString(() => this.getType(name), 'double')) === 'int') {
      this.setInt(name, value);
    } else {
      this.setDouble(name, value);
    }
  }

  getBool(name: string): boolean {
    return this.raw.getBool(name);
  }

  getDouble(name: string): number {
    return this.raw.getDouble(name);
  }

  getInt(name: string): number {
    return this.raw.getInt(name);
  }

  getString(name: string): string {
    return this.raw.getString(name);
  }

  getIntSet(name: string): number[] {
    return this.raw.getIntSet(name);
  }

  getDoubleList(name: string): number[] {
    return this.raw.getDoubleList(name);
  }

  getStringSet(name: string): string[] {
    return this.raw.getStringSet(name);
  }

  getType(name: string): string {
    return this.raw.getType(name);
  }

  /** Read a named setting using its native scalar or list representation. */
  value(name: string): SettingInput {
    const type = normalizeSettingType(this.getType(name));
    if (type === 'bool') return this.getBool(name);
    if (type === 'int') return this.getInt(name);
    if (type === 'string') return this.getString(name);
    if (type === 'intSet') return this.getIntSet(name);
    if (type === 'doubleList') return this.getDoubleList(name);
    if (type === 'stringSet') return this.getStringSet(name);
    return this.getDouble(name);
  }

  /** Return the names exposed by the native geometry settings object. */
  settingNames(): string[] {
    return this.raw.settingNames();
  }

  names(): string[] {
    return this.settingNames();
  }

  /** Release the native settings handle. */
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

function normalizeSettingType(type: string): SettingType {
  const normalized = type.toLowerCase().replace(/[\s_-]+/g, '');
  if (normalized.includes('bool')) return 'bool';
  if (normalized === 'int' || normalized.includes('integer')) return 'int';
  if (normalized.includes('stringset')) return 'stringSet';
  if (normalized.includes('doublelist')) return 'doubleList';
  if (normalized.includes('string')) return 'string';
  if (normalized.includes('set')) return 'intSet';
  return 'double';
}

function catchString(fn: () => string, fallback: string): string {
  try {
    return fn();
  } catch {
    return fallback;
  }
}
