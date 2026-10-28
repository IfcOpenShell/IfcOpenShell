// This file was generated with the assistance of an AI coding tool.

import { beforeAll, expect, it } from 'vitest';
import * as ifcopenshell from 'ifcopenshell';
import { createInstance, describeOrSkip } from './_helper.js';

describeOrSkip('Python-compatible identity', () => {
  beforeAll(async () => {
    const runtime = await createInstance();
    await runtime.loadPlugin('schema', 'ifc4');
  });

  it('returns one wrapper per entity, like Python equality and hashing', () => {
    using file = new ifcopenshell.File('IFC4');
    const wall = file.create('IfcWall');
    const relation = file.create('IfcRelAggregates', { RelatingObject: wall, RelatedObjects: [wall] });
    expect(file.byId(wall.id())).toBe(wall);
    expect(relation.RelatingObject).toBe(wall);
    expect(new Set([wall, file.byId(wall.id()), ...relation.RelatedObjects]).size).toBe(1);
    expect(file.byType('IfcWall')).toContain(wall);
  });

  it('iterates and indexes attributes like a Python entity', () => {
    using file = new ifcopenshell.File('IFC4');
    const wall = file.create('IfcWall', { Name: 'W' });
    expect([...wall][2]).toBe('W');
    expect(wall[2]).toBe('W');
    wall[2] = 'X';
    expect(wall.Name).toBe('X');
  });

  it('returns the containing File from entity.file()', () => {
    using file = new ifcopenshell.File('IFC4');
    expect(file.create('IfcWall').file()).toBe(file);
  });

  it('downcasts schema declarations like Python', () => {
    const schema = ifcopenshell.schemaByName('IFC4')!;
    const wall = schema.declarationByName('IfcWall') as any;
    expect(wall.isAbstract()).toBe(false);
    expect(wall.supertype().name()).toBe('IfcBuildingElement');
    expect(wall.subtypes().map((d: any) => d.name())).toContain('IfcWallStandardCase');
    using file = new ifcopenshell.File('IFC4');
    expect((file.create('IfcWall').declaration() as any).supertype().name()).toBe('IfcBuildingElement');
    const attribute = (name: string, index: number) => (schema.declarationByName(name) as any).attributeByIndex(index);
    expect(String(attribute('IfcWall', 2).typeOfAttribute())).toBe('<type IfcLabel: <string>>');
    expect(String(attribute('IfcPolyline', 0).typeOfAttribute())).toBe('<list [?:?] of <entity IfcCartesianPoint>>');
    expect(String(attribute('IfcSurfaceStyle', 1).typeOfAttribute())).toBe('<enumeration IfcSurfaceSide: (POSITIVE, NEGATIVE, BOTH)>');
    expect(attribute('IfcWall', 2)).toBeInstanceOf(ifcopenshell.wrapper.IfcOpenshellAttribute);
  });

  it('creates entities from positional attributes', () => {
    using file = new ifcopenshell.File('IFC4');
    const unit = file.create('IfcMonetaryUnit', ['USD']);
    expect(unit.Currency).toBe('USD');
  });

  it('accepts typed values created in another file, like Python', () => {
    using file = new ifcopenshell.File('IFC4');
    using other = new ifcopenshell.File('IFC4');
    const property = file.create('IfcPropertySingleValue', { Name: 'x' });
    property.NominalValue = other.create('IfcLabel', ['hi']);
    expect(property.NominalValue.wrappedValue).toBe('hi');
    property.set('NominalValue', other.create('IfcReal', [2.5]));
    expect(property.NominalValue.wrappedValue).toBe(2.5);
  });

  it('round-trips GlobalIds like ifcopenshell.guid', () => {
    expect(ifcopenshell.guid.compress('0ef7c3a5-e7bb-4b2c-8d1f-6a2c3e4f5a6b')).toBe('0EzyEbvxjBB8qVQYm_Jrfh');
    expect(ifcopenshell.guid.expand('0EzyEbvxjBB8qVQYm_Jrfh')).toBe('0ef7c3a5e7bb4b2c8d1f6a2c3e4f5a6b');
    expect(ifcopenshell.guid.new()).toMatch(/^[0-3][0-9A-Za-z_$]{21}$/);
  });
});
