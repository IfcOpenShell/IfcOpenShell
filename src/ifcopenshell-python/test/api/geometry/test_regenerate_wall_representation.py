# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Alexey Tkachenko
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

# This file was written with the help of Claude Code.

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.representation
import test.bootstrap


class TestRegenerateWallRepresentation(test.bootstrap.IFC4):
    def setup_wall(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file, length={"is_metric": True, "raw": "METERS"})
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        plan = ifcopenshell.api.context.add_context(self.file, context_type="Plan")
        self.axis_context = ifcopenshell.api.context.add_context(
            self.file, context_type="Plan", context_identifier="Axis", target_view="GRAPH_VIEW", parent=plan
        )
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall)
        layer_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialLayerSet")
        material = ifcopenshell.api.material.add_material(self.file)
        layer = ifcopenshell.api.material.add_layer(self.file, layer_set=layer_set, material=material)
        layer.LayerThickness = 0.2
        ifcopenshell.api.material.assign_material(
            self.file, products=[wall], type="IfcMaterialLayerSetUsage", material=layer_set
        )
        return wall

    def assign_axis(self, wall, curve):
        representation = self.file.createIfcShapeRepresentation(self.axis_context, "Axis", "Curve2D", [curve])
        ifcopenshell.api.geometry.assign_representation(self.file, product=wall, representation=representation)
        return representation

    def get_axis(self, wall):
        return ifcopenshell.util.representation.get_representation(wall, "Plan", "Axis", "GRAPH_VIEW")

    def test_regenerating_a_wall_with_a_straight_axis(self):
        wall = self.setup_wall()
        points = [self.file.createIfcCartesianPoint((0.0, 0.0)), self.file.createIfcCartesianPoint((4.0, 0.0))]
        self.assign_axis(wall, self.file.createIfcPolyline(points))
        assert ifcopenshell.api.geometry.regenerate_wall_representation(self.file, wall=wall)
        assert ifcopenshell.util.representation.get_representation(wall, "Model", "Body", "MODEL_VIEW")

    def test_leaving_a_wall_with_a_trimmed_curve_axis_unchanged(self):
        wall = self.setup_wall()
        position = self.file.createIfcAxis2Placement2D(self.file.createIfcCartesianPoint((0.0, 0.0)))
        circle = self.file.createIfcCircle(position, 3.0)
        trim1 = [self.file.createIfcParameterValue(0.0)]
        trim2 = [self.file.createIfcParameterValue(90.0)]
        arc = self.file.createIfcTrimmedCurve(circle, trim1, trim2, True, "PARAMETER")
        axis = self.assign_axis(wall, arc)
        assert ifcopenshell.api.geometry.regenerate_wall_representation(self.file, wall=wall) is None
        assert self.get_axis(wall) == axis
        assert axis.Items == (arc,)
        assert not ifcopenshell.util.representation.get_representation(wall, "Model", "Body", "MODEL_VIEW")

    def test_leaving_a_wall_with_an_arc_segment_in_its_axis_unchanged(self):
        wall = self.setup_wall()
        points = self.file.createIfcCartesianPointList2D(((3.0, 0.0), (2.12132, 2.12132), (0.0, 3.0)))
        arc = self.file.createIfcIndexedPolyCurve(points, [self.file.createIfcArcIndex((1, 2, 3))], False)
        axis = self.assign_axis(wall, arc)
        assert ifcopenshell.api.geometry.regenerate_wall_representation(self.file, wall=wall) is None
        assert self.get_axis(wall) == axis
        assert axis.Items == (arc,)
        assert not ifcopenshell.util.representation.get_representation(wall, "Model", "Body", "MODEL_VIEW")
