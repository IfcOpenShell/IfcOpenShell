# This file was generated with the assistance of an AI coding tool.
#
# Schema querying (Python): schema declarations.

# tag::example
import ifcopenshell
ifc4 = ifcopenshell.schema_by_name("IFC4")
# end::example

# tag::loop
for declaration in ifc4.declarations():
    print(declaration.name()) # 'IfcAbsorbedDoseMeasure', 'IfcAccelerationMeasure', 'IfcActionRequest', ...

ifcwall = ifc4.declaration_by_name("IfcWall")
# end::loop

assert ifcwall.name() == "IfcWall"
