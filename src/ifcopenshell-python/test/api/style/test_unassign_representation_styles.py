# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.style


class TestUnassignRepresentationStyles(test.bootstrap.IFC4):
    def test_run(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        product_shape = self.file.createIfcProductDefinitionShape()
        element.Representation = product_shape

        representation = self.file.createIfcShapeRepresentation()
        item = self.file.createIfcExtrudedAreaSolid()
        representation.Items = [item]

        style = self.file.createIfcSurfaceStyle()
        ifcopenshell.api.style.assign_representation_styles(
            self.file, styles=[style], shape_representation=representation
        )
        style2 = self.file.createIfcSurfaceStyle()
        ifcopenshell.api.style.assign_representation_styles(
            self.file,
            styles=[style2],
            shape_representation=representation,
            replace_previous_same_type_style=False,
        )
        assert item.StyledByItem[0].Styles == (style, style2)

        ifcopenshell.api.style.unassign_representation_styles(
            self.file, styles=[style], shape_representation=representation
        )
        assert item.StyledByItem[0].Styles == (style2,)

        # unassigning last style removes styled item
        ifcopenshell.api.style.unassign_representation_styles(
            self.file, styles=[style2], shape_representation=representation
        )
        assert len(item.StyledByItem) == 0
        assert len(self.file.by_type("IfcStyledItem")) == 0

    def test_assign_using_style_assignment(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        product_shape = self.file.createIfcProductDefinitionShape()
        element.Representation = product_shape

        representation = self.file.createIfcShapeRepresentation()
        item = self.file.createIfcExtrudedAreaSolid()
        representation.Items = [item]

        style = self.file.createIfcSurfaceStyle()
        ifcopenshell.api.style.assign_representation_styles(
            self.file,
            styles=[style],
            shape_representation=representation,
            should_use_presentation_style_assignment=True,
        )
        style_assignment = self.file.by_type("IfcPresentationStyleAssignment")[0]

        # reusing existing styled item and style assignment
        style2 = self.file.createIfcSurfaceStyle()
        ifcopenshell.api.style.assign_representation_styles(
            self.file,
            styles=[style2],
            shape_representation=representation,
            should_use_presentation_style_assignment=True,
            replace_previous_same_type_style=False,
        )
        assert style_assignment.Styles == (style, style2)

        ifcopenshell.api.style.unassign_representation_styles(
            self.file,
            styles=[style],
            shape_representation=representation,
            should_use_presentation_style_assignment=True,
        )
        assert style_assignment.Styles == (style2,)

        # unassigning last style removes styled item and presentation style
        ifcopenshell.api.style.unassign_representation_styles(
            self.file,
            styles=[style2],
            shape_representation=representation,
            should_use_presentation_style_assignment=True,
        )
        assert len(item.StyledByItem) == 0
        assert len(self.file.by_type("IfcStyledItem")) == 0
        assert len(self.file.by_type("IfcPresentationStyleAssignment")) == 0


class TestUnassignRepresentationStylesIFC2X3(test.bootstrap.IFC2X3):
    def test_run(self):
        TestUnassignRepresentationStyles.test_assign_using_style_assignment(self)
