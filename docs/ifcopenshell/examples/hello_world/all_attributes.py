# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): getting all attributes.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])
wall = model.by_type("IfcWall")[0]

# tag::example
# Gives us a dictionary of attributes, such as:
# {'id': 5, 'type': 'IfcWall', 'GlobalId': '0EI0MSHbX9gg8Fxwar7lL8', ... }
print(wall.get_info())
# end::example

assert wall.get_info()["Name"] == "Wall 01"
