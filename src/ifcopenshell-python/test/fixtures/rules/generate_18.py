import ifcopenshell

for i, type_decl in enumerate(("IfcLengthMeasure", "IfcPlaneAngleMeasure")):
    f = ifcopenshell.file(schema="IFC4X3_ADD1")
    f.createIfcRigidOperation(
        SourceCRS=f.createIfcGeographicCRS("EPSG:4326"),
        TargetCRS=f.createIfcGeographicCRS("EPSG:3857"),
        FirstCoordinate=f.create_entity(type_decl, 0.0),
        SecondCoordinate=f.create_entity("IfcPlaneAngleMeasure", 0.0),
        Height=0.0,
    )
    f.write(f"{'pass' if i else 'fail'}-rigid-op-IfcPlaneAngleMeasure-{type_decl}-ifc4x3_add1.ifc")
