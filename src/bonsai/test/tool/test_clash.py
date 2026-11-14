# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell
import pytest

import bonsai.tool as tool
from bonsai.tool.clash import Clash as subject
from test.bim.bootstrap import NewFile


class TestConvertClashPointToBlender(NewFile):
    def test_return_the_point_as_is_without_a_false_origin(self):
        tool.Ifc.set(ifcopenshell.file())
        assert tuple(subject.convert_clash_point_to_blender([105.0, 20.0, 3.0])) == (105.0, 20.0, 3.0)

    def test_subtract_the_false_origin(self):
        tool.Ifc.set(ifcopenshell.file())
        props = tool.Georeference.get_georeference_props()
        props.has_blender_offset = True
        props.blender_offset_x = "100.0"
        props.blender_offset_y = "10.0"
        props.blender_offset_z = "1.0"
        props.blender_x_axis_abscissa = "1.0"
        props.blender_x_axis_ordinate = "0.0"
        assert tuple(subject.convert_clash_point_to_blender([105.0, 20.0, 3.0])) == pytest.approx((5.0, 10.0, 2.0))
