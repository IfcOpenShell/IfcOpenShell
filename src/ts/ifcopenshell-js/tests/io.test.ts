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
import { createInstance, describeOrSkip } from './_helper.js';

/** Minimal IFC4 sample with a wall, a point and a typed property value. */
const SAMPLE = `ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('basic-io.ifc','2026-01-01T00:00:00',(''),(''),'','','');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
#1=IFCCARTESIANPOINT((0.,0.,0.));
#2=IFCWALL('0j$1cJ2rL4$v8Z1y4X9w2',$,'Wall',$,$,$,$,$,$);
#3=IFCPROPERTYSINGLEVALUE('FireRating',$,IFCLABEL('F30'),$);
ENDSEC;
END-ISO-10303-21;`;

const WALL_GUID = '0j$1cJ2rL4$v8Z1y4X9w2';

function openSample(): ifcopenshell.file {
  return ifcopenshell.open(new TextEncoder().encode(SAMPLE));
}

describeOrSkip('basic I/O', () => {
  let runtime: ifcopenshell.IfcOpenShell;
  beforeAll(async () => {
    runtime = await createInstance();
    await runtime.loadPlugin('schema', 'ifc4');
  });

  it('opens a model and answers the by_id, by_guid and by_type queries', () => {
    using file = openSample();
    expect(file.schemaName()).toBe('IFC4');
    expect(file.entityCount).toBe(3);
    expect(file.ids).toEqual([1, 2, 3]);

    // f[1].is_a("IfcCartesianPoint") / f.by_id(1)
    using point = file.get(1)!;
    expect(point.type).toBe('IfcCartesianPoint');
    expect(point.className(false)).toBe('IfcCartesianPoint');

    // f["28pa2ppDf1IA$BaQrvAf48"].is_a("IfcProject") / f.by_guid(...)
    try {
      console.log('byGuid raw:', file.byGuid(WALL_GUID));
    } catch (error) {
      console.log('byGuid threw:', (error as Error).message);
    }
    const wall = file.find(WALL_GUID)!;
    expect(wall?.type).toBe('IfcWall');
    expect(wall.id()).toBe(2);

    // f.by_type("IfcProject")
    expect(file.all('IfcCartesianPoint').map(entity => entity.id())).toEqual([1]);

    // is_a() reports the declaration, so a declared supertype only matches when
    // subtypes are requested; they are included by default.
    expect(file.all('IfcRepresentationItem', { includeSubtypes: false })).toEqual([]);
    expect(file.all('IfcRepresentationItem').map(entity => entity.id())).toEqual([1]);
  });

  it('reads attributes, typed values and inverses', () => {
    using file = openSample();
    using wall = file.get(2)!;
    using property = file.get(3)!;

    // f[22].Id == "" / f[22].Addresses is None
    expect(wall.get('Name')).toBe('Wall');
    expect(wall.get('Description')).toBeNull();

    // prop.NominalValue.wrappedValue: the inline IfcLabel carries the value.
    using nominal = property.get('NominalValue') as ifcopenshell.entity_instance;
    expect(nominal.get(0)).toBe('F30');

    // get_info() returns the id, type and decoded forward attributes.
    const info = wall.getInfo();
    expect(info.id).toBe(2);
    expect(info.type).toBe('IfcWall');
    expect(info.attributes.Name).toBe('Wall');
    expect(Object.keys(info.attributes)).toContain('Name');

    // Inverse attributes of a wall that nothing points at yet.
    expect(wall.inverseAttributes()).toContain('HasAssociations');
    expect(wall.inverse('HasAssociations')).toEqual([]);
  });

  it('serializes and reopens with the same queries answered', () => {
    using file = openSample();
    using wall = file.get(2)!;

    // f.write("output.ifc") then reading the file back.
    const text = file.text();
    expect(text).toContain('IFCWALL');
    expect(text).toContain('Wall');

    using reopened = ifcopenshell.open(new TextEncoder().encode(text));
    expect(reopened.schemaName()).toBe('IFC4');
    expect(reopened.entityCount).toBe(file.entityCount);

    const reopenedWall = reopened.find(WALL_GUID);
    console.log('GUID lookup:', reopenedWall?.type, 'count:', reopened.entityCount, 'guid in text:', text.includes(WALL_GUID));
    expect(reopenedWall?.type).toBe('IfcWall');
    expect(reopenedWall.get('Name')).toBe('Wall');
  });

  it('creates entities, mutates attributes and writes valid SPF', () => {
    using file = new ifcopenshell.file('IFC4');
    expect(file.schemaName()).toBe('IFC4');

    // f.createIfcCartesianPoint((0.0, 0.0, 0.0))
    using point = file.createEntity('IfcCartesianPoint');
    point.set('Coordinates', [0, 0, 0]);
    expect(point.type).toBe('IfcCartesianPoint');
    expect(point.get('Coordinates')).toEqual([0, 0, 0]);

    using wall = file.createEntity('IfcWall', { name: 'Wall' });
    // f[22].Id = "123" / "123" in str(f[22])
    wall.set('Description', '123');
    expect(wall.text(true)).toContain('123');
    expect(wall.get('Description')).toBe('123');
    wall.unset('Description');
    expect(wall.get('Description')).toBeNull();
    expect(wall.text(true)).not.toContain('123');

    const text = file.text();
    expect(text).toContain('IFCWALL');

    // The ids and the entity count agree on what the file holds.
    expect(file.ids.length).toBe(file.entityCount);
    expect(file.maxId).toBe(Math.max(...file.ids));
  });

  it('keeps inverses and traversals consistent when references move', () => {
    using file = new ifcopenshell.file('IFC4');
    using building = file.createEntity('IfcBuilding');
    using wall = file.createEntity('IfcWall');
    using relation = file.createEntity('IfcRelAggregates');

    relation.set('RelatingObject', building);
    relation.set('RelatedObjects', [wall]);

    // f[16] in f.get_inverse(f[15])
    expect(file.inverses(wall).map(entity => entity.id())).toContain(relation.id());
    expect(wall.inverse('Decomposes').map(entity => entity.id())).toContain(relation.id());

    // f.traverse(f[35], 1) / f.traverse(f[35])
    const shallow = file.traverseEntities(relation, { maxDepth: 1 });
    const deep = file.traverseEntities(relation);
    expect(deep.length).toBeGreaterThanOrEqual(shallow.length);
    expect(deep.map(entity => entity.id())).toContain(wall.id());

    // f[288].ConnectedTo[0].RelatingElement = f[340], then f[288].ConnectedTo == ()
    using otherWall = file.createEntity('IfcWall');
    using connects = file.createEntity('IfcRelConnectsPathElements');
    connects.set('RelatingElement', wall);
    expect(wall.inverse('ConnectedTo').map(entity => entity.id())).toEqual([connects.id()]);
    connects.set('RelatingElement', otherWall);
    expect(wall.inverse('ConnectedTo')).toEqual([]);
    expect(otherWall.inverse('ConnectedTo').map(entity => entity.id())).toEqual([connects.id()]);
  });
});
