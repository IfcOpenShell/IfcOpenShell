import ifcopenshell

make_nd = lambda d: lambda *c: (c + (0.0,)) if d == 3 else c

for d1, d2 in ((2, 3), (3, 3), (3, 2)):
    f = ifcopenshell.file(schema="IFC2X3")
    f.createIfcLocalPlacement(
        PlacementRelTo=f.createIfcLocalPlacement(
            PlacementRelTo=None,
            RelativePlacement=f.create_entity(
                f"IfcAxis2Placement{d1}D", f.createIfcCartesianPoint(make_nd(d1)(0.0, 0.0))
            ),
        ),
        RelativePlacement=f.create_entity(f"IfcAxis2Placement{d2}D", f.createIfcCartesianPoint(make_nd(d2)(0.0, 0.0))),
    )
    f.write(f"{'pass' if d1 >= d2 else 'fail'}-placement-{d1}d-{d2}d-ifc2x3.ifc")
