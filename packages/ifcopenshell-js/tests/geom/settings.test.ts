import { beforeAll, describe, expect, it } from 'vitest';
import { createInstance, describeOrSkip } from '../_helper.js';
import { GeomSettings, IfcOpenShellError, type IfcOpenShell } from '../../src/index.js';

describeOrSkip('GeomSettings', () => {
  let shell: IfcOpenShell;

  beforeAll(async () => {
    shell = await createInstance();
  });

  it('lists setting names', async () => {
    await using settings = new GeomSettings(shell);
    const names = await settings.names();
    expect(names.length).toBeGreaterThan(0);
    expect(names.every((name) => typeof name === 'string')).toBe(true);
  });

  it('sets common values through the generic API', async () => {
    await using settings = new GeomSettings(shell);
    await settings.set('weld-vertices', true);
    expect(await settings.getBool('weld-vertices')).toBe(true);

    await settings.set('mesher-linear-deflection', 0.0125);
    expect(await settings.getDouble('mesher-linear-deflection')).toBeCloseTo(0.0125, 6);
  });

  it('retains typed methods for explicit native setting types', async () => {
    await using settings = new GeomSettings(shell);
    await settings.setBool('weld-vertices', false);
    expect(await settings.value('weld-vertices')).toBe(false);
  });

  it('dispose is idempotent and guards released handles', async () => {
    const settings = new GeomSettings(shell);
    settings.dispose();
    settings.dispose();
    expect(() => settings.names()).toThrow(IfcOpenShellError);
  });
});
