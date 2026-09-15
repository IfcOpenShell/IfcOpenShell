import { describe, expect, it, vi } from 'vitest';
import { GeomIterator } from '../../src/index.js';
import type { IfcFile, IfcOpenShell } from '../../src/index.js';
import type { GeomSettings } from '../../src/geom/settings.js';

describe('geometry failure contracts', () => {
  it('reports failed iterator initialization instead of silent exhaustion', async () => {
    const rawIterator = {
      ptr: 1,
      destroy: vi.fn(),
      initialize: vi.fn(() => false),
      hadErrorProcessingElements: vi.fn(() => true),
    };
    const shell = fakeShell({ createIterator: () => rawIterator });
    const iterator = new GeomIterator(shell, fakeFile(), fakeSettings());
    await expect(iterator.nextMesh()).rejects.toThrow(/Failed to initialize GeomIterator.*selected kernel/);
    await iterator[Symbol.asyncDispose]();
    expect(rawIterator.destroy).toHaveBeenCalledOnce();
  });
});

function fakeShell(geom: Record<string, unknown>): IfcOpenShell {
  return {
    loadPlugin: vi.fn(async () => undefined),
    raw: { geom },
  } as unknown as IfcOpenShell;
}

function fakeFile(): IfcFile {
  return { raw: { schemaName: () => 'IFC4' } } as unknown as IfcFile;
}

function fakeSettings(): GeomSettings {
  return { raw: {}, getInt: () => 0 } as unknown as GeomSettings;
}
