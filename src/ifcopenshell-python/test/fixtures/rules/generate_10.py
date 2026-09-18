import itertools

import ifcopenshell

from ...fixture_generate import normalize_header, pass_if, write_fixture

defaults = {"Girth": 1.0, "WallThickness": 0.11}
depths = [2.0, 3.0]
widths = [0.2, 0.3]

Girth, Depth, WallThickness, Width = 0.0, 0.0, 0.0, 0.0

for d, w in itertools.product(depths, widths):

    D = dict(defaults, Depth=d, Width=w)
    globals().update(D)

    f = ifcopenshell.file(schema="IFC2X3")

    girth_valid = Girth < (Depth / 2.0)
    wallthickness_valid = (WallThickness < Width / 2.0) and (WallThickness < Depth / 2.0)
    valid = girth_valid and wallthickness_valid
    errors_if_fail = int(not girth_valid) + int(not wallthickness_valid)

    inst = f.createIfcCShapeProfileDef(
        "AREA", None, f.createIfcAxis2Placement2D(f.createIfcCartesianPoint((0.0, 0.0))), **D
    )
    normalize_header(f)
    write_fixture(
        f, __file__, pass_if(valid, errors_if_fail=errors_if_fail), f"cshape-profile-width-{w}-depth-{d}-ifc2x3"
    )
