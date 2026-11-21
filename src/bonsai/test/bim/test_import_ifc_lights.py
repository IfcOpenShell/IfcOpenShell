# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.root

from bonsai.bim.import_ifc import IfcImporter
from test.bim.bootstrap import NewFile


class TestImportLights(NewFile):
    def test_light_fixture_becomes_a_blender_light(self):
        ifc = ifcopenshell.file(schema="IFC4")
        importer = IfcImporter.__new__(IfcImporter)
        fixture = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcLightFixture", name="Lamp")
        assert importer.is_light_element(fixture)
        light = importer.create_light(fixture)
        assert isinstance(light, bpy.types.Light)
        assert light.type == "POINT"

    def test_direction_source_becomes_a_sun(self):
        ifc = ifcopenshell.file(schema="IFC4")
        importer = IfcImporter.__new__(IfcImporter)
        fixture = ifcopenshell.api.root.create_entity(
            ifc, ifc_class="IfcLightFixture", name="Sun", predefined_type="DIRECTIONSOURCE"
        )
        assert importer.create_light(fixture).type == "SUN"
