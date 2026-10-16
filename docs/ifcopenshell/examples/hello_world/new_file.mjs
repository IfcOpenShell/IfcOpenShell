// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (JavaScript): creating a new file.

// tag::example
import * as ifcopenshell from 'ifcopenshell';

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = new ifcopenshell.File('IFC4');
try {
  const wall = model.create('IfcWall', { Name: 'Example wall' });
  wall.set('GlobalId', '0YvctVUKr0kugbFTf53O9L');
  console.log(wall.id(), wall.Name);
  console.log(model.toString());
} finally {
  model.dispose();
}
// end::example
