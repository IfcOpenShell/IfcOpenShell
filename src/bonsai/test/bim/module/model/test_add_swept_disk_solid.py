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
import ifcopenshell.util.representation
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestAddSweptDiskSolid(NewFile):
    def test_adding_a_swept_disk_solid_creates_a_proxy_with_a_single_swept_disk_body_item(self):
        bpy.ops.bim.create_project()
        bpy.ops.mesh.add_swept_disk_solid(radius=0.05)
        element = tool.Ifc.get_entity(bpy.context.active_object)
        assert element.is_a("IfcBuildingElementProxy")
        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        assert [item.is_a() for item in body.Items] == ["IfcSweptDiskSolid"]
        assert body.Items[0].Radius == pytest.approx(0.05)

    def test_the_directrix_curve_of_a_swept_disk_solid_is_a_single_spline(self):
        bpy.ops.bim.create_project()
        bpy.ops.mesh.add_swept_disk_solid()
        obj = bpy.context.active_object
        body = ifcopenshell.util.representation.get_representation(
            tool.Ifc.get_entity(obj), "Model", "Body", "MODEL_VIEW"
        )
        tool.Loader.load_settings()
        bpy.ops.bim.switch_representation(obj=obj.name, ifc_definition_id=body.id())
        obj = bpy.context.active_object
        assert [len(spline.points) for spline in obj.data.splines] == [2]
