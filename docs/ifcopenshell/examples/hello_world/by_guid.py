# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): getting an instance by its GlobalId.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
print(model.by_guid("0EI0MSHbX9gg8Fxwar7lL8"))
# end::example

assert model.by_guid("0EI0MSHbX9gg8Fxwar7lL8").Name == "Wall 01"
