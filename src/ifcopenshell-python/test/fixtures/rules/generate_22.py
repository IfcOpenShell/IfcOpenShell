import ifcopenshell

from ...fixture_generate import normalize_header, pass_if, write_fixture

for cnt in range(0, 3):
    f = ifcopenshell.file(schema="IFC4")
    elem = f.createIfcWall(ifcopenshell.guid.new())
    for i in range(cnt):
        f.createIfcRelDefinesByProperties(
            ifcopenshell.guid.new(),
            None,
            None,
            None,
            [elem],
            f.createIfcPropertySet(
                ifcopenshell.guid.new(),
                None,
                "Pset_WallCommon",
                None,
                [f.createIfcPropertySingleValue("LoadBearing", None, f.createIfcBoolean(True))],
            ),
        )
    normalize_header(f)
    write_fixture(f, __file__, pass_if(cnt < 2), f"wall-{cnt}-same-psets")


f = ifcopenshell.file(schema="IFC4")
elem = f.createIfcWall(ifcopenshell.guid.new())
f.createIfcRelDefinesByProperties(
    ifcopenshell.guid.new(),
    None,
    None,
    None,
    [elem],
    f.createIfcPropertySet(
        ifcopenshell.guid.new(),
        None,
        "Pset_WallCommon",
        None,
        [f.createIfcPropertySingleValue("LoadBearing", None, f.createIfcBoolean(True))],
    ),
)
f.createIfcRelDefinesByProperties(
    ifcopenshell.guid.new(),
    None,
    None,
    None,
    [elem],
    f.createIfcPropertySet(
        ifcopenshell.guid.new(),
        None,
        "Custom",
        None,
        [f.createIfcPropertySingleValue("IsBeautiful", None, f.createIfcBoolean(True))],
    ),
)
normalize_header(f)
write_fixture(f, __file__, "pass", "wall-different-psets")
