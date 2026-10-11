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

from unittest.mock import patch

import bpy
import ifcopenshell.geom

import bonsai.tool as tool
from bonsai.tool.model import Model as subject
from test.bim.bootstrap import NewFile


class TestExportProfile(NewFile):
    def test_a_degenerate_curve_is_an_invalid_profile(self):
        tool.Ifc.set(ifcopenshell.file(schema="IFC4"))
        mesh = bpy.data.meshes.new("Profile")
        mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], [(0, 1), (1, 2), (2, 3), (3, 0)], [])
        obj = bpy.data.objects.new("Profile", mesh)

        with patch.object(ifcopenshell.geom, "create_shape", side_effect=RuntimeError):
            assert subject.export_profile(obj) is None
