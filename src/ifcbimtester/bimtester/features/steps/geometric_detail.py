from behave import step

from utils import IfcFile


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
