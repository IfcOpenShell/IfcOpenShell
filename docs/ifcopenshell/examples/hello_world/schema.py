# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): inspecting the schema.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
print(model.schema)  # May return IFC2X3, IFC4, or IFC4X3.
# end::example

assert model.schema == "IFC4"
