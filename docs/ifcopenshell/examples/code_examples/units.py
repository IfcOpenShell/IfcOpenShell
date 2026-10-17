# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): convert between SI units and project units.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

ifc_project_length = 2500.0

# tag::example
import ifcopenshell.util.unit

# ifc_project_length is a value you have read from the model, such as from a
# quantity set, in the length unit of the project.
unit_scale = ifcopenshell.util.unit.calculate_unit_scale(model)
# Convert to SI unit:
si_meters = ifc_project_length * unit_scale
# Convert from SI unit:
ifc_project_length = si_meters / unit_scale
# end::example

assert unit_scale > 0 and ifc_project_length == 2500.0
