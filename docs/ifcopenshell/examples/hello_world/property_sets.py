# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): reading the property sets of an element.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])
wall = model.by_type("IfcWall")[0]

# tag::example
import ifcopenshell.util.element

print(ifcopenshell.util.element.get_psets(wall))
# end::example

assert ifcopenshell.util.element.get_psets(wall)["Pset_WallCommon"]["FireRating"] == "2HR"
