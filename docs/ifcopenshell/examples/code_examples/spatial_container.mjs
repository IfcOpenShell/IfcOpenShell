// This file was generated with the assistance of an AI coding tool.
//
// Code examples (JavaScript): finding the spatial container of an element.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: spatial_container <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
const walls = model.byType('IfcWall');
for (const wall of walls) {
  const relations = wall.ContainedInStructure;
  for (const relation of relations) {
    const container = relation.RelatingStructure;
    if (container instanceof ifcopenshell.EntityInstance) {
      console.log(wall.id(), container.isA(), container.Name);
    }
  }
}
// end::example

const contained = walls.some((wall) => wall.ContainedInStructure.some(
  (relation) => relation.RelatingStructure?.Name === 'Level 01',
));
if (!contained) {
  console.error('expected the wall to be contained in Level 01');
  model.dispose();
  process.exit(1);
}
model.dispose();
