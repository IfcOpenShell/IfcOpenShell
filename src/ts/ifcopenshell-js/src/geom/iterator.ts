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

  /**
   * Returns and clears the runtime-wide log, which is where the geometry kernels report skipped elements.
   * It is shared with `parse.getLog()` and every other iterator, so a second read returns only what was logged since.
   */
  override getLog(): string {
    return ifcopenshell.parse.getLog();
  }
}
