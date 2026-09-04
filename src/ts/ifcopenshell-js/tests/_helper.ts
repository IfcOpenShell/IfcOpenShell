import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe } from 'vitest';
import { init } from '../src/index.js';
import type { IfcOpenShell } from '../src/index.js';

const wasmDir = process.env.IFCOPENSHELL_WASM_DIR
  ? resolve(process.env.IFCOPENSHELL_WASM_DIR)
  : null;

export const wasmAvailable = wasmDir !== null
  && existsSync(resolve(wasmDir, 'ifcopenshell_api.mjs'))
  && existsSync(resolve(wasmDir, 'ifcopenshell_wasm.node.mjs'))
  && existsSync(resolve(wasmDir, 'ifcopenshell_wasm.wasm'))
  && existsSync(resolve(wasmDir, 'ifcopenshell_plugins.json'));

export const describeOrSkip = wasmAvailable ? describe : describe.skip;

export async function createInstance(): Promise<IfcOpenShell> {
  return init();
}
