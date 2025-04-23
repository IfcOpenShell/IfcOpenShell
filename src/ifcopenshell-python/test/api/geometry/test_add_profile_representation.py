# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api.unit
import ifcopenshell.api.root
import ifcopenshell.api.context
import ifcopenshell.api.geometry
from ifcopenshell.util.shape_builder import ShapeBuilder


class TestAddProfileRepresentation(test.bootstrap.IFC4):
    def setup_profile(self) -> None:
        builder = ShapeBuilder(self.file)

        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        # In IFC2X3 the unit is required.
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix=None)
        ifcopenshell.api.unit.assign_unit(self.file, [unit])

        model_context = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        self.body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_context
        )
        rectangle = builder.rectangle((100, 100))
        self.profile = builder.profile(rectangle)

    def test_run(self):
        self.setup_profile()
        representation_string_cardinal_point = ifcopenshell.api.geometry.add_profile_representation(
            self.file,
            context=self.body,
            profile=self.profile,
            depth=1000,
            cardinal_point="bottom left",
        )
        representation_numeric_cardinal_point = ifcopenshell.api.geometry.add_profile_representation(
            self.file,
            context=self.body,
            profile=self.profile,
            depth=1000,
            cardinal_point=1,
        )
        representations = [representation_string_cardinal_point, representation_numeric_cardinal_point]
        for representation in representations:
            assert representation.is_a("IfcShapeRepresentation")
            item = representation.Items[0]
            assert item.is_a("IfcExtrudedAreaSolid")
            assert item.SweptArea == self.profile
            assert item.ExtrudedDirection.DirectionRatios == (0.0, 0.0, 1.0)
            assert item.Depth == 1000
            assert item.Position.Location.Coordinates == (-50.0, 50.0, 0.0)


class TestAddProfileRepresentationIFC2X3(test.bootstrap.IFC2X3, TestAddProfileRepresentation):
    pass


class TestAddProfileRepresentationIFC4X3(test.bootstrap.IFC4X3, TestAddProfileRepresentation):
    pass
