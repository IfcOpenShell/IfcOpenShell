import ifcopenshell

ifc_file = ifcopenshell.file(schema="IFC2X3")
ifc_file.create_entity(
    "IfcCurveStyle",
    CurveWidth=ifc_file.create_entity("IfcDescriptiveMeasure", "by layer"),
)
ifc_file.write("pass-IfcCurveStyle-ifc2x3.ifc")
