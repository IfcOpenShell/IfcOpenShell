# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): copying an instance into another file.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
wall = model.by_type("IfcWall")[0]
new_model = ifcopenshell.file(schema=model.schema)
new_model.add(wall)
# end::example

assert new_model.by_type("IfcWall")[0].GlobalId == wall.GlobalId
