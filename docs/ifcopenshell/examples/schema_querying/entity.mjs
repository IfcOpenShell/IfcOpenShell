// This file was generated with the assistance of an AI coding tool.
//
// Schema querying (JavaScript): entity inheritance and attributes.

import * as ifcopenshell from 'ifcopenshell';

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const ifc4 = ifcopenshell.schemaByName('IFC4');

// tag::example
// A declaration may be an entity, an enumeration, a select, or a defined type.
const ifcwall = ifc4.declarationByName('IfcWall').asEntity();

console.log(ifcwall.isAbstract()); // false
// The supertype, IfcBuildingElement, has 8 attributes
console.log(ifcwall.supertype().attributeCount());
// IfcWallElementedCase and IfcWallStandardCase
console.log(ifcwall.subtypes().length);
// end::example

// tag::attributes
// Only the attributes declared on IfcWall itself
console.log(ifcwall.attributes().map((attribute) => attribute.name()));
// Including the inherited attributes
for (const attribute of ifcwall.allAttributes()) {
  console.log(attribute.name(), attribute.optional());
}
// Inverse attributes
const inverses = ifcwall.allInverseAttributes();
console.log(inverses.map((attribute) => attribute.name()));
// end::attributes

const expected = !ifcwall.isAbstract()
  && ifcwall.supertype().attributeCount() === 8
  && ifcwall.subtypes().length === 2
  && ifcwall.allAttributes().length > ifcwall.attributes().length
  && inverses.length > 0;
if (!expected) {
  console.error('unexpected IfcWall declaration');
  process.exit(1);
}
