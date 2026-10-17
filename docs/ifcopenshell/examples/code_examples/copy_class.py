# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): copying an element with the authoring API.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

wall = model.by_type("IfcWall")[0]

# tag::example
import ifcopenshell.api.root

wall_copy = ifcopenshell.api.root.copy_class(model, product=wall)
# end::example

assert wall_copy.id() != wall.id() and wall_copy.is_a() == wall.is_a()
