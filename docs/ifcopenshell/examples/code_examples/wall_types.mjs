// This file was generated with the assistance of an AI coding tool.
//
// Code examples (JavaScript): listing wall types.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: wall_types <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
const types = model.byType('IfcWallType');
for (const type of types) {
  console.log(type.id(), type.Name);
}
// end::example

if (!Array.isArray(types)) {
  console.error('byType did not return an array');
  model.dispose();
  process.exit(1);
}
model.dispose();
