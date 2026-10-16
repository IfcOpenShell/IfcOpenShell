// This file was generated with the assistance of an AI coding tool.
//
// Geometry processing (JavaScript): one shape representation.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';

const input = process.argv[2];
if (!input) {
  console.error('usage: representation <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
await runtime.loadPlugin('mapping', 'ifc4');
await runtime.loadPlugin('kernel', 'manifold');
const model = ifcopenshell.open(await readFile(input), input);
const settings = new geom.Settings();

// tag::example
const wall = model.byType('IfcWall').find(
  (element) => element.Representation instanceof ifcopenshell.EntityInstance,
);
if (!wall) {
  throw new Error('No wall with a representation');
}

// Choose the Body representation, rather than the default 3D one.
const body = wall.Representation.Representations.find(
  (representation) => representation.RepresentationIdentifier === 'Body',
);
if (!body) {
  throw new Error('The wall has no Body representation');
}

const shape = geom.createShape(settings, wall, body, 'manifold');
if (shape) {
  console.log(shape.id(), shape.context());
}
// end::example

if (!shape) {
  console.error('shape creation failed');
  model.dispose();
  process.exit(1);
}
shape.destroy();
model.dispose();
