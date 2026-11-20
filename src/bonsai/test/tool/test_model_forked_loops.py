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

import bpy
import ifcopenshell

import bonsai.tool as tool
from bonsai.tool.model import Model as subject
from test.bim.bootstrap import NewFile


def make_forked_mesh_object():
    tool.Ifc.set(ifcopenshell.file())
    mesh = bpy.data.meshes.new("Fork")
    mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0), (-1, 0, 0)], [(0, 1), (0, 2), (0, 3)], [])
    return bpy.data.objects.new("Fork", mesh)


class TestAutoDetectProfiles(NewFile):
    def test_forked_edges_are_reported_as_an_invalid_profile(self):
        obj = make_forked_mesh_object()
        assert subject.auto_detect_profiles(obj, obj.data) == (False, "UNCLOSED_LOOP")


class TestAutoDetectCurves(NewFile):
    def test_forked_edges_are_reported_as_invalid_curves(self):
        obj = make_forked_mesh_object()
        assert subject.auto_detect_curves(obj, obj.data) == (False, "UNCLOSED_LOOP")
