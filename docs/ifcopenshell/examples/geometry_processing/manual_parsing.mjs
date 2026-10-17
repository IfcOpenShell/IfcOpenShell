// This file was generated with the assistance of an AI coding tool.
//
// Geometry processing (JavaScript): reading an extrusion depth directly.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: manual_parsing <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
for (const solid of model.byType('IfcExtrudedAreaSolid')) {
  console.log(solid.Depth);
}
// end::example

const depths = model.byType('IfcExtrudedAreaSolid').map((solid) => solid.Depth);
if (!depths.some((depth) => typeof depth === 'number' && depth > 0)) {
  console.error('expected an extrusion depth');
  model.dispose();
  process.exit(1);
}
model.dispose();
