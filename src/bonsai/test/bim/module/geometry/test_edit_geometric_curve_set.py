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

import bpy
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.util.representation
from ifcopenshell.util.shape_builder import ShapeBuilder

import bonsai.core.geometry
import bonsai.tool as tool
from bonsai.bim.module.geometry.operator import OverrideModeSetObject
from test.bim.bootstrap import NewFile


class TestEditGeometricCurveSet(NewFile):
    def create_annotation(self, polylines, object_type=None):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        annotation = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcAnnotation", name="Curves")
        annotation.ObjectType = object_type
        context = ifcopenshell.util.representation.get_context(ifc, "Plan", "Annotation", "PLAN_VIEW")
        builder = ShapeBuilder(ifc)
        curve_set = ifc.createIfcGeometricCurveSet([builder.polyline(points) for points in polylines])
        representation = builder.get_representation(context, [curve_set])
        ifcopenshell.api.geometry.assign_representation(ifc, product=annotation, representation=representation)
        obj = bpy.data.objects.new("Curves", bpy.data.meshes.new("Curves"))
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(annotation, obj)
        bonsai.core.geometry.switch_representation(tool.Ifc, tool.Geometry, obj=obj, representation=representation)
        return annotation, obj, curve_set

    def enter_item_mode(self, obj, curve_set):
        props = tool.Geometry.get_geometry_props()
        props.representation_obj = obj
        item_obj = bpy.data.objects.new("Item", bpy.data.meshes.new("Item"))
        bpy.context.scene.collection.objects.link(item_obj)
        props.add_item_object(item_obj, curve_set)
        tool.Model.import_curve(curve_set, obj=item_obj)
        tool.Ifc.link(curve_set, item_obj.data)
        return item_obj

    def save_item(self, item_obj):
        operator = Mock()
        operator._is_annotation_object = lambda element: OverrideModeSetObject._is_annotation_object(operator, element)
        OverrideModeSetObject.edit_representation_item(operator, item_obj)

    def get_loops(self, curve_set):
        return [[tuple(p) for p in curve.Points.CoordList] for curve in curve_set.Elements]

    def test_curve_set_is_curvelike(self):
        annotation, obj, curve_set = self.create_annotation([[(0, 0), (1, 0)]])
        assert tool.Geometry.is_curvelike_item(curve_set)

    def test_curve_set_elements_become_separate_loops(self):
        annotation, obj, curve_set = self.create_annotation([[(0, 0), (1, 0)], [(0, 1), (1, 1)]])
        item_obj = self.enter_item_mode(obj, curve_set)
        assert len(item_obj.data.vertices) == 4
        assert len(item_obj.data.edges) == 2

    def test_saving_keeps_the_curve_set_and_replaces_its_elements(self):
        annotation, obj, curve_set = self.create_annotation([[(0, 0), (1, 0)], [(0, 1), (1, 1)]])
        item_obj = self.enter_item_mode(obj, curve_set)
        for vertex in item_obj.data.vertices:
            vertex.co.y += 2
        self.save_item(item_obj)
        ifc = tool.Ifc.get()
        assert ifc.by_id(curve_set.id()) == curve_set
        assert len(ifc.by_type("IfcGeometricCurveSet")) == 1
        assert len(ifc.by_type("IfcIndexedPolyCurve")) == 2
        loops = sorted(self.get_loops(curve_set))
        assert loops == [[(0.0, 2.0), (1.0, 2.0)], [(0.0, 3.0), (1.0, 3.0)]]
