# This file was generated with the assistance of an AI coding tool.
#
# Geometry processing (Python): the geometry iterator.

import sys

ifc_path = sys.argv[1]

# tag::example
import multiprocessing

import ifcopenshell
import ifcopenshell.geom

ifc_file = ifcopenshell.open(ifc_path)

settings = ifcopenshell.geom.settings()
# tag::filter
iterator = ifcopenshell.geom.iterator(
    settings, ifc_file, multiprocessing.cpu_count(), geometry_library="hybrid-cgal-simple-opencascade"
)
# end::filter
processed = 0
if iterator.initialize():
    while True:
        shape = iterator.get()
        element = ifc_file.by_id(shape.id)
        matrix = shape.transformation.matrix
        faces = shape.geometry.faces
        edges = shape.geometry.edges
        verts = shape.geometry.verts
        materials = shape.geometry.materials
        material_ids = shape.geometry.material_ids
        # ... write code to process geometry here ...
        processed += 1
        if not iterator.next():
            break
print("Processed", processed, "elements")
# end::example

assert processed > 0
