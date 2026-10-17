# This file was generated with the assistance of an AI coding tool.
#
# Geometry tree (Python): selecting elements using precise geometry.

import multiprocessing
import sys

import ifcopenshell
import ifcopenshell.geom

ifc_file = ifcopenshell.open(sys.argv[1])


def build_tree(backend: str, native: bool) -> ifcopenshell.geom.tree:
    try:
        tree = ifcopenshell.geom.tree(backend=backend)
    except TypeError:
        # IfcOpenShell 0.8 has a single kind of tree.
        tree = ifcopenshell.geom.tree()
    settings = ifcopenshell.geom.settings()
    iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count())
    if iterator.initialize():
        while True:
            tree.add_element(iterator.get_native() if native else iterator.get())
            if not iterator.next():
                break
    return tree


tree = build_tree("opencascade.brep", native=True)

# tag::example
elements = tree.select((0.0, 0.0, 0.0))
# end::example

# tag::sphere
# This extension is also in meters.
elements = tree.select((0.0, 0.0, 0.0), extend=5.0)
# end::sphere

assert elements

# tag::element
wall = ifc_file.by_type("IfcWall")[0]
elements = tree.select(wall)
# end::element

assert wall in elements

# tag::completely_within
elements = tree.select(wall, completely_within=True)

# Alternatively, you may also specify an extension to dilate the geometry of
# the wall.
elements = tree.select(wall, completely_within=True, extend=5.0)
# end::completely_within
