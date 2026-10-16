# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): get the distribution system of an element.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
import ifcopenshell.util.system

for pipe in model.by_type("IfcPipeSegment"):
    # Elements may be assigned to multiple systems simultaneously, such as
    # electrical, hydraulic, etc
    for system in ifcopenshell.util.system.get_element_systems(pipe):
        # For example, it might be part of a Chilled Water system
        print("This pipe is part of the system", system.Name)
# end::example
