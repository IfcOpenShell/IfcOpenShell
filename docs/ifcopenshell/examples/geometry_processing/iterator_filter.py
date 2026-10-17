# This file was generated with the assistance of an AI coding tool.
#
# Geometry processing (Python): processing only some elements.

import multiprocessing
import sys

import ifcopenshell
import ifcopenshell.geom

ifc_file = ifcopenshell.open(sys.argv[1])
settings = ifcopenshell.geom.settings()

# tag::example
walls = ifc_file.by_type("IfcWall")
iterator = ifcopenshell.geom.iterator(
    settings,
    ifc_file,
    multiprocessing.cpu_count(),
    include=walls,
    geometry_library="hybrid-cgal-simple-opencascade",
)
# end::example

processed = set()
if iterator.initialize():
    while True:
        processed.add(iterator.get().id)
        if not iterator.next():
            break
assert processed == {wall.id() for wall in walls}
