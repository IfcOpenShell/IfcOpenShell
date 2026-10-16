// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (JavaScript): opening an IFC file.

// tag::example
import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

// The path is the first command-line argument so this example can be run.
const input = process.argv[2];
if (!input) {
  console.error('usage: load_model <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const bytes = await readFile(input);
const model = ifcopenshell.open(bytes, input);
console.log(model.schema());
// end::example

if (model.schema() !== 'IFC4') {
  console.error(`expected IFC4, got ${model.schema()}`);
  model.dispose();
  process.exit(1);
}
model.dispose();
