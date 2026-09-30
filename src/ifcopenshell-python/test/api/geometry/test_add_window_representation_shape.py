# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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
#
# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.util.shape
import test.bootstrap


class TestAddWindowRepresentationShape(test.bootstrap.IFC4):
    def setup_context(self) -> None:
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix=None)
        ifcopenshell.api.unit.assign_unit(self.file, [unit])
        model_context = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        self.body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_context
        )

    def get_bbox(self, representation: ifcopenshell.entity_instance):
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, representation)
        verts = ifcopenshell.util.shape.get_vertices(shape)
        return ifcopenshell.util.shape.get_bbox(verts)

    def test_round_window_is_a_circle_of_the_overall_width(self):
        self.setup_context()
        representation = ifcopenshell.api.geometry.add_window_representation(
            self.file, context=self.body, overall_width=1.0, overall_height=2.0, window_shape="ROUND"
        )
        (min_x, _, min_z), (max_x, _, max_z) = self.get_bbox(representation)
        assert max_x - min_x == pytest.approx(1.0, abs=1e-3)
        assert max_z - min_z == pytest.approx(1.0, abs=1e-3)

    def test_round_window_uses_circle_profiles(self):
        self.setup_context()
        ifcopenshell.api.geometry.add_window_representation(self.file, context=self.body, window_shape="ROUND")
        assert self.file.by_type("IfcCircleHollowProfileDef")
        assert self.file.by_type("IfcCircleProfileDef")

    def test_arch_window_apex_is_at_the_overall_height(self):
        self.setup_context()
        representation = ifcopenshell.api.geometry.add_window_representation(
            self.file, context=self.body, overall_width=1.0, overall_height=1.6, window_shape="ARCH"
        )
        (min_x, _, min_z), (max_x, _, max_z) = self.get_bbox(representation)
        assert max_x - min_x == pytest.approx(1.0, abs=1e-3)
        assert max_z - min_z == pytest.approx(1.6, abs=1e-3)

    def test_arch_window_adds_one_extra_framing_item_per_muntin(self):
        self.setup_context()
        few = ifcopenshell.api.geometry.add_window_representation(
            self.file, context=self.body, window_shape="ARCH", arch_muntin_count=2
        )
        many = ifcopenshell.api.geometry.add_window_representation(
            self.file, context=self.body, window_shape="ARCH", arch_muntin_count=5
        )
        assert len(many.Items) - len(few.Items) == 3

    def test_non_rectangular_shapes_ignore_the_partition_type(self):
        self.setup_context()
        single = ifcopenshell.api.geometry.add_window_representation(
            self.file, context=self.body, window_shape="ROUND", partition_type="SINGLE_PANEL"
        )
        double = ifcopenshell.api.geometry.add_window_representation(
            self.file, context=self.body, window_shape="ROUND", partition_type="DOUBLE_PANEL_VERTICAL"
        )
        assert len(single.Items) == len(double.Items)

    def test_omitting_overall_dimensions_does_not_crash(self):
        self.setup_context()
        representation = ifcopenshell.api.geometry.add_window_representation(self.file, context=self.body)
        assert representation.is_a("IfcShapeRepresentation")


class TestAddWindowRepresentationShapeIFC2X3(test.bootstrap.IFC2X3):
    def test_arch_window_can_be_created(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix=None)
        ifcopenshell.api.unit.assign_unit(self.file, [unit])
        model_context = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_context
        )
        representation = ifcopenshell.api.geometry.add_window_representation(
            self.file, context=body, overall_width=1.0, overall_height=1.6, window_shape="ARCH"
        )
        assert representation.is_a("IfcShapeRepresentation")
