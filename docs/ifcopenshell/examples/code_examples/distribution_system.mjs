// This file was generated with the assistance of an AI coding tool.
//
// Code examples (JavaScript): get the distribution system of an element.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: distribution_system <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
for (const pipe of model.byType('IfcPipeSegment')) {
  // Elements may be assigned to multiple systems simultaneously, such as
  // electrical, hydraulic, etc
  for (const relation of pipe.HasAssignments) {
    const isSystem = relation.isA('IfcRelAssignsToGroup')
      && relation.RelatingGroup.isA('IfcSystem');
    if (isSystem) {
      console.log('This pipe is part of', relation.RelatingGroup.Name);
    }
  }
}
// end::example

model.dispose();
