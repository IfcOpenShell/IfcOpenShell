// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (JavaScript): querying walls.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: 03_walls <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::count
const walls = model.byType('IfcWall');
console.log('Number of walls:', walls.length);
// end::count

// tag::is_a
const wall = walls[0];
console.log(wall.isA()); // 'IfcWall'
console.log(wall.isA('IfcElement')); // true
// end::is_a

// tag::attributes
console.log(wall.get(0)); // The first attribute is the GlobalId
console.log(wall.Name);
// end::attributes

// tag::by_guid
const byGuid = model.byGuid('0EI0MSHbX9gg8Fxwar7lL8');
// end::by_guid

const expected = walls.length === 1
  && wall.Name === 'Wall 01'
  && byGuid.id() === wall.id();
if (!expected) {
  console.error('expected one wall named Wall 01');
  model.dispose();
  process.exit(1);
}
model.dispose();
