import ifcopenshell
from ...fixture_generate import fail_if, normalize_header, write_fixture

create_plane = lambda f: f.createIfcPlane(f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0))))
create_polyline = lambda f: f.createIfcPolyline(
    (f.createIfcCartesianPoint((0.0, 0.0)), f.createIfcCartesianPoint((1.0, 0.0)))
)

for i, make_item in enumerate((create_plane, create_polyline)):
    f = ifcopenshell.file(schema="IFC2X3")
    inst = f.createIfcAnnotationSurface(make_item(f))
    normalize_header(f)
    write_fixture(f, __file__, fail_if(i == 1), f"annotation-surface-{inst.Item.is_a()}-ifc2x3")
