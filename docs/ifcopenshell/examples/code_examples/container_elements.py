# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): get all elements in a container.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
import ifcopenshell.util.element

for storey in model.by_type("IfcBuildingStorey"):
    elements = ifcopenshell.util.element.get_decomposition(storey)
    print(f"There are {len(elements)} located on storey {storey.Name}, they are:")
    for element in elements:
        print(element.Name)
# end::example

assert any(ifcopenshell.util.element.get_decomposition(storey) for storey in model.by_type("IfcBuildingStorey"))
