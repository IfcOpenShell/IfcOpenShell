# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): creating an instance.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
# Will return #74=IfcWall($,$,$,$,$,$,$,$,$) - notice all of the attributes are blank!
new_wall = model.createIfcWall()
# Will return a list with our new wall in it
print(model.by_type("IfcWall"))
# end::example

assert new_wall in model.by_type("IfcWall")
