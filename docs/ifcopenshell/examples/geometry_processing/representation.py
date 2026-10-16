# This file was generated with the assistance of an AI coding tool.
#
# Geometry processing (Python): processing a particular representation.

import sys

import ifcopenshell
import ifcopenshell.geom

ifc_file = ifcopenshell.open(sys.argv[1])
settings = ifcopenshell.geom.settings()

# tag::example
window = ifc_file.by_type("IfcWindow")[0]
for representation in window.Representation.Representations:
    if representation.RepresentationIdentifier != "Body":
        continue
    # The third argument nominates the shape representation to process
    shape = ifcopenshell.geom.create_shape(settings, window, representation)
    print(representation.RepresentationIdentifier, len(shape.geometry.faces) // 3, "triangles")
# end::example

assert shape.id == window.id()

# tag::standalone
import ifcopenshell.util.representation

element = ifc_file.by_type("IfcWall")[0]

# Process a shape representation. The geometry is returned directly,
# equivalent to shape.geometry when passing in an element.
body = ifcopenshell.util.representation.get_representation(element, "Model", "Body")
geometry = ifcopenshell.geom.create_shape(settings, body)

# Process a representation item
geometry = ifcopenshell.geom.create_shape(settings, ifc_file.by_type("IfcExtrudedAreaSolid")[0])

# Process a profile
geometry = ifcopenshell.geom.create_shape(settings, ifc_file.by_type("IfcProfileDef")[0])
# end::standalone

assert geometry.verts
