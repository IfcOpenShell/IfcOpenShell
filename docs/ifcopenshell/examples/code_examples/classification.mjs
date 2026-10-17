// This file was generated with the assistance of an AI coding tool.
//
// Code examples (JavaScript): get the classification of an element.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: classification <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
const wall = model.byType('IfcWall')[0];
// Elements may have multiple classification references assigned
for (const relation of wall.HasAssociations) {
  if (!relation.isA('IfcRelAssociatesClassification')) {
    continue;
  }
  const reference = relation.RelatingClassification;
  if (reference.isA('IfcClassificationReference')) {
    // A reference code might be Pr_30_59_99_02
    console.log('The wall has a reference of', reference.Identification);
    // A system might be Uniclass 2015
    console.log('It is part of', reference.ReferencedSource?.Name);
  }
}
// end::example

model.dispose();
