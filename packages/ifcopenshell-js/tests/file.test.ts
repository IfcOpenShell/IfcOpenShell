import { afterAll, beforeAll, expect, it } from 'vitest';
import { createInstance, describeOrSkip } from './_helper.js';
import { IfcFile, IfcOpenShellError, type IfcOpenShell } from '../src/index.js';

describeOrSkip('IfcFile', () => {
  let shell: IfcOpenShell;

  beforeAll(async () => {
    shell = await createInstance();
    await shell.loadPlugin('schema', 'ifc4');
  });

  afterAll(() => shell.dispose());

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
});
