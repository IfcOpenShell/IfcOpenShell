// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (JavaScript): reading an entity by STEP id.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: by_id <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::schema
console.log(model.schema());
// end::schema
// tag::example
const entity = model.byId(1);
console.log(entity.id(), entity.isA());
// end::example

if (!entity || entity.isA() !== 'IfcProject' || entity.Name !== 'Hello World') {
  console.error('expected #1 to be the Hello World IfcProject');
  model.dispose();
  process.exit(1);
}
model.dispose();
