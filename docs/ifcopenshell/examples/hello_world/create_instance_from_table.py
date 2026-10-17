# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): creating an instance from a dictionary of attributes.

import sys

import ifcopenshell
import ifcopenshell.guid

model = ifcopenshell.open(sys.argv[1])

# tag::example
data = {
    "GlobalId": ifcopenshell.guid.new(),
    "Name": "Wall Name",
}
wall = model.create_entity("IfcWall", **data)
# end::example

assert wall.Name == "Wall Name"
