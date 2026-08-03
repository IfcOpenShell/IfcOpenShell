import ifcopenshell
from generate import normalize_header, pass_if, write_fixture

pts = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]
dims = [(2, 3, 3), (3, 3, 2), (2, 2, 2), (3, 3, 3)]


def make_point(xy, dim):
    return f.createIfcCartesianPoint((xy + (0.0,))[0:dim])


for d in dims:
    f = ifcopenshell.file(schema="IFC2X3")
    inst = f.create_entity(
        "IfcBezierCurve", 1, list(map(lambda t: make_point(*t), zip(pts, d))), "POLYLINE_FORM", False, False
    )
    normalize_header(f)
    write_fixture(
        f,
        __file__,
        pass_if(len(set(d)) == 1),
        f"bspline-curve-point-dimensions-{'-'.join(map(str, d))}-ifc2x3",
    )
