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

import math

import bpy
import ifcopenshell.util.element
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestConvertToParametricWall(NewFile):
    def test_a_rotated_solid_wall_becomes_a_layered_wall(self):
        bpy.ops.bim.create_project()
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        obj.dimensions = (4.0, 0.3, 3.0)
        bpy.ops.object.transform_apply(scale=True)
        obj.rotation_euler.z = math.radians(30)
        obj.location = (1.0, 2.0, 0.0)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcWall")

        bpy.ops.bim.convert_to_parametric_wall()

        element = tool.Ifc.get_entity(obj)
        assert tool.Model.get_usage_type(element) == "LAYER2"
        layer_set = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        assert layer_set.MaterialLayers[0].LayerThickness == pytest.approx(0.3)
        assert ifcopenshell.util.element.get_pset(element, "EPset_Parametric", "Engine") == "Bonsai.DumbLayer2"
        assert tuple(obj.dimensions) == pytest.approx((4.0, 0.3, 3.0))
