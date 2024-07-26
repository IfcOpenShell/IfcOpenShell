import ifcopenshell

for depth in (-1.0, 0.0, 1.0):
    f = ifcopenshell.file(schema="IFC2X3")
    f.createIfcExtrudedAreaSolid(
        f.createIfcRectangleProfileDef(
            "AREA", None, f.createIfcAxis2Placement2D(f.createIfcCartesianPoint((0.0, 0.0))), 1.0, 1.0
        ),
        f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0))),
        f.createIfcDirection((0.0, 0.0, 1.0)),
        depth,
    )
    f.write(f"{'pass' if depth > 0. else 'fail'}-extrusion-depth-{depth}-ifc2x3.ifc")
