# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): getting an instance by its STEP ID.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
print(model.by_id(1))
# end::example

assert model.by_id(1).is_a("IfcProject")
