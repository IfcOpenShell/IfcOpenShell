import { beforeAll, expect, it } from 'vitest';
import { createInstance, describeOrSkip } from './_helper.js';
import { IfcFile, IfcOpenShellError, type IfcOpenShell } from '../src/index.js';

describeOrSkip('IfcFile', () => {
  let shell: IfcOpenShell;

  beforeAll(async () => {
    shell = await createInstance();
    await shell.loadPlugin('schema', 'ifc4');
  });

  it('creates, queries, and serializes an IFC file', async () => {
    await using file = await IfcFile.createEmpty(shell, 'IFC4');
    await using wall = file.create('IfcWall', { name: 'Generated wall' });

    expect(wall.type).toBe('IfcWall');
    expect(wall.get('Name')).toBe('Generated wall');
    await using fetched = file.get(wall.id);
    expect(fetched?.type).toBe('IfcWall');
    const walls = file.all('IfcWall');
    try {
      expect(walls.map((entity) => entity.id)).toEqual([wall.id]);
    } finally {
      walls.forEach((entity) => entity.dispose());
    }
    expect(file.text()).toContain('IFCWALL');
  });

  it('guards a disposed file handle', async () => {
    const file = await IfcFile.createEmpty(shell, 'IFC4');
    file.dispose();
    file.dispose();
    expect(() => file.raw).toThrow(IfcOpenShellError);
  });

  it('serializes IFC logical values as JSON', async () => {
    const text = `ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('x.ifc','2026-01-01T00:00:00',(),(),'','','');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
#1=IFCPROPERTYSINGLEVALUE('x',$,IFCLOGICAL(.U.),$);
ENDSEC;
END-ISO-10303-21;`;
    await using file = await IfcFile.open(shell, new TextEncoder().encode(text));
    await using property = file.get(1);
    expect(JSON.parse(shell.raw.parse.getInfoJson(property!.raw, true))).toMatchObject({
      NominalValue: { type: 'IfcLogical', wrappedValue: 'UNKNOWN' },
    });
  });
});
