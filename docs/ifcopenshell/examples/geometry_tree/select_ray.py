# This file was generated with the assistance of an AI coding tool.
#
# Geometry tree (Python): selecting elements using a ray.

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
# A ray from 10 metres up, pointing down
origin = (5.0, 5.0, 10.0)
direction = (0.0, 0.0, -1.0)
results = tree.select_ray(origin, direction, length=100.0)

for result in results:
    print(ifc_file.by_id(result.instance.id()))  # The element the ray intersects with
    print(list(result.position))  # The XYZ intersection point
    print(result.distance)  # The distance between the ray origin and the intersection
    print(list(result.normal))  # The normal of the face being intersected
    print(result.dot_product)  # The dot product of the face being intersected with the ray
# end::example

assert len(results) > 0
