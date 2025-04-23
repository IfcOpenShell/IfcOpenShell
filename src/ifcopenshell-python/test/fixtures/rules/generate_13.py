import ifcopenshell

coords = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
make_3d = lambda cs: [c + (0.0,) for c in cs]
inner_1 = [(1.0, 1.0), (2.0, 1.0), (2.0, 2.0), (1.0, 2.0)]
inner_2 = [(3.0, 3.0), (4.0, 3.0), (4.0, 4.0), (3.0, 4.0)]

old_map = map
map = lambda fn, *args: list(old_map(fn, *args))

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)))
f.write(f"pass-axis2-3d-pos-ifc2x3.ifc")

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcAxis2Placement3D(
    f.createIfcCartesianPoint((0.0, 0.0, 0.0)),
    f.createIfcDirection((0.0, 0.0, 1.0)),
    f.createIfcDirection((1.0, 0.0, 0.0)),
)
f.write(f"pass-axis2-two-directions-ifc2x3.ifc")

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcAxis2Placement3D(
    f.createIfcCartesianPoint((0.0, 0.0, 0.0)),
    Axis=f.createIfcDirection((0.0, 0.0, 1.0)),
    RefDirection=None,
)
f.write(f"fail-axis2-only-axis-ifc2x3.ifc")

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcAxis2Placement3D(
    f.createIfcCartesianPoint((0.0, 0.0, 0.0)),
    Axis=None,
    RefDirection=f.createIfcDirection((1.0, 0.0, 0.0)),
)
f.write(f"fail-axis2-only-ref-ifc2x3.ifc")

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcAxis2Placement3D(
    f.createIfcCartesianPoint((0.0, 0.0, 0.0)),
    f.createIfcDirection((1.0, 0.0)),
    f.createIfcDirection((0.0, 1.0, 0.0)),
)
f.write(f"fail-axis2-2d-axis-ifc2x3.ifc")

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcAxis2Placement3D(
    f.createIfcCartesianPoint((0.0, 0.0)),
)
f.write(f"fail-axis2-2d-pos-ifc2x3.ifc")

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcAxis2Placement3D(
    f.createIfcCartesianPoint((0.0, 0.0, 0.0)),
    f.createIfcDirection((0.0, 0.0, 1.0)),
    f.createIfcDirection((1.0, 0.0)),
)
f.write(f"fail-axis2-2d-ref-ifc2x3.ifc")

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcAxis2Placement3D(
    f.createIfcCartesianPoint((0.0, 0.0, 0.0)),
    Axis=f.createIfcDirection((0.0, 0.0, 1.0)),
    RefDirection=f.createIfcDirection((0.0, 0.0, 1.0)),
)
f.write(f"fail-axis2-parallel-axes.ifc")

f = ifcopenshell.file(schema="IFC2X3")
f.createIfcAxis2Placement3D(
    f.createIfcCartesianPoint((0.0, 0.0, 0.0)),
    Axis=f.createIfcDirection((0.0, 0.0, 1.0)),
    RefDirection=f.createIfcDirection((0.0, 0.0, -1.0)),
)
f.write(f"fail-axis2-anti-parallel-axes.ifc")
