# This file was generated with the assistance of an AI coding tool.
#
# Schema querying (Python): enumerations and select types.

import ifcopenshell

ifc4 = ifcopenshell.schema_by_name("IFC4")

# tag::example
wall_types = ifc4.declaration_by_name("IfcWallTypeEnum")
# ('MOVABLE', 'PARAPET', 'PARTITIONING', 'PLUMBINGWALL', ...)
print(wall_types.enumeration_items())

units = ifc4.declaration_by_name("IfcUnit")
# (<entity IfcDerivedUnit>, <entity IfcMonetaryUnit>, <type IfcNamedUnit>)
print(units.select_list())
# end::example

assert "PARAPET" in wall_types.enumeration_items()
assert "IfcNamedUnit" in [item.name() for item in units.select_list()]
