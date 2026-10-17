// This file was generated with the assistance of an AI coding tool.
//
// Geometry creation (JavaScript): a triangulated face set.

import * as ifcopenshell from 'ifcopenshell';

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = new ifcopenshell.File('IFC4');

// tag::example
const points = model.create('IfcCartesianPointList3D', {
  CoordList: [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
});
const mesh = model.create('IfcTriangulatedFaceSet', {
  Coordinates: points,
  Closed: false,
  // One triangle, with one-based indices into the CoordList.
  CoordIndex: [[1, 2, 3]],
});
console.log(mesh.id());
// end::example

const index = mesh.get('CoordIndex');
if (!Array.isArray(index) || index.length !== 1) {
  console.error('expected one triangle');
  model.dispose();
  process.exit(1);
}
model.dispose();
