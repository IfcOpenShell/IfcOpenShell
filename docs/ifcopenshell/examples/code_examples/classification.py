# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): get the classification of an element.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
import ifcopenshell.util.classification

wall = model.by_type("IfcWall")[0]
# Elements may have multiple classification references assigned
references = ifcopenshell.util.classification.get_references(wall)
for reference in references:
    # A reference code might be Pr_30_59_99_02
    print("The wall has a classification reference of", reference.Identification)
    # A system might be Uniclass 2015
    system = ifcopenshell.util.classification.get_classification(reference)
    print("This reference is part of the system", system.Name)
# end::example
