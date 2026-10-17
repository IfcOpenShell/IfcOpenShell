// This file was generated with the assistance of an AI coding tool.
//
// Code examples (JavaScript): reading the project length unit.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: units <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
for (const assignment of model.byType('IfcUnitAssignment')) {
  for (const unit of assignment.Units) {
    const isLengthUnit = unit.isA('IfcSIUnit')
      && unit.UnitType === 'LENGTHUNIT';
    if (isLengthUnit) {
      // For millimetres, the Prefix is MILLI and the Name is METRE.
      console.log(unit.Prefix, unit.Name);
    }
  }
}
// end::example

const lengthUnits = model.byType('IfcSIUnit').filter(
  (unit) => unit.UnitType === 'LENGTHUNIT',
);
if (lengthUnits.length !== 1 || lengthUnits[0].Name !== 'METRE') {
  console.error('expected one metre length unit');
  model.dispose();
  process.exit(1);
}
model.dispose();
