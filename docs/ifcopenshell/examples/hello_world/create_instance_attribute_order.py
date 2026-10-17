# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): creating an instance with attributes in order.

import sys

import ifcopenshell
import ifcopenshell.guid

model = ifcopenshell.open(sys.argv[1])

# tag::example
# Gives us #74=IfcWall('0EI0MSHbX9gg8Fxwar7lL8',$,$,$,$,$,$,$,$)
wall = model.create_entity("IfcWall", ifcopenshell.guid.new())
# end::example

assert len(wall.GlobalId) == 22
