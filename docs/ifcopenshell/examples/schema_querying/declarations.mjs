// This file was generated with the assistance of an AI coding tool.
//
// Schema querying (JavaScript): schema declarations.

import * as ifcopenshell from 'ifcopenshell';

const runtime = await ifcopenshell.init();
// tag::example
// The schema plugin has to be loaded, but no model has to be opened.
await runtime.loadPlugin('schema', 'ifc4');
const ifc4 = ifcopenshell.schemaByName('IFC4');

// 'IfcAbsorbedDoseMeasure', 'IfcAccelerationMeasure', 'IfcActionRequest', ...
for (const declaration of ifc4.declarations()) {
  console.log(declaration.name());
}

const ifcwall = ifc4.declarationByName('IfcWall');
// end::example

if (ifcwall?.name() !== 'IfcWall' || ifc4.declarations().length < 100) {
  console.error('expected the IFC4 schema to declare IfcWall');
  process.exit(1);
}
