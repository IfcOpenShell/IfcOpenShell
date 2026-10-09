import { beforeAll, expect, it } from 'vitest';
import * as ifcopenshell from 'ifcopenshell';
import { IfcOpenshellFile, IfcOpenshellInstance } from '@ifcopenshell/wasm/api';
import { createInstance, describeOrSkip } from './_helper.js';

describeOrSkip('file and EntityInstance', () => {
  let runtime: ifcopenshell.IfcOpenShell;
  beforeAll(async () => {
    runtime = await createInstance();
    await runtime.loadPlugin('schema', 'ifc4');
  });

  it('returns Python-compatible flat info and applies options recursively', () => {
    using file = new ifcopenshell.File('IFC4');
    const building = file.create('IfcBuilding', { Name: 'Building', Description: 'Ignored' });
    const wall = file.create('IfcWall', { Name: 'Wall' });
    const relation = file.create('IfcRelAggregates', { RelatingObject: building, RelatedObjects: [wall, wall] });
    const info = relation.getInfo();
    expect(info.id).toBe(relation.id());
    expect(info.type).toBe('IfcRelAggregates');
    expect(info).not.toHaveProperty('attributes');
    const parent = info.RelatingObject as ifcopenshell.EntityInstance;
    const children = info.RelatedObjects as ifcopenshell.EntityInstance[];
    {
      expect(parent.id()).toBe(building.id());
      expect(children.map(child => child.id())).toEqual([wall.id(), wall.id()]);
    }

    const recursive = relation.getInfo({ recursive: true, includeIdentifier: false, ignore: ['Description'] });
    expect(recursive).not.toHaveProperty('id');
    expect(recursive.RelatingObject).toMatchObject({ type: 'IfcBuilding', Name: 'Building' });
    expect(recursive.RelatingObject).not.toHaveProperty('id');
    expect(recursive.RelatingObject).not.toHaveProperty('Description');
    expect(recursive.RelatedObjects).toEqual([
      expect.objectContaining({ type: 'IfcWall', Name: 'Wall' }),
      expect.objectContaining({ type: 'IfcWall', Name: 'Wall' }),
    ]);
    expect(wall.get('Name')).toBe('Wall');
    const custom = relation.getInfo({ recursive: true, returnType: info => new Map(Object.entries(info)) });
    expect(custom).toBeInstanceOf(Map);
    expect(custom.get('RelatingObject')).toBeInstanceOf(Map);
  });

  it('expands distinct inline typed values independently of their zero ids', () => {
    using file = ifcopenshell.open(new TextEncoder().encode(`ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('','',(),(),'','','');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
#1=IFCPROPERTYLISTVALUE('values',$,(IFCLABEL('first'),IFCLABEL('second')),$);
ENDSEC;
END-ISO-10303-21;`));
    const property = file.byId(1);
    expect(property.getInfo({ recursive: true }).ListValues).toEqual([
      { id: 0, type: 'IfcLabel', wrappedValue: 'first' },
      { id: 0, type: 'IfcLabel', wrappedValue: 'second' },
    ]);
  });

  it('creates arbitrary attributes and removes a failed partial entity', () => {
    using file = new ifcopenshell.File('IFC4');
    const point = file.create('IfcCartesianPoint', { Coordinates: [1, 2, 3] });
    expect(point.get('Coordinates')).toEqual([1, 2, 3]);
    const wall = file.create('IfcWall', { Name: 'Wall', Description: 'Description', Tag: 'W1', PredefinedType: 'STANDARD' });
    expect(wall.getInfo()).toMatchObject({ Name: 'Wall', Description: 'Description', Tag: 'W1', PredefinedType: 'STANDARD' });
    const before = file.ids;
    expect(() => file.create('IfcWall', { Name: 'Partial', MissingAttribute: 'invalid' })).toThrow();
    expect(file.ids).toEqual(before);
    expect(() => file.create('IfcWall', { Name: 123 })).toThrow();
    expect(file.ids).toEqual(before);
  });

  it('deduplicates inverses and preserves duplicates and attribute indices on request', () => {
    using file = new ifcopenshell.File('IFC4');
    const wall = file.create('IfcWall');
    const relation = file.create('IfcRelConnectsPathElements', { RelatingElement: wall, RelatedElement: wall });
    const unique = file.getInverse(wall);
    {
      expect(unique).toBeInstanceOf(Set);
      expect([...unique].map(item => item.id())).toEqual([relation.id()]);
      expect(unique.has(relation)).toBe(true);
      const fetched = file.byId(relation.id());
      expect(unique.has(fetched)).toBe(true);
      expect(unique.has(wall)).toBe(false);
    }
    const duplicates = file.getInverse(wall, { allowDuplicate: true });
    expect(duplicates.map(item => item.id())).toEqual([relation.id(), relation.id()]);
    const indexed = file.getInverse(wall, { allowDuplicate: true, withAttributeIndices: true });
    {
      expect(indexed.map(([item, index]) => [item.id(), index])).toEqual([
        [relation.id(), relation.attributeIndex('RelatingElement')],
        [relation.id(), relation.attributeIndex('RelatedElement')],
      ]);
    }
    expect(() => file.getInverse(wall, { withAttributeIndices: true })).toThrow('requires allowDuplicate');
  });

  it('separates the schema family, full identifier and schema declaration', async () => {
    await runtime.loadPlugin('schema', 'ifc4x3_add2');
    using file = new ifcopenshell.File('IFC4X3_ADD2');
    expect(file.schema()).toBe('IFC4X3');
    expect(file.schemaIdentifier()).toBe('IFC4X3_ADD2');
    const schema = ifcopenshell.schemaByName(file.schemaIdentifier())!;
    expect(schema.name()).toBe('IFC4X3_ADD2');
    const declaration = schema.declarationByName('IfcWall')!;
    expect(declaration.name()).toBe('IfcWall');
    expect(file.byId).toBe(IfcOpenshellFile.prototype.byId);
    expect(file.byGuid).toBe(IfcOpenshellFile.prototype.byGuid);
    expect(file.byType).toBe(IfcOpenshellFile.prototype.byType);
    for (const name of ['get', 'find', 'all', 'isValid', 'headerInfo', 'text', 'traverseEntities', 'unit']) {
      expect(name in file).toBe(false);
    }
  });

  it('creates and queries files using public classes', () => {
    using file = new ifcopenshell.File('IFC4');
    const wall = file.create('IfcWall', { Name: 'Wall' });
    expect(file).toBeInstanceOf(IfcOpenshellFile);
    expect(wall).toBeInstanceOf(IfcOpenshellInstance);
    expect(wall).toBeInstanceOf(ifcopenshell.EntityInstance);
    expect(wall.get('Name')).toBe('Wall');
    expect(wall.getArgumentByName('Name')).toBe('Wall');
    const header = file.header()!;
    const schema = header.fileSchema();
    expect(schema.schemaIdentifiers()).toEqual(['IFC4']);
    const fetched = file.byId(wall.id());
    expect(fetched?.get('Name')).toBe('Wall');
    expect(file.toString()).toContain('IFCWALL');
    file.dispose();
    expect(() => file.schema()).toThrow('disposed');
  });

  it('returns ordinary arrays and reserves Disposable for model owners', () => {
    using file = new ifcopenshell.File('IFC4');
    const wall = file.create('IfcWall');
    expect('dispose' in wall).toBe(false);
    expect(Symbol.dispose in wall).toBe(false);
    expect(Symbol.dispose in file).toBe(true);
    for (const items of [
      file.byType('IfcWall'),
      file.byTypeExclSubtypes('IfcWall'),
      file.traverse(wall, -1),
      file.traverseBreadthFirst(wall, -1),
      wall.inverse('Decomposes'),
    ]) {
      expect(Array.isArray(items)).toBe(true);
      expect(Symbol.dispose in items).toBe(false);
      for (const item of items) expect(item).toBeInstanceOf(ifcopenshell.EntityInstance);
    }
  });

  it('converts references and aggregates in the binding', () => {
    using file = new ifcopenshell.File('IFC4');
    const building = file.create('IfcBuilding');
    const wall = file.create('IfcWall');
    const relation = file.create('IfcRelAggregates');
    relation.set('RelatingObject', building);
    relation.set('RelatedObjects', [wall]);
    const parent = relation.get('RelatingObject') as ifcopenshell.EntityInstance;
    const children = relation.get('RelatedObjects') as ifcopenshell.EntityInstance[];
    {
      expect(parent).toBeInstanceOf(ifcopenshell.EntityInstance);
      expect(parent.id()).toBe(building.id());
      expect(children.map(child => child.id())).toEqual([wall.id()]);
    }
    for (const entities of [
      file.byType('IfcWall'),
      [...file.getInverse(wall)],
      wall.inverse('Decomposes'),
      file.traverse(relation, -1),
    ]) {
      {
        expect(entities.length).toBeGreaterThan(0);
        for (const entity of entities) {
          expect(entity).toBeInstanceOf(ifcopenshell.EntityInstance);
          expect(entity.isA()).toBe(entity.className(false));
          expect(entity.id()).toBeGreaterThan(0);
        }
      }
    }
    using other = new ifcopenshell.File('IFC4');
    const otherWall = other.create('IfcWall');
    expect(() => relation.set('RelatedObjects', [otherWall])).toThrow('different IFC file');
    relation.set('RelatedObjects', []);
    expect(relation.get('RelatedObjects')).toEqual([]);
  });

  it('converts scalars, enums, logicals, nulls and nested arrays', () => {
    using file = new ifcopenshell.File('IFC4');
    const wall = file.create('IfcWall');
    wall.set('PredefinedType', 'STANDARD');
    expect(wall.get('PredefinedType')).toBe('STANDARD');
    expect(() => wall.set('PredefinedType', 'NOT_A_VALUE')).toThrow();
    wall.set('Name', null);
    expect(wall.get('Name')).toBeNull();
    expect(() => wall.set('Name', 123)).toThrow();
    const point = file.create('IfcCartesianPoint');
    point.set('Coordinates', [1, 2.5, 3]);
    expect(point.get('Coordinates')).toEqual([1, 2.5, 3]);
    const points = file.create('IfcCartesianPointList3D');
    points.set('CoordList', [[1, 2, 3], [4, 5, 6]]);
    expect(points.get('CoordList')).toEqual([[1, 2, 3], [4, 5, 6]]);
    const triangulation = file.create('IfcTriangulatedFaceSet');
    triangulation.set('CoordIndex', [[1, 2, 3]]);
    expect(triangulation.get('CoordIndex')).toEqual([[1, 2, 3]]);
    triangulation.set('Closed', true);
    expect(triangulation.get('Closed')).toBe(true);
    expect(() => triangulation.set('Closed', 1)).toThrow();
  });

  it('converts binary arrays and nested entity references and preserves derived markers', () => {
    using file = new ifcopenshell.File('IFC4');
    const point = file.create('IfcCartesianPoint');
    point.set('Coordinates', [0, 0, 0]);
    const surface = file.create('IfcBSplineSurfaceWithKnots');
    surface.set('ControlPointsList', [[point, point], [point, point]]);
    const rows = surface.get('ControlPointsList') as ifcopenshell.EntityInstance[][];
    try {
      expect(rows.map(row => row.map(item => item.id()))).toEqual([[point.id(), point.id()], [point.id(), point.id()]]);
    } finally { rows.flat().forEach(item => item.destroy()); }
    const texture = file.create('IfcPixelTexture');
    texture.set('Pixel', ['0101', '1111']);
    expect(texture.get('Pixel')).toEqual(['0101', '1111']);
    expect(() => texture.set('Pixel', ['invalid'])).toThrow();
    const unit = file.create('IfcSIUnit');
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
    const property = file.byId(1)!;
    const logical = property.get('NominalValue') as ifcopenshell.EntityInstance;
    expect(logical.get(0)).toBe('UNKNOWN');
    logical.set(0, false);
    expect(logical.get(0)).toBe(false);
    logical.set(0, 'UNKNOWN');
    expect(logical.get(0)).toBe('UNKNOWN');
    const integerProperty = file.byId(2)!;
    const integer = integerProperty.get('NominalValue') as ifcopenshell.EntityInstance;
    expect(integer.get(0)).toBe(9007199254740993n);
    integer.set(0, -9007199254740993n);
    expect(integer.get(0)).toBe(-9007199254740993n);
    integer.set(0, 42);
    expect(integer.get(0)).toBe(42);
    expect(() => integer.set(0, 1.5)).toThrow();
    expect(() => integer.set(0, 1n << 63n)).toThrow();
  });
});
