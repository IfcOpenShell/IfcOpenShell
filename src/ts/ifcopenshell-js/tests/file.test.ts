import { beforeAll, expect, it } from 'vitest';
import * as ifcopenshell from 'ifcopenshell';
import { IfcOpenshellFile, IfcOpenshellInstance } from '@ifcopenshell/wasm/api';
import { createInstance, describeOrSkip } from './_helper.js';

describeOrSkip('file and entity_instance', () => {
  let runtime: ifcopenshell.IfcOpenShell;
  beforeAll(async () => {
    runtime = await createInstance();
    await runtime.loadPlugin('schema', 'ifc4');
  });

  it('creates and queries files using public classes', () => {
    using file = new ifcopenshell.file('IFC4');
    using wall = file.createEntity('IfcWall', { name: 'Wall' });
    expect(file).toBeInstanceOf(IfcOpenshellFile);
    expect(wall).toBeInstanceOf(IfcOpenshellInstance);
    expect(wall).toBeInstanceOf(ifcopenshell.entity_instance);
    expect(wall.get('Name')).toBe('Wall');
    expect(wall.getArgumentByName('Name')).toBe('Wall');
    expect(file.headerInfo()?.schemas).toEqual(['IFC4']);
    using fetched = file.get(wall.id());
    expect(fetched?.get('Name')).toBe('Wall');
    expect(file.text()).toContain('IFCWALL');
    file.dispose();
    expect(() => file.schemaName()).toThrow('disposed');
  });

  it('converts references and aggregates in the binding', () => {
    using file = new ifcopenshell.file('IFC4');
    using building = file.createEntity('IfcBuilding');
    using wall = file.createEntity('IfcWall');
    using relation = file.createEntity('IfcRelAggregates');
    relation.set('RelatingObject', building);
    relation.set('RelatedObjects', [wall]);
    const parent = relation.get('RelatingObject') as ifcopenshell.entity_instance;
    const children = relation.get('RelatedObjects') as ifcopenshell.entity_instance[];
    try {
      expect(parent).toBeInstanceOf(ifcopenshell.entity_instance);
      expect(parent.id()).toBe(building.id());
      expect(children.map(child => child.id())).toEqual([wall.id()]);
    } finally { parent.dispose(); children.forEach(child => child.dispose()); }
    for (const entities of [
      file.all('IfcWall'),
      file.inverses(wall),
      wall.inverse('Decomposes'),
      file.traverseEntities(relation),
    ]) {
      try {
        expect(entities.length).toBeGreaterThan(0);
        for (const entity of entities) {
          expect(entity).toBeInstanceOf(ifcopenshell.entity_instance);
          expect(entity.isA()).toBe(entity.className(false));
          expect(entity.id()).toBeGreaterThan(0);
        }
      } finally { entities.forEach(entity => entity.dispose()); }
    }
    using other = new ifcopenshell.file('IFC4');
    using otherWall = other.createEntity('IfcWall');
    expect(() => relation.set('RelatedObjects', [otherWall])).toThrow('different IFC file');
    relation.set('RelatedObjects', []);
    expect(relation.get('RelatedObjects')).toEqual([]);
  });

  it('converts scalars, enums, logicals, nulls and nested arrays', () => {
    using file = new ifcopenshell.file('IFC4');
    using wall = file.createEntity('IfcWall');
    wall.set('PredefinedType', 'STANDARD');
    expect(wall.get('PredefinedType')).toBe('STANDARD');
    expect(() => wall.set('PredefinedType', 'NOT_A_VALUE')).toThrow();
    wall.set('Name', null);
    expect(wall.get('Name')).toBeNull();
    expect(() => wall.set('Name', 123)).toThrow();
    using point = file.createEntity('IfcCartesianPoint');
    point.set('Coordinates', [1, 2.5, 3]);
    expect(point.get('Coordinates')).toEqual([1, 2.5, 3]);
    using points = file.createEntity('IfcCartesianPointList3D');
    points.set('CoordList', [[1, 2, 3], [4, 5, 6]]);
    expect(points.get('CoordList')).toEqual([[1, 2, 3], [4, 5, 6]]);
    using triangulation = file.createEntity('IfcTriangulatedFaceSet');
    triangulation.set('CoordIndex', [[1, 2, 3]]);
    expect(triangulation.get('CoordIndex')).toEqual([[1, 2, 3]]);
    triangulation.set('Closed', true);
    expect(triangulation.get('Closed')).toBe(true);
    expect(() => triangulation.set('Closed', 1)).toThrow();
  });

  it('converts binary arrays and nested entity references and preserves derived markers', () => {
    using file = new ifcopenshell.file('IFC4');
    using point = file.createEntity('IfcCartesianPoint');
    point.set('Coordinates', [0, 0, 0]);
    using surface = file.createEntity('IfcBSplineSurfaceWithKnots');
    surface.set('ControlPointsList', [[point, point], [point, point]]);
    const rows = surface.get('ControlPointsList') as ifcopenshell.entity_instance[][];
    try {
      expect(rows.map(row => row.map(item => item.id()))).toEqual([[point.id(), point.id()], [point.id(), point.id()]]);
    } finally { rows.flat().forEach(item => item.dispose()); }
    using texture = file.createEntity('IfcPixelTexture');
    texture.set('Pixel', ['0101', '1111']);
    expect(texture.get('Pixel')).toEqual(['0101', '1111']);
    expect(() => texture.set('Pixel', ['invalid'])).toThrow();
    using unit = file.createEntity('IfcSIUnit');
    unit.set('Dimensions', null);
    expect(unit.get('Dimensions')).toBeNull();
    expect(unit.toString(true)).toContain('IFCSIUNIT(*,');
  });

  it('preserves int64 values, logical UNKNOWN and inline typed values', () => {
    const text = `ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('','',(),(),'','','');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
#1=IFCPROPERTYSINGLEVALUE('logical',$,IFCLOGICAL(.U.),$);
#2=IFCPROPERTYSINGLEVALUE('integer',$,IFCINTEGER(9007199254740993),$);
ENDSEC;
END-ISO-10303-21;`;
    using file = ifcopenshell.open(new TextEncoder().encode(text));
    using property = file.get(1)!;
    using logical = property.get('NominalValue') as ifcopenshell.entity_instance;
    expect(logical.get(0)).toBe('UNKNOWN');
    logical.set(0, false);
    expect(logical.get(0)).toBe(false);
    logical.set(0, 'UNKNOWN');
    expect(logical.get(0)).toBe('UNKNOWN');
    using integerProperty = file.get(2)!;
    using integer = integerProperty.get('NominalValue') as ifcopenshell.entity_instance;
    expect(integer.get(0)).toBe(9007199254740993n);
    integer.set(0, -9007199254740993n);
    expect(integer.get(0)).toBe(-9007199254740993n);
    integer.set(0, 42);
    expect(integer.get(0)).toBe(42);
    expect(() => integer.set(0, 1.5)).toThrow();
    expect(() => integer.set(0, 1n << 63n)).toThrow();
  });
});
