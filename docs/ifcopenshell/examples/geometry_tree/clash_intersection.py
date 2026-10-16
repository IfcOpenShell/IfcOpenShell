# This file was generated with the assistance of an AI coding tool.
#
# Geometry tree (Python): detecting intersection clashes.

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


tree = build_tree("opencascade.trianglebvh", native=False)
group_a_elements = ifc_file.by_type("IfcWall")
group_b_elements = ifc_file.by_type("IfcSlab")

# tag::example
clashes = tree.clash_intersection_many(
    group_a_elements,  # e.g. from model.by_type("IfcWall")
    group_b_elements,  # Group b can be the same as group a to clash within a single set
    tolerance=0.002,  # Any protrusions less than 2mm are ignored
    check_all=True,  # Keep on checking all potential intersections to find a worst case protrusion distance
)

for clash in clashes:
    # Get the two elements that clash and their metadata
    element1 = clash.a
    element2 = clash.b
    a_global_id = element1.get_argument(0)
    b_global_id = element2.get_argument(0)
    a_ifc_class = element1.is_a()
    b_ifc_class = element2.is_a()
    a_name = element1.get_argument(2)
    b_name = element2.get_argument(2)

    # Potential clash types that can be detected are protrusions, pierces, and collisions
    clash_type = ["protrusion", "pierce", "collision", "clearance"][clash.clash_type]

    # P1 and P2 represent two XYZ coordinates. The meaning of the coordinate
    # depends on the clash type.
    p1 = list(clash.p1)
    p2 = list(clash.p2)

    # This represents the protrusion or piercing distance in meters.
    # It is also the distance between P1 and P2.
    distance = clash.distance
# end::example

print(len(clashes), "intersections")
