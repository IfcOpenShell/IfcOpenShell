import ifcopenshell

pts = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]
dims = [(2, 3, 3), (3, 3, 2), (2, 2, 2), (3, 3, 3)]


def make_point(xy, dim):
    return f.createIfcCartesianPoint((xy + (0.0,))[0:dim])


for d in dims:
    f = ifcopenshell.file(schema="IFC2X3")
    inst = f.createIfcBSplineCurve(1, list(map(lambda t: make_point(*t), zip(pts, d))), "POLYLINE_FORM", False, False)
    f.write(
        f"{'pass' if len(set(d)) == 1 else 'fail'}-bspline-curve-point-dimensions-{'-'.join(map(str, d))}-ifc2x3.ifc"
    )
