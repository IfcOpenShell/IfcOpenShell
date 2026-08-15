
/**
 * Core `@ifcopenshell-js/web` API.
 *
 * @module Core
 */

import './disposable.js';

export {
  init,
  IfcOpenShellError,
  IfcOpenShellErrorCode,
  IfcOpenShellErrorKind,
  abortError,
  isIfcOpenShellAbortError,
} from './init.js';
export type { IfcOpenShell } from './init.js';
export { IfcFile } from './file.js';
export type { FileInfo, HeaderInfo, OpenOptions } from './file.js';
export { Entity } from './entity.js';
export type { AttributeInput, EntityInfo } from './entity.js';
export { AttributeValue } from './attribute.js';
export type { IfcLogical, IfcValue, NestedEntityIds } from './attribute.js';
export {
  GeomIterator,
  GeomSettings,
  columnMajorToRowMajor4,
  rowMajorToColumnMajor4,
  transformPoint4,
} from './geom/index.js';
export type {
  CollectOptions,
  CollectResult,
  IteratorFilter,
  IteratorMetadata,
  IteratorOptions,
  Mesh,
  MeshFloatArray,
  MeshPrecision,
  MatrixPoint3,
  OperationProgress,
} from './geom/index.js';
export {
  SerializerSettings,
  exportToBuffer,
} from './serializers/index.js';
export type {
  ExportOptions,
  ExportResult,
  SerializerFormat,
} from './serializers/index.js';
export type {
  EmscriptenFS,
  EmscriptenOption,
  EmscriptenOptions,
  EmscriptenModuleFactory,
  IfcOpenshellApiFactory,
  IfcOpenshellModule,
  InitOptions,
  PluginEntry,
  PluginKind,
  PluginLoader,
  PluginManifest,
  Ptr,
  WasmAssets,
} from './types.js';
export * as util from './util/index.js';
