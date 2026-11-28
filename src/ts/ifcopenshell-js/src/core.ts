// This file was generated with the assistance of an AI coding tool.

import { init as initialize } from './init.js';
import type { InitOptions, WasmAssets } from './types.js';

export function init(options: InitOptions & { wasmAssets: WasmAssets }) {
  return initialize(options);
}

export {
  schemaByName,
  ifcopenshell,
  IfcOpenShellError,
  IfcOpenShellErrorCode,
  IfcOpenShellErrorKind,
  abortError,
  isIfcOpenShellAbortError,
} from './init.js';
export type { IfcOpenShell } from './init.js';
export { File, open } from './file.js';
export type { GetInverseOptions, OpenOptions } from './file.js';
export { EntityInstance } from './entity_instance.js';
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
