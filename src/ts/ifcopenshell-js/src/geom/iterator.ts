import { IfcOpenshellGeomIterator } from '@ifcopenshell/wasm/api';
import type { file } from '../file.js';
import { IfcOpenShellError, ifcopenshell } from '../init.js';
import type { settings } from './settings.js';

/** Entity ids or IFC type names, matching the native include/exclude filters. */
export type IteratorFilter = number[] | string[];

/** Optional native iterator configuration. */
export interface IteratorOptions {
  numThreads?: number;
  include?: IteratorFilter;
  exclude?: IteratorFilter;
  geometryLibrary?: string;
}

/** Synchronous native iterator. Load schema, mapping and kernel plugins before construction. */
export class iterator extends IfcOpenshellGeomIterator {
  private readonly sourceFile: file;

  constructor(
    readonly settings: settings,
    file: file,
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
}
