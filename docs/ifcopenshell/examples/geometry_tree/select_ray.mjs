// This file was generated with the assistance of an AI coding tool.
//
// Geometry tree (JavaScript): selecting along a ray.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';

const input = process.argv[2];
if (!input) {
  console.error('usage: select_ray <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
await runtime.loadPlugin('mapping', 'ifc4');
await runtime.loadPlugin('kernel', 'opencascade');
await runtime.loadPlugin('tree', 'opencascade.brep');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
const settings = new geom.Settings();
const tree = runtime.raw.geom.createTree('opencascade.brep');
if (!tree) {
  throw new Error('Geometry tree was not created');
}
tree.addFile(model, settings);

// tag::select
// A ray from (-2, 0, 0.5), along the positive X axis, 100 metres long.
const intersections = tree.selectRay(-2, 0, 0.5, 1, 0, 0, 100);
const count = tree.rayIntersectionCount(intersections);
for (let index = 0; index < count; index += 1) {
  const intersection = tree.rayIntersectionAt(intersections, index);
  console.log(
    intersection.instance().id(),
    intersection.distance(),
    intersection.position(),
    intersection.normal(),
  );
}
// end::select
// end::example

model.dispose();
