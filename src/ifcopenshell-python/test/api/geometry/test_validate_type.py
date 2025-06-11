# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

import test.bootstrap
import ifcopenshell.api.root
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.util.shape_builder


class TestValidateType(test.bootstrap.IFC4):
    def test_validating_a_non_csg_representation(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        rep = builder.get_representation(body, [builder.rectangle()])
        assert ifcopenshell.api.geometry.validate_type(self.file, rep) is True
        assert rep.RepresentationType == "Curve2D"

    def test_failing_a_non_csg_representation(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        rep = builder.get_representation(body, [builder.rectangle(), builder.block()])
        assert ifcopenshell.api.geometry.validate_type(self.file, rep) is False
        assert rep.RepresentationType is None

    def test_validating_a_correct_representation(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        first = builder.sphere()
        second = builder.block()
        rep = builder.get_representation(body, [first, second])

        ifcopenshell.api.geometry.add_boolean(self.file, first, [second])
        assert ifcopenshell.api.geometry.validate_type(self.file, rep) is True
        assert rep.RepresentationType == "CSG"

    def test_adding_multiple_booleans_from_three_top_level_items(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        first = builder.sphere()
        second1 = builder.block()
        second2 = builder.block()
        second3 = builder.block()
        rep = builder.get_representation(body, [first, second1, second2, second3])

        booleans = ifcopenshell.api.geometry.add_boolean(self.file, first, [second1])
        assert len(booleans) == 1
        assert len(rep.Items) == 3
        assert ifcopenshell.api.geometry.validate_type(self.file, rep) is True
        assert len(rep.Items) == 1
        assert rep.RepresentationType == "CSG"
        assert rep.Items[0].Operator == "UNION"

    def test_failing_validation_on_unreconcilable_types(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        first = builder.sphere()
        second1 = builder.block()
        second2 = builder.rectangle()
        rep = builder.get_representation(body, [first, second1, second2])

        booleans = ifcopenshell.api.geometry.add_boolean(self.file, first, [second1])
        assert len(booleans) == 1
        assert len(rep.Items) == 2
        assert ifcopenshell.api.geometry.validate_type(self.file, rep) is False
        assert len(rep.Items) == 2
        assert rep.RepresentationType is None


class TestValidateTypeIFC2X3(test.bootstrap.IFC2X3, TestValidateType):
    pass
