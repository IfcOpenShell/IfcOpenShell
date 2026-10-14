// This file was generated with the assistance of an AI coding tool.
//
// Code examples (JavaScript): inverses and forward traversal.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: 06_navigate <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
const entity = model.byId(model.ids[0]);

// Everything that references the entity, as a Set.
const referring = model.getInverse(entity);
console.log('Referenced by:', [...referring].map((item) => item.id()));

// Everything the entity references, one level deep.
const referenced = model.traverse(entity, 1);
console.log('References:', referenced.map((item) => item.id()));
// end::example

if (!entity || referenced.length === 0) {
  console.error('expected forward references from the first entity');
  model.dispose();
  process.exit(1);
}
model.dispose();
