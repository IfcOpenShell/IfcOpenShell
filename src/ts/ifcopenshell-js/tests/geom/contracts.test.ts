import { afterEach, beforeAll, expect, it, vi } from 'vitest';
import { IfcOpenshellGeomIterator } from '@ifcopenshell/wasm/api';
import { File as makeFile, type IfcOpenShell } from 'ifcopenshell';
import * as geomApi from 'ifcopenshell/geom';
import { createInstance, describeOrSkip } from '../_helper.js';

import * as runtimeModule from '../../dist/init.js';

// Use real native handles so construction exercises the generated ownership transfer.
describeOrSkip('native geometry iterator contract', () => {
  let runtime: IfcOpenShell;
  beforeAll(async () => {
    runtime = await createInstance();
    await runtime.loadPlugin('schema', 'ifc4');
    await runtime.loadPlugin('mapping', 'ifc4');
    await runtime.loadPlugin('kernel', 'opencascade');
  });

  afterEach(() => vi.restoreAllMocks());

  function fixture() {
    vi.restoreAllMocks();
    const geom = {
      ...runtime.raw.geom,
      createIterator: vi.fn(runtime.raw.geom.createIterator),
      createIteratorWithIncludeExcludeId: vi.fn(runtime.raw.geom.createIteratorWithIncludeExcludeId),
      createIteratorWithIncludeExclude: vi.fn(runtime.raw.geom.createIteratorWithIncludeExclude),
    };
    const testRuntime = { ...runtime, loadPlugin: vi.fn(), raw: { ...runtime.raw, geom } };
    vi.spyOn(runtimeModule, 'ifcopenshell', 'get').mockReturnValue(testRuntime.raw);
    const file = new makeFile('IFC4');
    return { geom, runtime: testRuntime, file };
  }

  it('inherits native methods and transfers the factory handle without loading or initializing', () => {
    const { geom, runtime, file } = fixture();
    using ownedFile = file;
    using settings = new geomApi.Settings();
    const initialize = vi.spyOn(IfcOpenshellGeomIterator.prototype, 'initialize');
    try {
      using iterator = new geomApi.Iterator(settings, file);
      expect(iterator).toBeInstanceOf(IfcOpenshellGeomIterator);
      expect(iterator.initialize).toBe(IfcOpenshellGeomIterator.prototype.initialize);
      expect(iterator.get).toBe(IfcOpenshellGeomIterator.prototype.get);
      expect(iterator.next).toBe(IfcOpenshellGeomIterator.prototype.next);
      expect(geom.createIterator).toHaveBeenCalledWith('opencascade', settings, file, 1);
      expect(runtime.loadPlugin).not.toHaveBeenCalled();
      expect(initialize).not.toHaveBeenCalled();
      const source = geom.createIterator.mock.results[0]!.value!;
      expect(source.ptr).toBe(0);
      expect(iterator.ptr).not.toBe(0);
      source.destroy();
      // An empty file has no first shape; preserve the native false result.
      expect(iterator.initialize()).toBe(false);
      iterator.dispose();
      iterator.destroy();
      expect(iterator.ptr).toBe(0);
      expect(() => iterator.get()).toThrow('disposed');
      expect(settings.getBool('weld-vertices')).toBeTypeOf('boolean');
      expect(file.schema()).toBe('IFC4');
    } finally {
      initialize.mockRestore();
    }
  });

  it('passes filters through and rejects simultaneous include/exclude', () => {
    const { geom, file } = fixture();
    using ownedFile = file;
    using settings = new geomApi.Settings();
    using included = new geomApi.Iterator(settings, file, { numThreads: 2, include: [123], geometryLibrary: 'opencascade' });
    expect(geom.createIteratorWithIncludeExcludeId).toHaveBeenCalledWith('opencascade', settings, file, [123], true, 2);
    using excluded = new geomApi.Iterator(settings, file, { exclude: ['IfcSpace'] });
    expect(geom.createIteratorWithIncludeExclude).toHaveBeenCalledWith('opencascade', settings, file, ['IfcSpace'], false, 1);
    expect(() => new geomApi.Iterator(settings, file, { include: [], exclude: [] })).toThrow('either include or exclude');
  });
});
