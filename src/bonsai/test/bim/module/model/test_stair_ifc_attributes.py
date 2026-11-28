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

# This file was generated with the assistance of an AI coding tool.

import bpy
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile, NewIfc4X3

pytestmark = pytest.mark.model


def _add_stair_flight() -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    bpy.ops.bim.assign_class(ifc_class="IfcStairFlight", predefined_type="STRAIGHT", userdefined_type="")
    bpy.ops.bim.add_stair()
    return obj


class TestStairFlightAttributesIfc4(NewFile):
    def test_deprecated_attributes_are_written(self):
        bpy.ops.bim.create_project()
        flight = tool.Ifc.get_entity(_add_stair_flight())
        assert flight.NumberOfRisers
        assert flight.NumberOfTreads
        assert flight.RiserHeight
        assert flight.TreadLength


class TestStairFlightAttributesIfc4X3(NewIfc4X3):
    def test_deprecated_attributes_are_left_empty(self):
        flight = tool.Ifc.get_entity(_add_stair_flight())
        assert flight.NumberOfRisers is None
        assert flight.NumberOfTreads is None
        assert flight.RiserHeight is None
        assert flight.TreadLength is None
