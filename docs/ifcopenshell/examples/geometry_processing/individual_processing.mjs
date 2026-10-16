// This file was generated with the assistance of an AI coding tool.
//
// Geometry processing (JavaScript): one product.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: individual_processing <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
// tag::setup
import * as geom from 'ifcopenshell/geom';

// The mapping interprets IFC representations, the kernel does the geometry.
await runtime.loadPlugin('mapping', 'ifc4');
await runtime.loadPlugin('kernel', 'manifold');
// end::setup
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
const settings = new geom.Settings();
settings.set('weld-vertices', false);

// The first wall that has a shape.
const wall = model.byType('IfcWall').find(
  (element) => element.Representation instanceof ifcopenshell.EntityInstance,
);
if (!wall) {
  throw new Error('No wall with a representation');
}

const shape = geom.createShape(settings, wall, undefined, 'manifold');
if (!shape) {
  throw new Error('Shape creation failed');
}

// The GUID and the STEP ID of the element we processed.
console.log(shape.guid(), shape.id());

// A column-major 4x4 matrix, with the location and rotation of the element.
const matrix = shape.transformationBuffer(Float64Array);
console.log(matrix);

const triangulation = shape.asTriangulationElement();
const geometry = triangulation?.geometry();
if (!geometry) {
  throw new Error('Triangulation failed');
}

// X Y Z of vertices in a flattened list, e.g. [v1x, v1y, v1z, v2x, ...]
// These are local to the matrix above, unless use-world-coords is set.
const verts = geometry.vertsBuffer(Float32Array);

// Indices of vertices per triangle, e.g. [f1v1, f1v2, f1v3, f2v1, ...]
const faces = geometry.facesBuffer(Uint32Array);

console.log(verts.length / 3, 'vertices,', faces.length / 3, 'triangles');

// The buffers are copies, so the native objects can be released already.
geometry.destroy();
triangulation.destroy();
shape.destroy();
// end::example

if (verts.length === 0 || faces.length === 0) {
  console.error('expected triangulated vertices');
  model.dispose();
  process.exit(1);
}
model.dispose();
