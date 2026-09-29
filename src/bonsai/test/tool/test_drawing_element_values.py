# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.type

from bonsai.bim.module.drawing.data import ElementValuesData


def test_type_keys_of_a_typed_ifc2x3_element():
    ifc = ifcopenshell.file(schema="IFC2X3")
    wall_type = ifc.createIfcWallType(Name="Type A")
    wall = ifc.createIfcWall()
    ifcopenshell.api.type.assign_type(ifc, related_objects=[wall], relating_type=wall_type)
    assert ("type.Name", "Type Name: Type A") in ElementValuesData._get_type_keys(wall)
