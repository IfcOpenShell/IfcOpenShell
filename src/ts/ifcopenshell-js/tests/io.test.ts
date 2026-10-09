// This file was generated with the assistance of an AI coding tool.

/**
 * Basic I/O, ported from `test/tests.py`.
 *
 * The Python file opens `input/acad2010_walls.ifc` (a submodule this package
 * does not have) and then asserts on `ifcopenshell.file` and
 * `ifcopenshell.entity_instance` behaviour. The same operations are covered
 * here: the model under test is an inline SPF sample, and everything else is
 * built through the API and round-tripped through serialization.
 *
 * Left out because the TypeScript API has no counterpart yet: `file.types()`.
 */

import { beforeAll, expect, it } from 'vitest';
import * as ifcopenshell from 'ifcopenshell';
import { createInstance, describeOrSkip, listEntities } from './_helper.js';

/** Minimal IFC4 sample with a wall, a point and a typed property value. */

const WALL_GUID = '2oDrMkUQb3vB0ekOiTdteW';

const SAMPLE = `ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('basic-io.ifc','2026-01-01T00:00:00',(''),(''),'','','');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
#1=IFCCARTESIANPOINT((0.,0.,0.));
#2=IFCWALL('${WALL_GUID}',$,'Wall',$,$,$,$,$,$);
#3=IFCPROPERTYSINGLEVALUE('FireRating',$,IFCLABEL('F30'),$);
ENDSEC;
END-ISO-10303-21;`;

function openSample(): ifcopenshell.File {
  return ifcopenshell.open(new TextEncoder().encode(SAMPLE));
}

