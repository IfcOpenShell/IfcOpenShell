import { describe, expect, it } from 'vitest';
import {
  abortError,
  init,
  IfcOpenShellError,
  IfcOpenShellErrorCode,
  IfcOpenShellErrorKind,
  isIfcOpenShellAbortError,
} from '../src/index.js';

describe('init', () => {
  it('boots the default direct runtime in Node', async () => {
    const shell = await init();
    await shell.loadPlugin('schema', 'ifc4');
    expect(await shell.loadedPlugins()).toContain('schema:ifc4');
  });

  it('rejects unknown plugins with the public error type', async () => {
    const shell = await init();
    await expect(shell.loadPlugin('schema', 'definitely-not-a-schema')).rejects.toBeInstanceOf(IfcOpenShellError);
  });

  it('wraps default asset-resolution failures with the public error type', async () => {
    await expect(init({ wasmRoot: '/definitely-missing-ifcopenshell-wasm-root' })).rejects.toMatchObject({
      name: 'IfcOpenShellError',
      message: 'Failed to resolve packaged WASM assets',
      cause: expect.any(Error),
    });
  });

  it('creates typed cancellation errors', () => {
    const error = abortError();
    expect(error).toMatchObject({
      name: 'AbortError',
      kind: IfcOpenShellErrorKind.CANCELLED,
      code: IfcOpenShellErrorCode.OPERATION_CANCELLED,
    });
    expect(isIfcOpenShellAbortError(error)).toBe(true);
  });
});
