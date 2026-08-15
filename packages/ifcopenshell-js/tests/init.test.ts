
import { describe, expect, it } from 'vitest';
import { init, IfcOpenShellError } from '../src/index.js';

describe('init', () => {
  it('boots the default direct runtime in Node', async () => {
    const shell = await init();
    try {
      await shell.loadPlugin('schema', 'ifc4');
      expect(await shell.loadedPlugins()).toContain('schema:ifc4');
    } finally {
      await shell.dispose();
    }
  });

  it('rejects unknown plugins with the public error type', async () => {
    const shell = await init();
    try {
      await expect(shell.loadPlugin('schema', 'definitely-not-a-schema')).rejects.toBeInstanceOf(IfcOpenShellError);
    } finally {
      await shell.dispose();
    }
  });

  it('wraps default asset-resolution failures with the public error type', async () => {
    await expect(init({ wasmRoot: '/definitely-missing-ifcopenshell-wasm-root' })).rejects.toMatchObject({
      name: 'IfcOpenShellError',
      message: 'Failed to resolve packaged WASM assets',
      cause: expect.any(Error),
    });
  });
});
