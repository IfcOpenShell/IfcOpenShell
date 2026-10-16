// This file was generated with the assistance of an AI coding tool.
//
// Schema querying (JavaScript): enumerations and select types.

import * as ifcopenshell from 'ifcopenshell';

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const ifc4 = ifcopenshell.schemaByName('IFC4');

// tag::example
const wallTypes = ifc4.declarationByName('IfcWallTypeEnum').asEnumerationType();
// 'MOVABLE', 'PARAPET', 'PARTITIONING', 'PLUMBINGWALL', ...
console.log(wallTypes.enumerationItems());

const units = ifc4.declarationByName('IfcUnit').asSelectType();
// 'IfcDerivedUnit', 'IfcMonetaryUnit', 'IfcNamedUnit'
console.log(units.selectListNames());
// end::example

const expected = wallTypes.enumerationItems().includes('PARAPET')
  && units.selectListNames().includes('IfcNamedUnit');
if (!expected) {
  console.error('unexpected enumeration or select declaration');
  process.exit(1);
}
