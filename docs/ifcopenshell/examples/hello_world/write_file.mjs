// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (JavaScript): editing an attribute and writing the file.

import { readFile, writeFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: write_file <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
const wall = model.byType('IfcWall')[0];
wall.set('Name', 'My new wall name');

// toString() serialises the model as IFC-SPF text.
await writeFile('updated.ifc', model.toString(), 'utf8');
// end::example

const written = await readFile('updated.ifc', 'utf8');
const expected = wall.Name === 'My new wall name'
  && written.includes('My new wall name');
if (!expected) {
  console.error('updated.ifc is missing the new wall name');
  model.dispose();
  process.exit(1);
}
model.dispose();
