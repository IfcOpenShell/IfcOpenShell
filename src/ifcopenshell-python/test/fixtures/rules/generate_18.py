import ifcopenshell
from generate import normalize_header, pass_if, write_fixture

for i, type_decl in enumerate(("IfcLengthMeasure", "IfcPlaneAngleMeasure")):
    f = ifcopenshell.file(schema="IFC4X3")
    f.createIfcRigidOperation(
        SourceCRS=f.createIfcGeographicCRS("EPSG:4326"),
        TargetCRS=f.createIfcGeographicCRS("EPSG:3857"),
        FirstCoordinate=f.create_entity(type_decl, 0.0),
        SecondCoordinate=f.create_entity("IfcPlaneAngleMeasure", 0.0),
        Height=0.0,
    )
    normalize_header(f)
    write_fixture(f, __file__, pass_if(bool(i)), f"rigid-op-IfcPlaneAngleMeasure-{type_decl}-ifc4x3")
