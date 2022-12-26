import ifcopenshell

depth = 1.0
for (dir_x, dir_z) in ((0., -1.), (0., 0.), (1., 0.), (1., 0.001), (0., 1.)):
    f = ifcopenshell.file(schema="IFC2X3")
    f.createIfcExtrudedAreaSolid(
        f.createIfcRectangleProfileDef(
            "AREA", None,
            f.createIfcAxis2Placement2D(
                f.createIfcCartesianPoint((0., 0.))
            ), 1., 1.
        ),
        f.createIfcAxis2Placement3D(
            f.createIfcCartesianPoint((0., 0., 0.))
        ),
        f.createIfcDirection((dir_x, 0., dir_z)),
        depth
    )
    f.write(f"{'pass' if dir_z != 0. else 'fail'}-extrusion-dir-{dir_x}-{dir_z}-ifc2x3.ifc")
