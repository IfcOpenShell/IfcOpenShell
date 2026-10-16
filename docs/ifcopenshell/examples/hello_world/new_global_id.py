# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): generating a new GlobalId.

import sys

import ifcopenshell
import ifcopenshell.guid

model = ifcopenshell.open(sys.argv[1])
wall = model.by_type("IfcWall")[0]

# tag::example
wall.GlobalId = ifcopenshell.guid.new()
# end::example

assert wall.GlobalId != "0EI0MSHbX9gg8Fxwar7lL8" and len(wall.GlobalId) == 22
