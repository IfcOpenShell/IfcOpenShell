# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import os
import bpy
import ifcopenshell
import bonsai.core.tool
import bonsai.tool as tool
from test.bim.bootstrap import NewFile
from bonsai.tool.polyline import Polyline as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Polyline)


class TestValidateInput(NewFile):
    def test_simple_units(self):
        unit_settings = bpy.context.scene.unit_settings
        unit_settings.system = "METRIC"
        unit_settings.length_unit = "METERS"
        assert subject.validate_input("25", "D") == (True, "25.0")
        unit_settings.length_unit = "MILLIMETERS"
        assert subject.validate_input("25", "D") == (True, "0.025")

        unit_settings.system = "IMPERIAL"
        assert subject.validate_input("25", "D") == (True, "7.62")
        assert subject.validate_input("25'", "D") == (True, "7.62")
        assert subject.validate_input('25"', "D") == (True, "0.635")

        # Angle.
        assert subject.validate_input("25", "A") == (True, "25.0")
