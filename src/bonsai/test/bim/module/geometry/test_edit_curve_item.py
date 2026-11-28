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

from unittest.mock import Mock

import bmesh
import bpy
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import numpy as np
from ifcopenshell.util.shape_builder import ShapeBuilder

import bonsai.core.geometry
import bonsai.tool as tool
from bonsai.bim.module.geometry.operator import OverrideModeSetObject
from test.bim.bootstrap import NewFile

POINTS_3D = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.5), (2.0, 0.0, 1.0)]
POINTS_2D = [(0.0, 0.0), (1.0, 0.0), (2.0, 1.0)]


class TestEditCurveItem(NewFile):
    def edit_curve(self, points):
        return self.edit_item(lambda ifc: ShapeBuilder(ifc).polyline(points))

    def edit_circle(self):
        return self.edit_item(
            lambda ifc: ifc.createIfcCircle(
                ifc.createIfcAxis2Placement3D(
                    ifc.createIfcCartesianPoint((2.0, 3.0, 1.5)),
                    ifc.createIfcDirection((0.5, 0.0, 0.75**0.5)),
                    ifc.createIfcDirection((0.75**0.5, 0.0, -0.5)),
                ),
                1.0,
            )
        )

    def edit_item(self, create_item):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBuildingElementProxy")
        context = ifcopenshell.util.representation.get_context(ifc, "Model", "Body", "MODEL_VIEW")
        builder = ShapeBuilder(ifc)
        representation = builder.get_representation(context, [create_item(ifc)])
        ifcopenshell.api.geometry.assign_representation(ifc, product=element, representation=representation)
        obj = bpy.data.objects.new("Curve", bpy.data.meshes.new("Curve"))
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(element, obj)
        bonsai.core.geometry.switch_representation(tool.Ifc, tool.Geometry, obj=obj, representation=representation)
        tool.Blender.select_and_activate_single_object(bpy.context, obj)
        bpy.ops.bim.override_mode_set_edit()
        item_obj = tool.Geometry.get_geometry_props().item_objs[0].obj
        tool.Blender.select_and_activate_single_object(bpy.context, item_obj)
        bpy.ops.bim.override_mode_set_edit()
        assert bpy.context.mode == "EDIT_MESH"
        return element, item_obj

    def save_with_tab(self, item_obj):
        bpy.ops.object.mode_set(mode="OBJECT")
        operator = Mock()
        operator._is_annotation_object = lambda element: False
        OverrideModeSetObject.edit_representation_item(operator, item_obj)

    def get_points(self, element):
        curve = element.Representation.Representations[0].Items[0]
        return sorted(tuple(round(c, 3) for c in p) for p in curve.Points.CoordList)

    def is_circle(self, element, location):
        circle = element.Representation.Representations[0].Items[0]
        placement = ifcopenshell.util.placement.get_axis2placement(circle.Position)
        expected = [(0.75**0.5, 0.0, -0.5), (0.0, 1.0, 0.0), (0.5, 0.0, 0.75**0.5), location]
        return np.isclose(circle.Radius, 1.0) and np.allclose(placement[:3].T, expected, atol=1e-6)

    def test_tab_leaves_a_3d_curve_unchanged(self):
        element, item_obj = self.edit_curve(POINTS_3D)
        self.save_with_tab(item_obj)
        assert self.get_points(element) == POINTS_3D

    def test_space_leaves_a_3d_curve_unchanged(self):
        element, item_obj = self.edit_curve(POINTS_3D)
        bpy.ops.bim.direct_profile_edit()
        assert self.get_points(element) == POINTS_3D

    def test_tab_saves_a_point_moved_in_z(self):
        element, item_obj = self.edit_curve(POINTS_3D)
        bm = bmesh.from_edit_mesh(item_obj.data)
        max(bm.verts, key=lambda v: v.co.x).co.z += 0.25 * ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        bmesh.update_edit_mesh(item_obj.data)
        self.save_with_tab(item_obj)
        assert self.get_points(element) == [*POINTS_3D[:2], (2.0, 0.0, 1.25)]

    def test_tab_leaves_a_2d_curve_unchanged(self):
        element, item_obj = self.edit_curve(POINTS_2D)
        self.save_with_tab(item_obj)
        assert self.get_points(element) == POINTS_2D

    def test_tab_leaves_a_tilted_circle_unchanged(self):
        element, item_obj = self.edit_circle()
        self.save_with_tab(item_obj)
        assert self.is_circle(element, (2.0, 3.0, 1.5))

    def test_space_leaves_a_tilted_circle_unchanged(self):
        element, item_obj = self.edit_circle()
        bpy.ops.bim.direct_profile_edit()
        assert self.is_circle(element, (2.0, 3.0, 1.5))

    def test_tab_saves_a_tilted_circle_moved_in_z(self):
        element, item_obj = self.edit_circle()
        bm = bmesh.from_edit_mesh(item_obj.data)
        for vert in bm.verts:
            vert.co.z += 0.25 * ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        bmesh.update_edit_mesh(item_obj.data)
        self.save_with_tab(item_obj)
        assert self.is_circle(element, (2.0, 3.0, 1.75))
