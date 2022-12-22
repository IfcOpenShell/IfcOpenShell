import ifcopenshell

coords = [(0., 0.), (10., 0.), (10., 10.), (0., 10.)]
make_3d = lambda cs: [c + (0.,) for c in cs]
inner_1 = [(1., 1.), (2., 1.), (2., 2.), (1., 2.)]
inner_2 = [(3., 3.), (4., 3.), (4., 4.), (3., 4.)]

old_map = map
map = lambda fn, *args: list(old_map(fn, *args))

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcArbitraryProfileDefWithVoids(
    "AREA",
    None,
    f.createIfcPolyline(map(f.createIfcCartesianPoint, coords)),
    [
        f.createIfcPolyline(map(f.createIfcCartesianPoint, inner_1)),
        f.createIfcPolyline(map(f.createIfcCartesianPoint, inner_2)),
    ]
)
f.write(f"pass-arbitrary-profile-with-voids-ifc2x3.ifc")

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcArbitraryProfileDefWithVoids(
    "CURVE",
    None,
    f.createIfcPolyline(map(f.createIfcCartesianPoint, coords)),
    [
        f.createIfcPolyline(map(f.createIfcCartesianPoint, inner_1)),
        f.createIfcPolyline(map(f.createIfcCartesianPoint, inner_2)),
    ]
)
f.write(f"fail-arbitrary-profile-with-voids-curve-ifc2x3.ifc")

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcArbitraryProfileDefWithVoids(
    "AREA",
    None,
    f.createIfcPolyline(map(f.createIfcCartesianPoint, make_3d(coords))),
    [
        f.createIfcPolyline(map(f.createIfcCartesianPoint, inner_1)),
        f.createIfcPolyline(map(f.createIfcCartesianPoint, inner_2)),
    ]
)
f.write(f"fail-arbitrary-profile-with-voids-3d-outer-ifc2x3.ifc")

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcArbitraryProfileDefWithVoids(
    "AREA",
    None,
    f.createIfcPolyline(map(f.createIfcCartesianPoint, coords)),
    [
        f.createIfcPolyline(map(f.createIfcCartesianPoint, make_3d(inner_1))),
        f.createIfcPolyline(map(f.createIfcCartesianPoint, inner_2)),
    ]
)
f.write(f"fail-arbitrary-profile-with-voids-3d-inner-ifc2x3.ifc")

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcArbitraryProfileDefWithVoids(
    "AREA",
    None,
    f.createIfcPolyline(map(f.createIfcCartesianPoint, coords)),
    [
        f.createIfcPolyline(map(f.createIfcCartesianPoint, make_3d(inner_1))),
        f.createIfcPolyline(map(f.createIfcCartesianPoint, make_3d(inner_2))),
    ]
)
f.write(f"fail-arbitrary-profile-with-voids-3d-inner-2-ifc2x3.ifc")

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcArbitraryProfileDefWithVoids(
    "AREA",
    None,
    f.createIfcPolyline(map(f.createIfcCartesianPoint, coords)),
    [
        f.createIfcLine(
            f.createIfcCartesianPoint((0., 0.)),
            f.createIfcVector(
                f.createIfcDirection((0., 0.)),
                1.
            )
        )
    ]
)
f.write(f"fail-arbitrary-profile-with-voids-inner-line-ifc2x3.ifc")