import ifcopenshell
from ...fixture_generate import normalize_header, pass_if, write_fixture

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
    normalize_header(f)
    write_fixture(f, __file__, pass_if(i in (0, 1, 3)), f"{i}-box-alignment-{box_alignment}{suffix}-ifc2x3")
