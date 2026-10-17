// This file was generated with the assistance of an AI coding tool.
//
// Code examples (JavaScript): following an occurrence to its type.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: element_type <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
const walls = model.byType('IfcWall');
for (const wall of walls) {
  const relations = wall.IsTypedBy;
  for (const relation of relations) {
    const type = relation.RelatingType;
    if (type instanceof ifcopenshell.EntityInstance) {
      console.log(wall.Name, type.Name);
    }
  }
}
// end::example

model.dispose();
