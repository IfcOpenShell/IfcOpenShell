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
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.project


class TestExportSelectedElements(NewFile):
    def test_only_the_selected_element_is_written(self, tmp_path):
        tool.Project.get_project_props().template_file = "IFC4 Demo Template.ifc"
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()
        wall_type = next(t for t in ifc_file.by_type("IfcWallType"))
        bpy.ops.bim.add_occurrence(relating_type_id=wall_type.id())
        bpy.ops.bim.add_occurrence(relating_type_id=wall_type.id())
        walls = ifc_file.by_type("IfcWall")
        assert len(walls) == 2
        obj = tool.Ifc.get_object(walls[0])
        tool.Blender.set_objects_selection(bpy.context, obj, (obj,))
        output = tmp_path / "selected.ifc"

        assert bpy.ops.bim.export_selected_elements(filepath=str(output)) == {"FINISHED"}

        exported = ifcopenshell.open(str(output))
        assert [w.GlobalId for w in exported.by_type("IfcWall")] == [walls[0].GlobalId]
