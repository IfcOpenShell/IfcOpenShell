# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): writing the model.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
model.write("updated.ifc")
# end::example

assert ifcopenshell.open("updated.ifc").by_type("IfcWall")
