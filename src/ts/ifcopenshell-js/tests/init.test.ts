import { describe, expect, it } from 'vitest';
import {
  abortError,
  init,
  ifcopenshell,
  IfcOpenShellError,
  IfcOpenShellErrorCode,
  IfcOpenShellErrorKind,
  isIfcOpenShellAbortError,
} from 'ifcopenshell';

describe('init', () => {
  it('boots the default direct runtime in Node', async () => {
    expect(ifcopenshell).toBeUndefined();
    await expect(init({ wasmAssets: {} as never })).rejects.toThrow('wasmAssets.initModule');
    const first = init();
    expect(init()).toBe(first);
    const runtime = await first;
    expect(await init()).toBe(runtime);
    expect(ifcopenshell).toBe(runtime.raw);
    await expect(init({ pluginLoader: async () => {} })).rejects.toThrow('configure it only on the first');
    await runtime.loadPlugin('schema', 'ifc4');
    expect(await runtime.loadedPlugins()).toContain('schema:ifc4');
  });

  it('rejects unknown plugins with the public error type', async () => {
    const runtime = await init();
    await expect(runtime.loadPlugin('schema', 'definitely-not-a-schema')).rejects.toBeInstanceOf(IfcOpenShellError);
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
