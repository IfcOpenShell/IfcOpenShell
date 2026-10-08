import { beforeAll, expect, it } from 'vitest';
import { IfcOpenshellGeomSettings } from '@ifcopenshell/wasm/api';
import { createInstance, describeOrSkip } from '../_helper.js';
import { IfcOpenShellError, type IfcOpenShell } from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';

describeOrSkip('GeomSettings', () => {
  let runtime: IfcOpenShell;

  beforeAll(async () => {
    runtime = await createInstance();
  });

  it('lists setting names', async () => {
    await using settings = new geom.settings();
    expect(settings).toBeInstanceOf(IfcOpenshellGeomSettings);
    expect(settings.set).toBe(IfcOpenshellGeomSettings.prototype.set);
    expect(settings.get).toBe(IfcOpenshellGeomSettings.prototype.get);
    const names = await settings.names();
    expect(names.length).toBeGreaterThan(0);
    expect(names.every((name) => typeof name === 'string')).toBe(true);
  });

  it('sets common values through the generic API', async () => {
    await using settings = new geom.settings();
    settings.set('weld-vertices', false);
    expect(settings.get('weld-vertices')).toBe(false);
    expect(settings.getBool('weld-vertices')).toBe(false);

    await settings.set('mesher-linear-deflection', 0.0125);
    expect(await settings.getDouble('mesher-linear-deflection')).toBeCloseTo(0.0125, 6);
  });

  it('retains typed methods for explicit native setting types', async () => {
    await using settings = new geom.settings();
    await settings.setBool('weld-vertices', false);
    expect(await settings.value('weld-vertices')).toBe(false);
  });

  it('uses the exact native types for enums and empty collection values', () => {
    using settings = new geom.settings();
    const values: [string, string, number | number[] | string[]][] = [
      ['iterator-output', 'IteratorOutputOptions', 0],
      ['dimensionality', 'OutputDimensionalityTypes', 1],
      ['function-step-type', 'FunctionStepMethod', 0],
      ['triangulation-type', 'TriangulationMethod', 0],
      ['model-offset', 'std::vector<double>', [1, 2, 3]],
      ['context-ids', 'std::set<int>', []],
      ['context-types', 'std::set<std::string>', []],
      ['context-priorities', 'std::vector<std::string>', ['Body', 'Axis']],
    ];
    for (const [name, type, value] of values) {
      expect(settings.getType(name)).toBe(type);
      settings.set(name, value);
      expect(settings.value(name)).toEqual(value);
    }
    expect(() => settings.set('nonexistent-setting', 1)).toThrow();
  });

  it('converts values in the native binding and rejects mismatched JS types', () => {
    using settings = runtime.raw.geom.createSettings();
    settings.set('weld-vertices', false);
    expect(settings.get('weld-vertices')).toBe(false);
    settings.set('circle-segments', 24);
    expect(settings.get('circle-segments')).toBe(24);
    settings.set('context-ids', [3, 1, 3]);
    expect(settings.get('context-ids')).toEqual([1, 3]);
    settings.set('context-types', ['Body']);
    expect(settings.get('context-types')).toEqual(['Body']);
    expect(() => settings.set('weld-vertices', 0)).toThrow('Expected boolean');
    expect(() => settings.set('context-ids', [1.5])).toThrow('Expected int32');
    expect(() => settings.set('context-types', [1])).toThrow('Expected string');
    expect(() => settings.set('model-offset', '1,2,3')).toThrow('Expected array');
    expect(() => settings.get('nonexistent-setting')).toThrow();
    settings.destroy();
    expect(() => settings.set('weld-vertices', false)).toThrow('disposed');
    expect(() => settings.get('weld-vertices')).toThrow('disposed');
  });

  it('dispose is idempotent and guards released handles', async () => {
    const settings = new geom.settings();
    settings.dispose();
    settings.dispose();
    expect(() => settings.names()).toThrow(IfcOpenShellError);
  });
});
