import ifcopenshell
from generate import normalize_header

ifc_file = ifcopenshell.file(schema="IFC2X3")
ifc_file.create_entity(
    "IfcCurveStyle",
    CurveWidth=ifc_file.create_entity("IfcDescriptiveMeasure", "by layer"),
)
normalize_header(ifc_file)
ifc_file.write("pass-IfcCurveStyle-ifc2x3.ifc")