describeOrSkip('basic I/O', () => {
  let runtime: ifcopenshell.IfcOpenShell;
  beforeAll(async () => {
    runtime = await createInstance();
    await runtime.loadPlugin('schema', 'ifc4');
  });

  it('keeps formatted inspection separate from entity info and handles absent ids', async () => {
    using file = openSample();
    expect(await ifcopenshell.util.inspectEntity(file, 2)).toMatchObject({
      id: 2,
      type: 'IfcWall',
      guid: WALL_GUID,
      attributes: expect.arrayContaining([{ name: 'Name', value: 'Wall' }]),
    });
    expect(await ifcopenshell.util.inspectEntity(file, 999)).toBeNull();
    expect(() => file.byId(999)).toThrow();
    expect(() => file.byGuid('missing')).toThrow();
  });

  it('opens a model and answers the by_id, by_guid and by_type queries', () => {
    using file = openSample();
    expect(file.schema()).toBe('IFC4');
    expect(file.entityCount).toBe(3);
    expect(file.ids).toEqual([1, 2, 3]);

    // f[1].is_a("IfcCartesianPoint") / f.by_id(1)
    using point = file.byId(1)!;
    expect(point.isA()).toBe('IfcCartesianPoint');
    expect(point.isA(false)).toBe('IfcCartesianPoint');
    expect(point.isA(true)).toBe('IFC4.IfcCartesianPoint');
    expect(point.isA('IfcCartesianPoint')).toBe(true);
    expect(point.isA('IfcRepresentationItem')).toBe(true);
    expect(point.isA('IfcWall')).toBe(false);
    expect(point.className(false)).toBe('IfcCartesianPoint');

    // f["28pa2ppDf1IA$BaQrvAf48"].is_a("IfcProject") / f.by_guid(...)
    using wall = file.byGuid(WALL_GUID)!;
    expect(wall?.isA()).toBe('IfcWall');
    expect(wall.id()).toBe(2);
    using found = file.byGuid(WALL_GUID)!;
    expect(found.id()).toBe(2);

    // f.by_type("IfcProject")
    expect(listEntities(file.byType('IfcCartesianPoint')).map(entity => entity.id())).toEqual([1]);

    // is_a() reports the declaration, so a declared supertype only matches when
    // subtypes are requested; they are included by default.
    expect(listEntities(file.byTypeExclSubtypes('IfcRepresentationItem'))).toEqual([]);
    expect(listEntities(file.byType('IfcRepresentationItem')).map(entity => entity.id())).toEqual([1]);
  });

  it('reads attributes, typed values and inverses', () => {
    using file = openSample();
    using wall = file.byId(2)!;
    using property = file.byId(3)!;

    // f[22].Id == "" / f[22].Addresses is None
    expect(wall.get('Name')).toBe('Wall');
    expect(wall.get('Description')).toBeNull();

    // prop.NominalValue.wrappedValue: the inline IfcLabel carries the value.
    using nominal = property.get('NominalValue') as ifcopenshell.EntityInstance;
    expect(nominal.get(0)).toBe('F30');

    // get_info() returns the id, type and decoded forward attributes.
    const info = wall.getInfo();
    expect(info.id).toBe(2);
    expect(info.type).toBe('IfcWall');
    expect(info.Name).toBe('Wall');
    expect(Object.keys(info)).toContain('Name');

    // Inverse attributes of a wall that nothing points at yet.
    expect(wall.inverseAttributes()).toContain('HasAssociations');
    expect(wall.inverse('HasAssociations')).toEqual([]);
  });

  it('serializes and reopens with the same queries answered', () => {
    using file = openSample();
    using wall = file.byId(2)!;

    // f.write("output.ifc") then reading the file back.
    const text = file.toString();
    expect(text).toContain('IFCWALL');
    expect(text).toContain('Wall');

    using reopened = ifcopenshell.open(new TextEncoder().encode(text));
    expect(reopened.schema()).toBe('IFC4');
    expect(reopened.entityCount).toBe(file.entityCount);

    const reopenedWall = reopened.byGuid(WALL_GUID);
    console.log('GUID lookup:', reopenedWall?.isA(), 'count:', reopened.entityCount, 'guid in text:', text.includes(WALL_GUID));
    expect(reopenedWall?.isA()).toBe('IfcWall');
    expect(reopenedWall.get('Name')).toBe('Wall');
  });

  it('creates entities, mutates attributes and writes valid SPF', () => {
    using file = new ifcopenshell.File('IFC4');
    expect(file.schema()).toBe('IFC4');

    // f.createIfcCartesianPoint((0.0, 0.0, 0.0))
    using point = file.create('IfcCartesianPoint');
    point.set('Coordinates', [0, 0, 0]);
    expect(point.isA()).toBe('IfcCartesianPoint');
    expect(point.get('Coordinates')).toEqual([0, 0, 0]);

    using wall = file.create('IfcWall', { Name: 'Wall' });
    // f[22].Id = "123" / "123" in str(f[22])
    wall.set('Description', '123');
    expect(wall.toString(true)).toContain('123');
    expect(wall.get('Description')).toBe('123');
    wall.unsetAttributeValue('Description');
    expect(wall.get('Description')).toBeNull();
    expect(wall.toString(true)).not.toContain('123');

    const text = file.toString();
    expect(text).toContain('IFCWALL');

    // The ids and the entity count agree on what the file holds.
    expect(file.ids.length).toBe(file.entityCount);
    expect(file.maxId).toBe(Math.max(...file.ids));
  });

  it('keeps inverses and traversals consistent when references move', () => {
    using file = new ifcopenshell.File('IFC4');
    using building = file.create('IfcBuilding');
    using wall = file.create('IfcWall');
    using relation = file.create('IfcRelAggregates');

    relation.set('RelatingObject', building);
    relation.set('RelatedObjects', [wall]);

    // f[16] in f.get_inverse(f[15])
    expect([...file.getInverse(wall)].map(entity => entity.id())).toContain(relation.id());
    expect(wall.inverse('Decomposes').map(entity => entity.id())).toContain(relation.id());

    // f.traverse(f[35], 1) / f.traverse(f[35])
    const shallow = listEntities(file.traverse(relation, 1));
    const deep = listEntities(file.traverse(relation, -1));
    expect(deep.length).toBeGreaterThanOrEqual(shallow.length);
    expect(deep.map(entity => entity.id())).toContain(wall.id());

    // f[288].ConnectedTo[0].RelatingElement = f[340], then f[288].ConnectedTo == ()
    using otherWall = file.create('IfcWall');
    using connects = file.create('IfcRelConnectsPathElements');
    connects.set('RelatingElement', wall);
    expect(wall.inverse('ConnectedTo').map(entity => entity.id())).toEqual([connects.id()]);
    connects.set('RelatingElement', otherWall);
    expect(wall.inverse('ConnectedTo')).toEqual([]);
    expect(otherWall.inverse('ConnectedTo').map(entity => entity.id())).toEqual([connects.id()]);
  });
});
