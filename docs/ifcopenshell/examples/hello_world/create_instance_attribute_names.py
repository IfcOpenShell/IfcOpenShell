# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): creating an instance with attributes by name.

import sys

import ifcopenshell
import ifcopenshell.guid

model = ifcopenshell.open(sys.argv[1])

# tag::example
# Gives us #74=IfcWall('0EI0MSHbX9gg8Fxwar7lL8',$,'Wall Name',$,$,$,$,$,$)
wall = model.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new(), Name="Wall Name")
# end::example

assert wall.Name == "Wall Name"
