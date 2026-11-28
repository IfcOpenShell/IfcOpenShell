// This file was generated with the assistance of an AI coding tool.

import { describe, expect, it } from 'vitest';
import { init, File, ifcopenshell, IfcOpenShellError } from 'ifcopenshell/core';
import { init as defaultInit, File as DefaultFile } from 'ifcopenshell';
import { Settings } from 'ifcopenshell/geom';
import * as core from '@ifcopenshell/wasm/core';
import ifc4 from '@ifcopenshell/wasm/plugins/schema/ifc4';
import ifc4Mapping from '@ifcopenshell/wasm/plugins/mapping/ifc4';
import manifold from '@ifcopenshell/wasm/plugins/kernel/manifold';

describe('explicit-asset entry', () => {
  it('requires wasmAssets', async () => {
    // @ts-expect-error Exercise JavaScript callers without options.
    await expect(init()).rejects.toThrow(new IfcOpenShellError('wasmAssets is required by ifcopenshell/core'));
  });

  it('loads selected plugins and shares the runtime with other entries', async () => {
    const runtime = await init({
      wasmAssets: {
        ...core,
        manifest: {
          schema: { ifc4 },
          mapping: { ifc4: ifc4Mapping },
          kernel: { manifold },
        },
      },
    });
    await runtime.loadPlugin('schema', 'ifc4');
    await runtime.loadPlugin('mapping', 'ifc4');
    await runtime.loadPlugin('kernel', 'manifold');
    expect(runtime.loadedPlugins()).toEqual(['schema:ifc4', 'mapping:ifc4', 'kernel:manifold']);
    expect(await defaultInit()).toBe(runtime);
    expect(ifcopenshell).toBe(runtime.raw);
    expect(File).toBe(DefaultFile);
    using file = new File('IFC4');
    expect(file.create('IfcWall', { Name: 'Selected plugins' }).Name).toBe('Selected plugins');
    const settings = new Settings();
    settings.set('weld-vertices', false);
    expect(settings.get('weld-vertices')).toBe(false);
  });
});
