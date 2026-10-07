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
    def _write_project(self, path, name: str) -> str:
        ifc = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject", name=name)
        ifc.write(str(path))
        return str(path)

    def test_preview_does_not_rebind_the_save_target(self, tmp_path):
        path = self._write_project(tmp_path / "preview.ifc", "Picked")

        bpy.ops.bim.load_project(filepath=path, is_advanced=True, should_start_fresh_session=False)

        assert tool.Blender.get_bim_props().ifc_file == ""
        assert tool.Project.get_project_props().advanced_load_filepath == path

    def test_preview_over_an_open_project_reads_the_picked_file(self, tmp_path):
        path = self._write_project(tmp_path / "preview.ifc", "Picked")
        bpy.ops.bim.create_project()

        bpy.ops.bim.load_project(filepath=path, is_advanced=True, should_start_fresh_session=False)

        assert tool.Ifc.get().by_type("IfcProject")[0].Name == "Picked"

    def test_loading_elements_binds_the_save_target(self, tmp_path):
        path = self._write_project(tmp_path / "loaded.ifc", "Picked")

        bpy.ops.bim.load_project(filepath=path, is_advanced=True, should_start_fresh_session=False)
        bpy.ops.bim.load_project_elements()

        assert tool.Blender.get_bim_props().ifc_file == path

    def test_geometry_only_import_never_becomes_the_save_target(self, tmp_path):
        path = self._write_project(tmp_path / "imported.ifc", "Picked")

        bpy.ops.bim.load_project(
            filepath=path, is_advanced=True, should_start_fresh_session=False, import_without_ifc_data=True
        )
        bpy.ops.bim.load_project_elements()

        assert tool.Blender.get_bim_props().ifc_file == ""
        assert tool.Ifc.get() is None
