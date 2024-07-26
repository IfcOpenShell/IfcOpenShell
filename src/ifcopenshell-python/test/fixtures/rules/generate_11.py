import ifcopenshell

depth = 1.0
for dir_x, dir_z in ((0.0, -1.0), (0.0, 0.0), (1.0, 0.0), (1.0, 0.001), (0.0, 1.0)):

    schemas = ["IFC2X3"]
    if (dir_x, dir_z) == (0.0, 0.0):
        schemas.append("IFC4")

    for schema in schemas:
        f = ifcopenshell.file(schema=schema)
        f.createIfcExtrudedAreaSolid(
            f.createIfcRectangleProfileDef(
                "AREA", None, f.createIfcAxis2Placement2D(f.createIfcCartesianPoint((0.0, 0.0))), 1.0, 1.0
            ),
            f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0))),
            f.createIfcDirection((dir_x, 0.0, dir_z)),
            depth,
        )

        # Due to the way IfcDotProduct and IfcNormalise interact, (0 0 0) actually
        # results into indeterminate. But in IFC4 onwars there is a rule in IfcDirection
        # for non-zero magnitude

        valid = dir_z != 0.0
        if f.schema == "IFC2X3" and (dir_x, dir_z) == (0.0, 0.0):
            valid = True

        f.write(f"{'pass' if valid else 'fail'}-extrusion-dir-{dir_x}-{dir_z}-{f.schema.lower()}.ifc")
