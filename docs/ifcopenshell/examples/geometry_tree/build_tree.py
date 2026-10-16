# This file was generated with the assistance of an AI coding tool.
#
# Geometry tree (Python): building trees from the geometry iterator.
#
# Requires IfcOpenShell 0.9, where the backend selects the type of tree.

import sys

ifc_path = sys.argv[1]

# tag::example
import multiprocessing

import ifcopenshell
import ifcopenshell.geom

ifc_file = ifcopenshell.open(ifc_path)

settings = ifcopenshell.geom.settings()
iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count())

# A BVH tree of triangulated elements, for clashing
tree = ifcopenshell.geom.tree(backend="opencascade.trianglebvh")
if iterator.initialize():
    while True:
        tree.add_element(iterator.get())
        if not iterator.next():
            break

# Alternatively, a UB tree of native elements, for selection
tree = ifcopenshell.geom.tree(backend="opencascade.brep")
if iterator.initialize():
    while True:
        tree.add_element(iterator.get_native())
        if not iterator.next():
            break
# end::example

assert tree.select_box(ifc_file.by_type("IfcWall")[0])
