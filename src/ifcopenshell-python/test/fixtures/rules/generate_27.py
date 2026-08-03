import ifcopenshell
from ...fixture_generate import normalize_header, write_fixture

ifc_file = ifcopenshell.file(schema="IFC2X3")
ifc_file.create_entity(
    "IfcCurveStyle",
    CurveWidth=ifc_file.create_entity("IfcDescriptiveMeasure", "by layer"),
)
normalize_header(ifc_file)
write_fixture(ifc_file, __file__, "pass", "IfcCurveStyle-ifc2x3")
