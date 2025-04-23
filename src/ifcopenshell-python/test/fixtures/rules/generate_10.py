import itertools
import ifcopenshell

defaults = {"Girth": 1.0, "WallThickness": 0.11}
depths = [2.0, 3.0]
widths = [0.2, 0.3]

for d, w in itertools.product(depths, widths):

    D = dict(defaults, Depth=d, Width=w)
    globals().update(D)

    f = ifcopenshell.file(schema="IFC2X3")

    valid = (Girth < (Depth / 2.0)) and ((WallThickness < Width / 2.0) and (WallThickness < Depth / 2.0))

    inst = f.createIfcCShapeProfileDef(
        "AREA", None, f.createIfcAxis2Placement2D(f.createIfcCartesianPoint((0.0, 0.0))), **D
    )
    f.write(f"{'pass' if valid else 'fail'}-cshape-profile-width-{w}-depth-{d}-ifc2x3.ifc")
