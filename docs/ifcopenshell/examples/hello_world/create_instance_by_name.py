# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): creating an instance from the name of its class.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
model.create_entity("IfcWall")
# end::example

assert len(model.by_type("IfcWall")) == 2
