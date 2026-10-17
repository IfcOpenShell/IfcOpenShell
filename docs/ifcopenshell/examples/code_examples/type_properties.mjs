// This file was generated with the assistance of an AI coding tool.
//
// Code examples (JavaScript): get the properties of a type.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: type_properties <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
const wall = model.byType('IfcWall')[0];
for (const relation of wall.IsTypedBy) {
  // Property sets of a type are listed by the type itself, with no
  // relationship to unwrap.
  const wallType = relation.RelatingType;
  for (const pset of wallType.HasPropertySets ?? []) {
    console.log(pset.Name);
  }
}
// end::example

model.dispose();
