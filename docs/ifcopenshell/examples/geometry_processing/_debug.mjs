import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';
import * as geom from 'ifcopenshell/geom';

const input = process.argv[2];
const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
await runtime.loadPlugin('mapping', 'ifc4');
await runtime.loadPlugin('kernel', 'manifold');
await runtime.loadPlugin('kernel', 'opencascade');
await runtime.loadPlugin('tree', 'opencascade.brep');
await runtime.loadPlugin('tree', 'opencascade.trianglebvh');
const model = ifcopenshell.open(await readFile(input), input);
const wall = model.byType('IfcWall').find((item) => item.Representation instanceof ifcopenshell.EntityInstance);
const reps = wall.Representation.Representations;
for (const rep of reps) {
  console.log('REP', rep.RepresentationIdentifier, rep.RepresentationType, rep.isA());
  try {
    const shape = geom.createShape(new geom.Settings(), wall, rep, 'manifold');
    console.log('  shape', shape && shape.id());
    shape?.destroy();
  } catch (error) {
    console.log('  fail', error.message);
  }
}
const geomApi = runtime.raw.geom;
const settings = new geom.Settings();
for (const backend of ['opencascade.brep', 'opencascade.trianglebvh']) {
  try {
    const tree = geomApi.createTreeFromFileWithSettings(model, settings);
    console.log('fromFile', backend, tree && tree.ptr);
    tree?.destroy();
  } catch (error) {
    console.log('fromFile fail', backend, error.message);
  }
  try {
    const tree = geomApi.createTree(backend);
    console.log('created', backend, typeof tree.addFile);
    tree.addFile(model, settings);
    console.log('added', backend);
    tree.destroy();
  } catch (error) {
    console.log('add fail', backend, error.message);
  }
}
model.dispose();
