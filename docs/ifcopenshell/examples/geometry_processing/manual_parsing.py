# This file was generated with the assistance of an AI coding tool.
#
# Geometry processing (Python): reading geometry parameters directly.

import sys

import ifcopenshell

ifc_file = ifcopenshell.open(sys.argv[1])

# tag::example
import ifcopenshell.util.unit

unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)

for solid in ifc_file.by_type("IfcExtrudedAreaSolid"):
    # In project length units
    print(solid.Depth)

    # In SI metres
    print(solid.Depth * unit_scale)
# end::example

assert ifc_file.by_type("IfcExtrudedAreaSolid") and unit_scale > 0
