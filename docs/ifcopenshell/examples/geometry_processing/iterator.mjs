// This file was generated with the assistance of an AI coding tool.
//
// Geometry processing (JavaScript): the geometry iterator.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';

const input = process.argv[2];
if (!input) {
  console.error('usage: iterator <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
await runtime.loadPlugin('mapping', 'ifc4');
await runtime.loadPlugin('kernel', 'manifold');
const model = ifcopenshell.open(await readFile(input), input);
const settings = new geom.Settings();
settings.set('weld-vertices', false);

// tag::example
// tag::filter
const iterator = new geom.Iterator(settings, model, {
  geometryLibrary: 'manifold',
  numThreads: 1,
  include: ['IfcWall', 'IfcSlab'],
});
// end::filter
let processed = 0;
try {
  if (iterator.initialize()) {
    do {
      const shape = iterator.get();
      if (shape) {
        console.log(shape.id(), shape.guid(), shape.name());
        // ... write code to process the geometry here ...
        processed += 1;
        shape.destroy();
      }
    } while (iterator.next());
  }
} finally {
  iterator.dispose();
}
console.log('Processed', processed, 'elements');
// end::example

if (processed === 0) {
  console.error('iterator produced no shapes');
  model.dispose();
  process.exit(1);
}
model.dispose();
