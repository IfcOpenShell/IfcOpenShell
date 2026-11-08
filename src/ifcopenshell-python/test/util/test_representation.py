# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import numpy as np

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.representation as subject
import test.bootstrap


class TestGetReferenceLineIFC4(test.bootstrap.IFC4):
    def test_plan_axis_graph_view(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        plan = ifcopenshell.api.context.add_context(self.file, context_type="Plan")
        axis_ctx = ifcopenshell.api.context.add_context(
            self.file, context_type="Plan", context_identifier="Axis", target_view="GRAPH_VIEW", parent=plan
        )
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        polyline = self.file.createIfcPolyline(
            [self.file.createIfcCartesianPoint((0.0, 0.0)), self.file.createIfcCartesianPoint((4.5, 0.0))]
        )
        rep = self.file.createIfcShapeRepresentation(axis_ctx, "Axis", "Curve2D", [polyline])
        wall.Representation = self.file.createIfcProductDefinitionShape(None, None, [rep])

        ref = subject.get_reference_line(wall)
        assert np.allclose(ref[0], (0.0, 0.0))
        assert np.allclose(ref[1], (4.5, 0.0))

    def test_model_axis_graph_view(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        axis_ctx = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Axis", target_view="GRAPH_VIEW", parent=model
        )
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        polyline = self.file.createIfcPolyline(
            [self.file.createIfcCartesianPoint((0.0, 0.0)), self.file.createIfcCartesianPoint((5.0, 0.0))]
        )
        rep = self.file.createIfcShapeRepresentation(axis_ctx, "Axis", "Curve2D", [polyline])
        wall.Representation = self.file.createIfcProductDefinitionShape(None, None, [rep])

        ref = subject.get_reference_line(wall)
        assert np.allclose(ref[0], (0.0, 0.0))
        assert np.allclose(ref[1], (5.0, 0.0))

    def test_model_axis_model_view_with_3d_points(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        axis_ctx = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Axis", target_view="MODEL_VIEW", parent=model
        )
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        polyline = self.file.createIfcPolyline(
            [self.file.createIfcCartesianPoint((6.0, 0.0, 0.0)), self.file.createIfcCartesianPoint((1.0, 0.0, 0.0))]
        )
        rep = self.file.createIfcShapeRepresentation(axis_ctx, "Axis", "Curve3D", [polyline])
        wall.Representation = self.file.createIfcProductDefinitionShape(None, None, [rep])

        ref = subject.get_reference_line(wall)
        assert ref[0].shape == (2,)
        assert ref[1].shape == (2,)
        assert np.allclose(ref[0], (1.0, 0.0))
        assert np.allclose(ref[1], (6.0, 0.0))

    def test_extrusion_fallback_rectangle_profile(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body_ctx = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        profile = self.file.createIfcRectangleProfileDef(
            "AREA",
            None,
            self.file.createIfcAxis2Placement2D(self.file.createIfcCartesianPoint((2.5, 0.0)), None),
            5.0,
            0.2,
        )
        solid = self.file.createIfcExtrudedAreaSolid(
            profile, None, self.file.createIfcDirection((0.0, 0.0, 1.0)), 2.4
        )
        body_rep = self.file.createIfcShapeRepresentation(body_ctx, "Body", "SweptSolid", [solid])
        wall.Representation = self.file.createIfcProductDefinitionShape(None, None, [body_rep])

        ref = subject.get_reference_line(wall)
        assert np.allclose(ref[0], (0.0, 0.0))
        assert np.allclose(ref[1], (5.0, 0.0))

    def test_extrusion_fallback_composite_curve(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body_ctx = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        seg_pl = self.file.createIfcPolyline(
            [self.file.createIfcCartesianPoint((0.0, 0.0)), self.file.createIfcCartesianPoint((3.5, 0.0))]
        )
        seg = self.file.createIfcCompositeCurveSegment("CONTINUOUS", True, seg_pl)
        comp = self.file.createIfcCompositeCurve([seg], False)
        profile = self.file.createIfcArbitraryClosedProfileDef("AREA", None, comp)
        solid = self.file.createIfcExtrudedAreaSolid(
            profile, None, self.file.createIfcDirection((0.0, 0.0, 1.0)), 2.4
        )
        body_rep = self.file.createIfcShapeRepresentation(body_ctx, "Body", "SweptSolid", [solid])
        wall.Representation = self.file.createIfcProductDefinitionShape(None, None, [body_rep])

        ref = subject.get_reference_line(wall)
        assert np.allclose(ref[0], (0.0, 0.0))
        assert np.allclose(ref[1], (3.5, 0.0))

    def test_regenerate_wall_with_model_axis_representation(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file, length={"is_metric": True, "raw": "METERS"})
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body_ctx = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        axis_ctx = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Axis", target_view="GRAPH_VIEW", parent=model
        )
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall, matrix=np.eye(4))

        axis_pl = self.file.createIfcPolyline(
            [self.file.createIfcCartesianPoint((0.0, 0.0)), self.file.createIfcCartesianPoint((5.0, 0.0))]
        )
        axis_rep = self.file.createIfcShapeRepresentation(axis_ctx, "Axis", "Curve2D", [axis_pl])
        profile = self.file.createIfcRectangleProfileDef(
            "AREA",
            None,
            self.file.createIfcAxis2Placement2D(self.file.createIfcCartesianPoint((2.5, 0.0)), None),
            5.0,
            0.2,
        )
        solid = self.file.createIfcExtrudedAreaSolid(
            profile, None, self.file.createIfcDirection((0.0, 0.0, 1.0)), 2.4
        )
        body_rep = self.file.createIfcShapeRepresentation(body_ctx, "Body", "SweptSolid", [solid])
        wall.Representation = self.file.createIfcProductDefinitionShape(None, None, [axis_rep, body_rep])

        ms = ifcopenshell.api.material.add_material_set(self.file, name="w", set_type="IfcMaterialLayerSet")
        mat = ifcopenshell.api.material.add_material(self.file, name="m")
        layer = ifcopenshell.api.material.add_layer(self.file, layer_set=ms, material=mat)
        ifcopenshell.api.material.edit_layer(self.file, layer=layer, attributes={"LayerThickness": 0.2})
        ifcopenshell.api.material.assign_material(
            self.file, products=[wall], type="IfcMaterialLayerSetUsage", material=ms
        )

        ifcopenshell.api.geometry.regenerate_wall_representation(self.file, wall=wall)
        ref = subject.get_reference_line(wall)
        assert np.allclose(ref[0], (0.0, 0.0))
        assert np.allclose(ref[1], (5.0, 0.0))
        assert len(wall.Representation.Representations) == 2
