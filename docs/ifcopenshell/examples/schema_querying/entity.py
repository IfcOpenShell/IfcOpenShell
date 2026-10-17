# This file was generated with the assistance of an AI coding tool.
#
# Schema querying (Python): entity inheritance and attributes.

import ifcopenshell

ifc4 = ifcopenshell.schema_by_name("IFC4")
ifcwall = ifc4.declaration_by_name("IfcWall")

# tag::example
print(ifcwall.is_abstract()) # False
print(ifcwall.supertype()) # <entity IfcBuildingElement>
print(ifcwall.subtypes()) # (<entity IfcWallElementedCase>, <entity IfcWallStandardCase>)
# end::example

# tag::attributes
print(ifcwall.attributes())
print(ifcwall.all_attributes())
print(ifcwall.all_inverse_attributes())
# end::attributes

assert not ifcwall.is_abstract()
assert ifcwall.supertype().name() == "IfcBuildingElement"
assert len(ifcwall.all_attributes()) > len(ifcwall.attributes())
