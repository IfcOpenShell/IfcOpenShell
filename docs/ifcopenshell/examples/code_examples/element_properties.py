# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): get the properties of an element.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
import ifcopenshell.util.element

wall = model.by_type("IfcWall")[0]

# All properties and quantities of the wall, including inherited type
# properties, as a dictionary such as:
# {"Pset_WallCommon": {"id": 123, "FireRating": "2HR", ...}}
psets = ifcopenshell.util.element.get_psets(wall)
print(psets)

# Only properties and not quantities
print(ifcopenshell.util.element.get_psets(wall, psets_only=True))

# Only quantities and not properties
print(ifcopenshell.util.element.get_psets(wall, qtos_only=True))
# end::example

assert psets
