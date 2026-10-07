import { describe, expect, it } from 'vitest';
import { init } from 'ifcopenshell';

describe('browser runtime', () => {
  it('initializes the browser package and loads schema and geometry plugins', async () => {
    const runtime = await init();
    // The streamer must expose FILE_SCHEMA before any schema plugin is loaded.
    const stream = runtime.raw.parse.streamFromString(`ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('','',(''),(''),'','','');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
ENDSEC;
END-ISO-10303-21;`);
    const header = stream!.header()!;
    const declaration = header.fileSchema()!;
    expect(declaration.schemaIdentifiers()).toEqual(['IFC4']);
    expect(runtime.loadedPlugins()).toEqual([]);
    declaration.destroy(); header.destroy(); stream!.destroy();
    await runtime.loadPlugin('schema', 'ifc4');
    expect(runtime.loadedPlugins()).toContain('schema:ifc4');
    await runtime.loadPlugin('kernel', 'opencascade');
    expect(runtime.loadedPlugins()).toContain('kernel:opencascade');
    const file = runtime.raw.parse.newFile('IFC4', 0, '');
    expect(file).not.toBeNull();
    file?.destroy();
  });
});
