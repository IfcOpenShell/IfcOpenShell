# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import pytest

from test.bim.bootstrap import NewFile


class TestAddAnnotationRepresentation(NewFile):
    @pytest.mark.parametrize("schema", ["IFC4", "IFC2X3"])
    def test_splines_sharing_an_anchor_stay_separate_curves(self, schema):
        ifc = ifcopenshell.file(schema=schema)
        ifcopenshell.api.root.create_entity(ifc, "IfcProject")
        plan = ifcopenshell.api.context.add_context(ifc, context_type="Plan")
        context = ifcopenshell.api.context.add_context(
            ifc, context_type="Plan", context_identifier="Annotation", target_view="PLAN_VIEW", parent=plan
        )
        curve = bpy.data.curves.new("Leader", "CURVE")
        curve.dimensions = "3D"
        tips = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-1.0, -1.0, 0.0)]
        for tip in tips:
            spline = curve.splines.new("POLY")
            spline.points.add(1)
            spline.points[0].co = (0.0, 0.0, 0.0, 1.0)
            spline.points[1].co = (*tip, 1.0)
        obj = bpy.data.objects.new("Leader", curve)
        bpy.context.scene.collection.objects.link(obj)
        representation = ifcopenshell.api.geometry.add_representation(
            ifc, context=context, blender_object=obj, geometry=curve
        )
        curve_set = next(i for i in representation.Items if i.is_a("IfcGeometricCurveSet"))
        assert len(curve_set.Elements) == 3
        for element, tip in zip(curve_set.Elements, tips):
            if element.is_a("IfcPolyline"):
                points = [tuple(p.Coordinates) for p in element.Points]
            else:
                points = [tuple(p) for p in element.Points.CoordList]
            assert points == [(0.0, 0.0), tip[:2]]
