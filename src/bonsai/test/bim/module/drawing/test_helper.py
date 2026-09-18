# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

import types

import bpy
import ifcopenshell
import ifcopenshell.api.unit
import ifcopenshell.guid
import pytest

import bonsai.tool as tool
from bonsai.bim.module.drawing import helper
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.drawing


@pytest.fixture(autouse=True)
def _require_real_bpy():
    if not isinstance(bpy, types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


class TestFormatDistanceNamelessLengthUnit(NewFile):
    def test_it_does_not_crash_and_warns_once(self, caplog):
        ifc = ifcopenshell.file(schema="IFC4")
        ifc.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new())
        tool.Ifc.set(ifc)
        # A schema-non-conformant LENGTHUNIT with no Name, as produced by some
        # third-party exporters (#8885). ifcopenshell.file permits this on
        # creation even though IfcSIUnit.Name is not officially optional.
        length_unit = ifc.create_entity("IfcSIUnit", UnitType="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_unit])
        helper._warned_nameless_length_units.clear()

        with caplog.at_level("WARNING", logger="bonsai.bim.module.drawing.helper"):
            result = helper.format_distance(3.0)
            helper.format_distance(3.0)

        assert isinstance(result, str)
        warnings = [r for r in caplog.records if "IfcSIUnit" in r.message]
        assert len(warnings) == 1, "expected exactly one warning across both calls"

    def test_it_still_formats_when_length_unit_has_a_name(self, caplog):
        ifc = ifcopenshell.file(schema="IFC4")
        ifc.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new())
        tool.Ifc.set(ifc)
        length_unit = ifc.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Name="METRE")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_unit])
        helper._warned_nameless_length_units.clear()

        with caplog.at_level("WARNING", logger="bonsai.bim.module.drawing.helper"):
            result = helper.format_distance(3.0)

        assert "3" in result
        assert not [r for r in caplog.records if "IfcSIUnit" in r.message]
