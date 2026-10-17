# This file was generated with the assistance of an AI coding tool.
#
# Schema querying (Python): buildingSMART property set templates.

import sys

import ifcopenshell

# tag::example
import ifcopenshell.util.pset
templates = ifcopenshell.util.pset.PsetQto("IFC4")
# end::example

# tag::names
# ['Pset_EnvironmentalImpactIndicators', 'Pset_EnvironmentalImpactValues', 'Pset_WallCommon', 'Qto_WallBaseQuantities', ...]
print(templates.get_applicable_names("IfcWall"))
# end::names

# tag::applicable
print(templates.get_applicable("IfcWall"))
# end::applicable

# tag::by_name
templates.get_by_name('Pset_WallCommon')
# end::by_name

assert "Pset_WallCommon" in templates.get_applicable_names("IfcWall")

# tag::library
my_pset_library = ifcopenshell.open(sys.argv[1])
templates.templates.append(my_pset_library)
# end::library
