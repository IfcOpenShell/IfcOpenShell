// This file was generated with the assistance of an AI coding tool.
//
// Geometry tree (JavaScript): selecting by a bounding box.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';

const input = process.argv[2];
if (!input) {
  console.error('usage: select_box <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
await runtime.loadPlugin('mapping', 'ifc4');
await runtime.loadPlugin('kernel', 'opencascade');
await runtime.loadPlugin('tree', 'opencascade.brep');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
// tag::build
// The tree plugin is loaded like the other plugins:
// await runtime.loadPlugin('tree', 'opencascade.brep');
const settings = new geom.Settings();
const tree = runtime.raw.geom.createTree('opencascade.brep');
if (!tree) {
  throw new Error('Geometry tree was not created');
}
tree.addFile(model, settings);
// end::build

// tag::select
// Elements whose bounds overlap the box from (-1, -1, -1) to (1, 1, 1).
// Pass true as the last argument for elements completely within the box.
const selected = tree.selectBoxBounds(-1, -1, -1, 1, 1, 1, false);
for (const element of selected) {
  if (element) {
    console.log(element.id(), element.className(false));
  }
}
// end::select
// end::example

if (typeof selected?.[Symbol.iterator] !== 'function') {
  console.error('selectBoxBounds did not return a list');
  model.dispose();
  process.exit(1);
}
model.dispose();
