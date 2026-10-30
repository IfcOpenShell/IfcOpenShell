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
import ifcopenshell.util.element
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.type


class TestConvertToType(NewFile):
    def test_untyped_occurrence_gets_a_new_type_with_its_geometry(self):
        tool.Project.get_project_props().template_file = "IFC4 Demo Template.ifc"
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()
        wall_type = ifc_file.by_type("IfcWallType")[0]
        bpy.ops.bim.add_occurrence(relating_type_id=wall_type.id())
        wall = ifc_file.by_type("IfcWall")[0]
        obj = tool.Ifc.get_object(wall)
        tool.Blender.set_objects_selection(bpy.context, obj, (obj,))
        bpy.ops.bim.unassign_type()
        assert ifcopenshell.util.element.get_type(wall) is None

        assert bpy.ops.bim.convert_to_type(name="Converted") == {"FINISHED"}

        new_type = ifcopenshell.util.element.get_type(wall)
        assert new_type.is_a("IfcWallType")
        assert new_type.Name == "Converted"
        assert new_type.RepresentationMaps
