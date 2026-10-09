import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe } from 'vitest';
import { init } from 'ifcopenshell';
import type { IfcOpenShell } from 'ifcopenshell';

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

export function listEntities(list: import('@ifcopenshell/wasm/api').IfcOpenshellParseInstanceList): import('ifcopenshell').EntityInstance[] {
  try {
    const result: import('ifcopenshell').EntityInstance[] = [];
    for (let i = 0; i < list.size(); i++) {
      const item = list.get(i) as import('ifcopenshell').EntityInstance | null;
      if (item) result.push(item);
    }
    return result;
  } finally { list.dispose(); }
}
