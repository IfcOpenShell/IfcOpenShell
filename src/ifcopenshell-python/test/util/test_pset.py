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


class TestPsetQto:
    @classmethod
    def setup_class(cls):
        cls.pset_qto = util.pset.PsetQto("IFC4")

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
        assert len(names) == 5
        assert "Pset_WallCommon" in names
