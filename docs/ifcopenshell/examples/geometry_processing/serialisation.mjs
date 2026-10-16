// This file was generated with the assistance of an AI coding tool.
//
// Geometry processing (JavaScript): serialising to OBJ.

import { readFile, writeFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';
import { exportToBuffer } from 'ifcopenshell/serializers';

const input = process.argv[2];
if (!input) {
  console.error('usage: serialisation <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
await runtime.loadPlugin('mapping', 'ifc4');
await runtime.loadPlugin('kernel', 'manifold');
await runtime.loadPlugin('geometry_serializer', 'obj');
const model = ifcopenshell.open(await readFile(input), input);

// tag::example
const settings = new geom.Settings();
const result = await exportToBuffer(model, settings, 'obj', {
  kernel: 'manifold',
  numThreads: 1,
});
if (result) {
  await writeFile('model.obj', result.primary, 'utf8');
  await writeFile('model.mtl', result.secondary, 'utf8');
}
// end::example

if (!result?.primary.includes('v ')) {
  console.error('OBJ export produced no vertices');
  model.dispose();
  process.exit(1);
}
model.dispose();
