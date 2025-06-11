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


class TestRemoveBoolean(test.bootstrap.IFC4):
    def test_removing_a_single_top_level_boolean(self):
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
        ifcopenshell.api.geometry.remove_boolean(self.file, booleans[0])
        assert set(rep.Items) == {first, second}
        assert not self.file.by_type("IfcBooleanResult")

    def test_removing_a_top_level_nested_boolean(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        first = builder.sphere()
        second1 = builder.block()
        second2 = builder.block()
        rep = builder.get_representation(body, [first])

        ifcopenshell.api.geometry.add_boolean(self.file, first, [second1, second2])
        ifcopenshell.api.geometry.remove_boolean(self.file, second2)
        assert len(rep.Items) == 2
        assert second2 in rep.Items
        boolean = self.file.by_type("IfcBooleanResult")[0]
        assert boolean in rep.Items
        assert boolean.FirstOperand == first
        assert boolean.SecondOperand == second1

    def test_removing_a_nested_boolean(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        first = builder.sphere()
        second1 = builder.block()
        second2 = builder.block()
        rep = builder.get_representation(body, [first])

        ifcopenshell.api.geometry.add_boolean(self.file, first, [second1, second2])
        ifcopenshell.api.geometry.remove_boolean(self.file, second1)
        assert len(rep.Items) == 2
        assert second1 in rep.Items
        boolean = self.file.by_type("IfcBooleanResult")[0]
        assert boolean in rep.Items
        assert boolean.FirstOperand == first
        assert boolean.SecondOperand == second2


class TestRemoveBooleanIFC2X3(test.bootstrap.IFC2X3, TestRemoveBoolean):
    pass
