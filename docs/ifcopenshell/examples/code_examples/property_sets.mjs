// This file was generated with the assistance of an AI coding tool.
//
// Code examples (JavaScript): reading property sets.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: property_sets <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
const walls = model.byType('IfcWall');
for (const wall of walls) {
  for (const relation of wall.IsDefinedBy) {
    if (!relation.isA('IfcRelDefinesByProperties')) {
      continue;
    }

    // Quantity sets are skipped, as are sets of property sets.
    const pset = relation.RelatingPropertyDefinition;
    const isPropertySet = pset instanceof ifcopenshell.EntityInstance
      && pset.isA('IfcPropertySet');
    if (!isPropertySet) {
      continue;
    }

    for (const property of pset.HasProperties) {
      if (!property.isA('IfcPropertySingleValue')) {
        continue;
      }
      // Values are typed, such as IfcLabel('2HR'), so unwrap them.
      const value = property.NominalValue;
      const unwrapped = value instanceof ifcopenshell.EntityInstance
        ? value.get(0)
        : value;
      console.log(pset.Name, property.Name, unwrapped);
    }
  }
}
// end::example

const sawRating = walls.some((wall) => wall.IsDefinedBy.some((relation) => {
  const pset = relation.RelatingPropertyDefinition;
  if (!(pset instanceof ifcopenshell.EntityInstance)) {
    return false;
  }
  if (!pset.isA('IfcPropertySet')) {
    return false;
  }
  const properties = pset.HasProperties;
  return Array.isArray(properties) && properties.some((property) => (
    property instanceof ifcopenshell.EntityInstance
    && property.Name === 'FireRating'
    && property.NominalValue instanceof ifcopenshell.EntityInstance
    && property.NominalValue.get(0) === '2HR'
  ));
}));
if (!sawRating) {
  console.error('expected Pset_WallCommon.FireRating = 2HR');
  model.dispose();
  process.exit(1);
}
model.dispose();
