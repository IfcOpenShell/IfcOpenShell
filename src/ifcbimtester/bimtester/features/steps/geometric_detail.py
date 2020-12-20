from behave import step

from geometric_detail_methods import class_geometric_representation
from geometric_detail_methods import check_geometric_representation
from utils import assert_elements
from utils import IfcFile
from utils import switch_locale


@step("All elements must be under {number} polygons")
def step_impl(context, number):
    number = int(number)
    errors = []
    for element in IfcFile.get().by_type("IfcElement"):
        if not element.Representation:
            continue
        total_polygons = 0
        tree = IfcFile.get().traverse(element.Representation)
        for e in tree:
            if e.is_a("IfcFace"):
                total_polygons += 1
            elif e.is_a("IfcPolygonalFaceSet"):
                total_polygons += len(e.Faces)
            elif e.is_a("IfcTriangulatedFaceSet"):
                total_polygons += len(e.CoordIndex)
        if total_polygons > number:
            errors.append((total_polygons, element))
    if errors:
        message = (
            "The following {} elements are over 500 polygons:\n"
            .format(len(errors))
        )
        for error in errors:
            message += "Polygons: {} - {}\n".format(error[0], error[1])
        assert False, message


@step("all {ifc_class} elements have an {representation_class} representation")
def step_impl(context, ifc_class, representation_class):
    switch_locale(context.localedir, "en")
    class_geometric_representation(context, ifc_class, representation_class)


@step("all {ifc_class} elements must have a geometric representation without errors")
def step_impl(context, ifc_class):
    switch_locale(context.localedir, "en")
    check_geometric_representation(context, ifc_class)


