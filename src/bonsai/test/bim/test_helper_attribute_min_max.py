# This file was generated with the assistance of an AI coding tool.
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

import ifcopenshell

import bonsai.bim.helper
import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestImportAttributes(NewFile):
    def test_a_positive_length_cannot_be_set_to_zero(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        circle = ifc.createIfcCircleProfileDef("AREA", None, None, 1.0)
        attributes = tool.Layer.get_layer_props().layer_attributes

        bonsai.bim.helper.import_attributes(circle, attributes)
        attributes["Radius"].float_value = 0.0

        assert attributes["Radius"].float_value > 0.0
