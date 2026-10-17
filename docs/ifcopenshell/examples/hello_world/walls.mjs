// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (JavaScript): querying, reading, and editing a wall.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: walls <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);

// tag::by_guid
console.log(model.byGuid('0EI0MSHbX9gg8Fxwar7lL8'));
// end::by_guid

// tag::count
const walls = model.byType('IfcWall');
console.log(walls.length);
// end::count

// tag::instance_class
const wall = model.byType('IfcWall')[0];
console.log(wall.isA()); // 'IfcWall'
// end::instance_class

// tag::is_a
console.log(wall.isA('IfcWall')); // true
console.log(wall.isA('IfcElement')); // true
console.log(wall.isA('IfcWindow')); // false
// end::is_a

// tag::step_id
console.log(wall.id());
// end::step_id

// tag::attribute_by_index
console.log(wall.get(0)); // The first attribute is the GlobalId
console.log(wall.get(2)); // The third attribute is the Name
// end::attribute_by_index

// tag::attribute_by_name
console.log(wall.GlobalId);
console.log(wall.Name);
// end::attribute_by_name

// tag::all_attributes
// An object of attributes, such as:
// { id: 5, type: 'IfcWall', GlobalId: '0EI0MSHbX9gg8Fxwar7lL8', ... }
console.log(wall.getInfo());
// end::all_attributes

// tag::inverse_attributes
console.log(wall.IsDefinedBy);
// end::inverse_attributes

// tag::get_inverse
console.log(model.getInverse(wall));
// end::get_inverse

// tag::traverse
console.log(model.traverse(wall, -1));
// Or, let's just go down one level deep
console.log(model.traverse(wall, 1));
// end::traverse

// tag::set_attribute
wall.Name = 'My new wall name';
// end::set_attribute

// tag::new_global_id
wall.GlobalId = '0YvctVUKr0kugbFTf53O9L';
// end::new_global_id

const expected = walls.length === 1
  && wall.isA('IfcElement')
  && wall.id() === 5
  && wall.IsDefinedBy.length === 1
  && model.getInverse(wall).size === 2
  && model.traverse(wall, 1).length > 0
  && wall.Name === 'My new wall name'
  && wall.GlobalId === '0YvctVUKr0kugbFTf53O9L';
if (!expected) {
  console.error('unexpected wall data');
  model.dispose();
  process.exit(1);
}
model.dispose();
