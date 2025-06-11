# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

"""Run this test from src/ifcopenshell-python folder: pytest --durations=0 ifcopenshell/util/test_pset.py"""
from ifcopenshell.util import pset
from ifcopenshell import util
from ifcopenshell.util.pset import ApplicableEntity


class TestPsetQto:
    @classmethod
    def setup_class(cls):
        cls.pset_qto = pset.PsetQto("IFC4")

    def test_get_applicables(self):
        for i in range(1000):
            assert len(self.pset_qto.get_applicable("IfcMaterial")) == 9

    def test_get_applicables_names(self):
        for i in range(1000):
            assert len(self.pset_qto.get_applicable_names("IfcMaterial")) == 9

    def test_getting_applicables_for_a_specific_predefined_type(self):
        names = self.pset_qto.get_applicable_names("IfcAudioVisualAppliance")
        assert len(names) == 12
        assert "Pset_AudioVisualApplianceTypeAmplifier" not in names
        names = self.pset_qto.get_applicable_names("IfcAudioVisualAppliance", predefined_type="AMPLIFIER")
        assert "Pset_AudioVisualApplianceTypeAmplifier" in names
        assert len(names) == 13

    def test_getting_a_pset_of_a_type_where_the_type_class_is_not_explicitly_applicable(self):
        names = self.pset_qto.get_applicable_names("IfcWall")
        assert "Pset_WallCommon" in names
        names = self.pset_qto.get_applicable_names("IfcWallType")
        assert len(names) == 12
        assert "Pset_WallCommon" in names
        assert "Qto_WallBaseQuantities" in names  # Backported fix for IFC4

    def test_getting_applicable_names_by_predefined_type(self):
        names = self.pset_qto.get_applicable_names("IfcFurniture")
        assert "Pset_FurnitureTypeTable" not in names
        names = self.pset_qto.get_applicable_names("IfcFurniture", "TABLE")
        assert "Pset_FurnitureTypeTable" in names
        names = self.pset_qto.get_applicable_names("IfcFurnitureType", "TABLE")
        assert "Pset_FurnitureTypeTable" in names
        names = self.pset_qto.get_applicable_names("IfcFurnitureType")
        names2 = self.pset_qto.get_applicable_names("IfcFurnitureType", "CUSTOM")
        assert names == names2

    def test_getting_applicables_for_a_material_category(self):
        names = self.pset_qto.get_applicable_names("IfcMaterial")
        assert "Pset_MaterialConcrete" not in names
        names = self.pset_qto.get_applicable_names("IfcMaterial", "concrete")
        assert "Pset_MaterialConcrete" in names


class TestParseApplicableEntity:
    def test_run(self):
        assert pset.parse_applicable_entity("IfcBoilerType") == [
            ApplicableEntity("IfcBoilerType", "IfcBoilerType", None, False)
        ]

    def test_two_entities(self):
        assert pset.parse_applicable_entity("IfcBoilerType,IfcWallType") == [
            ApplicableEntity("IfcBoilerType", "IfcBoilerType", None, False),
            ApplicableEntity("IfcWallType", "IfcWallType", None, False),
        ]

    def test_two_entities_with_performance_history(self):
        assert pset.parse_applicable_entity("IfcBoilerType[PerformanceHistory],IfcWallType") == [
            ApplicableEntity("IfcBoilerType[PerformanceHistory]", "IfcBoilerType", None, True),
            ApplicableEntity("IfcWallType", "IfcWallType", None, False),
        ]

    def test_two_entities_with_predefined_type(self):
        assert pset.parse_applicable_entity("IfcBoilerType/STEAM,IfcWallType") == [
            ApplicableEntity("IfcBoilerType/STEAM", "IfcBoilerType", "STEAM", False),
            ApplicableEntity("IfcWallType", "IfcWallType", None, False),
        ]

    def test_two_entities_with_predefined_type_and_performance_history(self):
        assert pset.parse_applicable_entity("IfcBoilerType[PerformanceHistory]/STEAM,IfcWallType") == [
            ApplicableEntity("IfcBoilerType[PerformanceHistory]/STEAM", "IfcBoilerType", "STEAM", True),
            ApplicableEntity("IfcWallType", "IfcWallType", None, False),
        ]


class TestConvertApplicableEntitiesToQuery:
    def test_run(self):
        entities = [ApplicableEntity("IfcBoilerType", "IfcBoilerType", None, False)]
        assert pset.convert_applicable_entities_to_query(entities) == "IfcBoilerType"

    def test_two_entities(self):
        entities = [
            ApplicableEntity("IfcBoilerType", "IfcBoilerType", None, False),
            ApplicableEntity("IfcWallType", "IfcWallType", None, False),
        ]
        assert pset.convert_applicable_entities_to_query(entities) == "IfcBoilerType + IfcWallType"

    def test_two_entities_with_performance_history(self):
        entities = [
            ApplicableEntity("IfcBoilerType[PerformanceHistory]", "IfcBoilerType", None, True),
            ApplicableEntity("IfcWallType", "IfcWallType", None, False),
        ]
        assert pset.convert_applicable_entities_to_query(entities) == "IfcBoilerType + IfcWallType"

    def test_two_entities_with_predefined_type(self):
        entities = [
            ApplicableEntity("IfcBoilerType/STEAM", "IfcBoilerType", "STEAM", False),
            ApplicableEntity("IfcWallType", "IfcWallType", None, False),
        ]
        assert (
            pset.convert_applicable_entities_to_query(entities) == 'IfcBoilerType, PredefinedType="STEAM" + IfcWallType'
        )

    def test_two_entities_with_predefined_type_and_performance_history(self):
        entities = [
            ApplicableEntity("IfcBoilerType[PerformanceHistory]/STEAM", "IfcBoilerType", "STEAM", True),
            ApplicableEntity("IfcWallType", "IfcWallType", None, False),
        ]
        assert (
            pset.convert_applicable_entities_to_query(entities) == 'IfcBoilerType, PredefinedType="STEAM" + IfcWallType'
        )
