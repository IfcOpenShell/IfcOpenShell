// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (JavaScript): creating, copying, and removing instances.

import { readFile } from 'node:fs/promises';
import * as ifcopenshell from 'ifcopenshell';

const input = process.argv[2];
if (!input) {
  console.error('usage: create_instance <model.ifc>');
  process.exit(1);
}

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');
const model = ifcopenshell.open(await readFile(input), input);
const wallCount = model.byType('IfcWall').length;

// tag::create_instance
// Returns #74=IfcWall($,$,$,$,$,$,$,$,$): all of the attributes are blank!
const newWall = model.create('IfcWall');
console.log(model.byType('IfcWall'));
// end::create_instance

// tag::create_instance_attribute_order
const orderedWall = model.create('IfcWall');
orderedWall.set(0, '0EI0MSHbX9gg8Fxwar7lLC'); // GlobalId
orderedWall.set(2, 'Wall Name'); // Name
// end::create_instance_attribute_order

// tag::create_instance_attribute_names
model.create('IfcWall', {
  GlobalId: '0EI0MSHbX9gg8Fxwar7lLD',
  Name: 'Wall Name',
});
// end::create_instance_attribute_names

// tag::create_instance_from_table
const data = {
  GlobalId: '0EI0MSHbX9gg8Fxwar7lLE',
  Name: 'Wall Name',
};
model.create('IfcWall', data);
// end::create_instance_from_table

// tag::set_reference_attribute
const wall = model.create('IfcWall');
wall.OwnerHistory = model.create('IfcOwnerHistory');
// end::set_reference_attribute

// tag::copy_instance
const original = model.byType('IfcWall')[0];
const newModel = new ifcopenshell.File('IFC4');
const copy = newModel.add(original);
// end::copy_instance

// tag::remove_instance
model.remove(newWall);
// end::remove_instance

const expected = model.byType('IfcWall').length === wallCount + 4
  && orderedWall.Name === 'Wall Name'
  && wall.OwnerHistory.isA('IfcOwnerHistory')
  && copy.GlobalId === original.GlobalId
  && newModel.byType('IfcWall').length === 1;
newModel.dispose();
if (!expected) {
  console.error('unexpected instances');
  model.dispose();
  process.exit(1);
}
model.dispose();
