import { IfcOpenshellGeomIterator } from '@ifcopenshell/wasm/api';
import type { File } from '../file.js';
import { IfcOpenShellError, ifcopenshell } from '../init.js';
import type { Settings } from './settings.js';

/** Entity ids or IFC type names, matching the native include/exclude filters. */
export type IteratorFilter = number[] | string[];

/** Optional native iterator configuration. */
export interface IteratorOptions {
  /** The published WASM build is single-threaded; values above 1 throw. */
  numThreads?: number;
  include?: IteratorFilter;
  exclude?: IteratorFilter;
  geometryLibrary?: string;
}

/** One JSON message emitted by the iterator's native logger. */
export interface IteratorLogEntry {
  level: 'Performance' | 'Debug' | 'notice' | 'warning' | 'error';
  message: string;
  time: string;
  code?: string;
  /** IFC STEP representation of the product being processed. */
  product?: string;
  /** IFC STEP representation of the instance associated with the message. */
  instance?: string;
}

/** Synchronous native iterator. Load schema, mapping and kernel plugins before construction. */
export class Iterator extends IfcOpenshellGeomIterator {
  private readonly sourceFile: File;

  constructor(
    readonly settings: Settings,
    file: File,
    options: IteratorOptions = {},
  ) {
    const { numThreads = 1, include, exclude, geometryLibrary = 'opencascade' } = options;
    if (include !== undefined && exclude !== undefined) {
      throw new IfcOpenShellError('Specify either include or exclude, not both');
    }
    const geom = ifcopenshell.geom;
    const filter = include ?? exclude;
    const handle = filter === undefined
      ? geom.createIterator(geometryLibrary, settings, file, numThreads)
      : filter.every(value => typeof value === 'number')
        ? geom.createIteratorWithIncludeExcludeId(geometryLibrary, settings, file, filter as number[], include !== undefined, numThreads)
        : geom.createIteratorWithIncludeExclude(geometryLibrary, settings, file, filter as string[], include !== undefined, numThreads);
    if (!handle || handle.ptr === 0) throw new IfcOpenShellError('Failed to create iterator');
    super(handle);
    this.sourceFile = file;
  }

  /** Returns this iterator's accumulated messages without clearing them. */
  getLogEntries(): IteratorLogEntry[] {
    return this.getLog().split('\n').filter(line => line.trim()).map(line => JSON.parse(line) as IteratorLogEntry);
  }
}
