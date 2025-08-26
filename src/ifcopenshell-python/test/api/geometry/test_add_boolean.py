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


class TestAddBoolean(test.bootstrap.IFC4):
    def test_adding_a_boolean_from_two_top_level_items(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        first = builder.sphere()
        second = builder.block()
        rep = builder.get_representation(body, [first, second])

        booleans = ifcopenshell.api.geometry.add_boolean(self.file, first, [second])
        assert len(booleans) == 1
        boolean = booleans[0]
        assert boolean.is_a("IfcBooleanResult")
        assert boolean.FirstOperand == first
        assert boolean.SecondOperand == second
        assert boolean.Operator == "DIFFERENCE"
        assert set(rep.Items) == {boolean}

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
        rep = builder.get_representation(body, [first, second1, second2])

        booleans = ifcopenshell.api.geometry.add_boolean(self.file, first, [second1, second2])
        assert len(booleans) == 2
        assert len(rep.Items) == 1
        assert rep.Items[0].FirstOperand.is_a("IfcBooleanResult")
        assert rep.Items[0].SecondOperand == second2
        assert rep.Items[0].Operator == "DIFFERENCE"
        assert rep.Items[0].FirstOperand.FirstOperand == first
        assert rep.Items[0].FirstOperand.SecondOperand == second1
        assert rep.Items[0].FirstOperand.Operator == "DIFFERENCE"

    def test_adding_a_boolean_to_an_existing_operand_from_a_top_level_item(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        first = builder.sphere()
        second1 = builder.block()
        second2 = builder.block()
        rep = builder.get_representation(body, [first, second1])
        booleans = ifcopenshell.api.geometry.add_boolean(self.file, first, [second1])
        rep.Items = list(rep.Items) + [second2]
        booleans = ifcopenshell.api.geometry.add_boolean(self.file, first, [second2])
        assert len(booleans) == 1
        assert len(rep.Items) == 1
        assert rep.Items[0].FirstOperand.is_a("IfcBooleanResult")
        assert rep.Items[0].SecondOperand == second2
        assert rep.Items[0].FirstOperand.FirstOperand == first
        assert rep.Items[0].FirstOperand.SecondOperand == second1

    def test_adding_a_boolean_to_an_existing_operand_from_another_operand(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        first1 = builder.sphere()
        second1 = builder.block()
        first2 = builder.sphere()
        second2 = builder.block()
        rep = builder.get_representation(body, [first1, first2, second1, second2])
        booleans = ifcopenshell.api.geometry.add_boolean(self.file, first1, [second1])
        booleans = ifcopenshell.api.geometry.add_boolean(self.file, first2, [second2])
        booleans = ifcopenshell.api.geometry.add_boolean(self.file, first1, [second2])

        assert len(booleans) == 1
        assert len(rep.Items) == 2

        assert self.file.get_total_inverses(first1) == 1
        result = next(iter(self.file.get_inverse(first1)))
        assert result.FirstOperand == first1
        assert result.SecondOperand == second1
        result2 = next(iter(self.file.get_inverse(result)))
        assert result2.FirstOperand == result
        # Second2 is now used twice. Reusing is OK (albeit confusing), so long as things don't get recursive.
        assert result2.SecondOperand == second2

        assert self.file.get_total_inverses(first2) == 1
        result3 = next(iter(self.file.get_inverse(first2)))
        assert result3.FirstOperand == first2
        assert result3.SecondOperand == second2

    def test_preventing_recursive_booleans(self):
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
        ifcopenshell.api.geometry.add_boolean(self.file, first, [second])
        assert len(rep.Items) == 1
        assert rep.Items[0].FirstOperand == first
        assert rep.Items[0].SecondOperand == second
        ifcopenshell.api.geometry.add_boolean(self.file, second, [second])
        ifcopenshell.api.geometry.add_boolean(self.file, second, [first])
        assert len(rep.Items) == 1
        assert rep.Items[0].FirstOperand == first
        assert rep.Items[0].SecondOperand == second
        assert len(self.file.by_type("IfcBooleanResult")) == 1


class TestAddBooleanIFC2X3(test.bootstrap.IFC2X3, TestAddBoolean):
    pass
