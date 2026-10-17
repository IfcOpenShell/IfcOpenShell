// This file was generated with the assistance of an AI coding tool.
//
// Code examples (JavaScript): get all door occurrences of a type.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: type_occurrences <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
for (const doorType of model.byType('IfcDoorType')) {
  console.log('The door type is', doorType.Name);
  // A type refers to its occurrences through IfcRelDefinesByType.
  const doors = doorType.Types.flatMap((relation) => relation.RelatedObjects);
  console.log(`There are ${doors.length} of this type`);
  for (const door of doors) {
    console.log('The door name is', door.Name);
  }
}
// end::example

model.dispose();
