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

import bpy
import ifcopenshell
import ifcopenshell.api.root

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestLoadProjectAdvanced(NewFile):
    def test_preview_does_not_rebind_the_save_target(self, tmp_path):
        path = tmp_path / "preview.ifc"
        ifc = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifc.write(str(path))
        tool.Blender.get_bim_props().ifc_file = "/original.ifc"

        bpy.ops.bim.load_project(filepath=str(path), is_advanced=True, should_start_fresh_session=False)

        assert tool.Blender.get_bim_props().ifc_file == "/original.ifc"
        assert tool.Project.get_project_props().advanced_load_filepath == str(path)
