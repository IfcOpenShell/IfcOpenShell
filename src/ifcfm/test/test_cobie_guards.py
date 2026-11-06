# This file was generated with the assistance of an AI coding tool.

import ifcfm.cobie24
import ifcfm.cobie24legacy
import ifcopenshell
import ifcopenshell.api.root
import pytest


@pytest.mark.parametrize("module", [ifcfm.cobie24, ifcfm.cobie24legacy])
class TestCobieGuards:
    def test_orphan_storey_is_not_a_floor(self, module):
        file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(file, ifc_class="IfcBuildingStorey")
        assert module.get_floors(file) == []

    def test_unit_type_name_without_units(self, module):
        file = ifcopenshell.file(schema="IFC4")
        assert module.get_unit_type_name(file, "LENGTHUNIT") is None
