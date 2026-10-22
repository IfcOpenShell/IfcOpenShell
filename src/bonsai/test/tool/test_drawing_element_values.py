# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.type

from bonsai.bim.module.drawing.data import DecoratorData, ElementValuesData


def test_a_typed_ifc2x3_element_does_not_count_zero_occurrences_of_its_type():
    ifc = ifcopenshell.file(schema="IFC2X3")
    person = ifc.createIfcPerson()
    organisation = ifc.createIfcOrganization()
    ifc.createIfcPersonAndOrganization(ThePerson=person, TheOrganization=organisation)
    ifc.createIfcApplication(
        ApplicationDeveloper=organisation, Version="1", ApplicationFullName="Test", ApplicationIdentifier="Test"
    )
    wall_type = ifc.createIfcWallType(Name="Type A")
    walls = [ifc.createIfcWall(), ifc.createIfcWall()]
    ifcopenshell.api.type.assign_type(ifc, related_objects=walls, relating_type=wall_type)
    assert DecoratorData.get_element_value_by_key(walls[0], "types.count") != 0
    assert ("types.count", "Type Occurrence Count: 0") not in ElementValuesData._get_type_keys(walls[0])


def test_type_keys_of_a_typed_ifc2x3_element():
    ifc = ifcopenshell.file(schema="IFC2X3")
    person = ifc.createIfcPerson()
    organisation = ifc.createIfcOrganization()
    ifc.createIfcPersonAndOrganization(ThePerson=person, TheOrganization=organisation)
    ifc.createIfcApplication(
        ApplicationDeveloper=organisation, Version="1", ApplicationFullName="Test", ApplicationIdentifier="Test"
    )
    wall_type = ifc.createIfcWallType(Name="Type A")
    wall = ifc.createIfcWall()
    ifcopenshell.api.type.assign_type(ifc, related_objects=[wall], relating_type=wall_type)
    assert ("type.Name", "Type Name: Type A") in ElementValuesData._get_type_keys(wall)
