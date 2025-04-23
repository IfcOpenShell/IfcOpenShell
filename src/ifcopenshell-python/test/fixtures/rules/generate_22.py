import ifcopenshell

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
    f.write(f"{'pass' if cnt < 2 else 'fail'}-wall-{cnt}-same-psets.ifc")


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
f.write(f"pass-wall-different-psets.ifc")
