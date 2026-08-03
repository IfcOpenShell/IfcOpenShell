import ifcopenshell

for i, box_alignment in enumerate(["top-left", "center", "invalid", "CENTER"]):
    f = ifcopenshell.file(schema="IFC2X3")

    f.createIfcTextLiteralWithExtent(
        "My presentable text",
        f.createIfcAxis2Placement2D(f.createIfcCartesianPoint((0.0, 0.0))),
        "RIGHT",
        f.createIfcPlanarExtent(10.0, 10.0),
        box_alignment,
    )

    suffix = "-uppercase" if box_alignment == "CENTER" else ""
    f.write(f"{'pass' if i in (0,1,3) else 'fail'}-{i}-box-alignment-{box_alignment}{suffix}-ifc2x3.ifc")
