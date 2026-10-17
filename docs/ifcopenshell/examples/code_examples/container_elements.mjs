// This file was generated with the assistance of an AI coding tool.
//
// Code examples (JavaScript): get all elements in a container.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: container_elements <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
for (const storey of model.byType('IfcBuildingStorey')) {
  const elements = storey.ContainsElements.flatMap(
    (relation) => relation.RelatedElements,
  );
  console.log(`There are ${elements.length} located on storey ${storey.Name}`);
  for (const element of elements) {
    console.log(element.Name);
  }
}
// end::example

const storey = model.byType('IfcBuildingStorey')[0];
const contained = storey.ContainsElements.flatMap(
  (relation) => relation.RelatedElements,
);
if (contained.length !== 1 || contained[0].Name !== 'Wall 01') {
  console.error('expected Wall 01 on the storey');
  model.dispose();
  process.exit(1);
}

model.dispose();
