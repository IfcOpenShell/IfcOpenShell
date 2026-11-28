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

from types import SimpleNamespace

import bpy

from bonsai.bim.module.geometry.ui import object_menu
from test.bim.bootstrap import NewFile


class RecordingLayout:
    def __init__(self):
        self.operators = []

    def operator(self, idname, **kwargs):
        self.operators.append(idname)

    def separator(self):
        pass

    def menu(self, idname, **kwargs):
        pass


class TestObjectMenu(NewFile):
    def test_ifc_join_is_offered_in_the_object_menu(self):
        layout = RecordingLayout()
        object_menu(SimpleNamespace(layout=layout), bpy.context)
        assert "bim.override_object_join" in layout.operators
