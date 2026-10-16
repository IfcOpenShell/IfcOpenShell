# This file was generated with the assistance of an AI coding tool.
#
# Geometry tree (Python): detecting clearance clashes.

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
clashes = tree.clash_clearance_many(
    group_a_elements,  # e.g. from model.by_type("IfcWall")
    group_b_elements,  # Group b can be the same as group a to clash within a single set
    clearance=0.1,  # Any surface closer than 100mm is a clash
    check_all=False,  # Stop measuring once the first clearance violation is found per element
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

    # P1 and P2 represent the two XYZ coordinates between element1 and element2.
    p1 = list(clash.p1)
    p2 = list(clash.p2)

    # The distance between element1 and element2 that is less than the
    # clearance. It is the distance between P1 and P2, and cannot be less than 0.
    distance = clash.distance
# end::example

assert clashes, "walls are expected to be near the slabs"
