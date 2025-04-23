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


class TestAssignRepresentationStyles(test.bootstrap.IFC4):
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
        assert item.StyledByItem[0].Styles == (style,)

        # reusing existing styled item for different style type
        style2 = self.file.createIfcFillAreaStyle()
        ifcopenshell.api.style.assign_representation_styles(
            self.file, styles=[style2], shape_representation=representation
        )
        assert item.StyledByItem[0].Styles == (style, style2)
        assert len(self.file.by_type("IfcStyledItem")) == 1

        # replacing existing style of the same type
        style3 = self.file.createIfcSurfaceStyle()
        ifcopenshell.api.style.assign_representation_styles(
            self.file, styles=[style3], shape_representation=representation
        )
        assert item.StyledByItem[0].Styles == (style2, style3)
        assert len(self.file.by_type("IfcStyledItem")) == 1

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
        assert len(self.file.by_type("IfcPresentationStyleAssignment")) == 1
        style_assignment = self.file.by_type("IfcPresentationStyleAssignment")[0]
        assert style_assignment.Styles == (style,)
        assert item.StyledByItem[0].Styles == (style_assignment,)

        # reusing existing styled item for different style type
        style2 = self.file.createIfcFillAreaStyle()
        ifcopenshell.api.style.assign_representation_styles(
            self.file,
            styles=[style2],
            shape_representation=representation,
            should_use_presentation_style_assignment=True,
        )

        assert len(self.file.by_type("IfcPresentationStyleAssignment")) == 1
        assert item.StyledByItem[0].Styles == (style_assignment,)
        assert item.StyledByItem[0].Styles[0].Styles == (style, style2)
        assert len(self.file.by_type("IfcStyledItem")) == 1

        # replacing existing style of the same type
        style3 = self.file.createIfcSurfaceStyle()
        ifcopenshell.api.style.assign_representation_styles(
            self.file,
            styles=[style3],
            shape_representation=representation,
            should_use_presentation_style_assignment=True,
        )

        assert len(self.file.by_type("IfcPresentationStyleAssignment")) == 1
        assert item.StyledByItem[0].Styles == (style_assignment,)
        assert item.StyledByItem[0].Styles[0].Styles == (style2, style3)
        assert len(self.file.by_type("IfcStyledItem")) == 1

    def test_assign_style_to_topology_representation(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        product_shape = self.file.create_entity("IfcProductDefinitionShape")
        element.Representation = product_shape

        representation = self.file.create_entity("IfcTopologyRepresentation")
        item = self.file.create_entity("IfcFace")
        representation.Items = [item]

        style = self.file.create_entity("IfcSurfaceStyle")
        ifcopenshell.api.style.assign_representation_styles(
            self.file, styles=[style], shape_representation=representation
        )
        assert item.StyledByItem[0].Styles == (style,)


class TestAssignRepresentationStylesIFC2X3(test.bootstrap.IFC2X3):
    def test_run(self):
        TestAssignRepresentationStyles.test_assign_using_style_assignment(self)
