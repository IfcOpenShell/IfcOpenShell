// This file was generated with the assistance of an AI coding tool.
//
// Code examples (JavaScript): listing every entity.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: all_entities <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
for (const id of model.ids) {
  const entity = model.byId(id);
  console.log(entity.id(), entity.isA());
  if (entity.attributes().includes('Name')) {
    console.log(entity.Name);
  }
}
// end::example

if (model.ids.length === 0) {
  console.error('expected entities in the model');
  model.dispose();
  process.exit(1);
}
model.dispose();
