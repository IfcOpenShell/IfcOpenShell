
/**
 * Core `ifcopenshell` API.
 *
 * @module Core
 */


export {
  init,
  schemaByName,
  ifcopenshell,
  IfcOpenShellError,
  IfcOpenShellErrorCode,
  IfcOpenShellErrorKind,
  abortError,
  isIfcOpenShellAbortError,
} from './init.js';
export type { IfcOpenShell } from './init.js';
export { File, open, openPath, readResource, registerResource } from './file.js';
export type { GetInverseOptions, OpenOptions, StepHeader } from './file.js';
export { EntityInstance } from './entity_instance.js';
export * as guid from './guid.js';
export { version } from './version.js';
/** Native schema and geometry classes, for `instanceof` checks such as Python `isinstance(x, ifcopenshell_wrapper.attribute)`. */
export * as wrapper from '@ifcopenshell/wasm/api';
export type { AttributeValueType, EntityInfoValue, EntityInstanceInfo, GetInfoOptions } from './entity_instance.js';
export { exportToBuffer } from './serializers/index.js';
export type {
  OperationProgress,
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
