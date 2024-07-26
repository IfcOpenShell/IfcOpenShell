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
import ifcopenshell.api.material


class TestAssignMaterialStyleIFC2X3(test.bootstrap.IFC2X3):
    def test_run(self):
        material = ifcopenshell.api.material.add_material(self.file)
        context = self.file.createIfcGeometricRepresentationContext()
        style = self.file.createIfcSurfaceStyle()
        ifcopenshell.api.style.assign_material_style(self.file, material=material, style=style, context=context)

        assert len(material.HasRepresentation) == 1
        definition = material.HasRepresentation[0]
        assert len(definition.Representations) == 1
        representation = definition.Representations[0]
        assert representation.is_a("IfcStyledRepresentation")
        assert representation.ContextOfItems == context
        assert len(representation.Items) == 1
        item = representation.Items[0]
        assert item.is_a("IfcStyledItem")
        if self.file.schema != "IFC2X3":
            assert item.Styles == (style,)
        else:
            # IfcPresentationStyleAssignment
            assert len(item.Styles[0]) == 1
            assert item.Styles[0].Styles == (style,)

        style2 = self.file.createIfcSurfaceStyle()
        ifcopenshell.api.style.assign_material_style(self.file, material=material, style=style2, context=context)

        # reuse existing elements and reassign the style
        assert material.HasRepresentation == (definition,)
        assert definition.Representations == (representation,)
        assert len(representation.Items) == 1
        assert representation.Items[0] == item
        if self.file.schema != "IFC2X3":
            assert representation.Items[0].Styles == (style2,)
        else:
            # IfcPresentationStyleAssignment
            assert len(representation.Items[0].Styles) == 1
            assert representation.Items[0].Styles == (style2,)


class TestAssignMaterialStyleIFC4(test.bootstrap.IFC4, TestAssignMaterialStyleIFC2X3):
    # IfcMaterialConstituentSet was added in IFC4
    def test_update_shape_aspect_representations_items_styles_if_material_is_part_of_matching_material_constituents(
        self,
    ):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        name = "Concrete"
        product_shape = self.file.createIfcProductDefinitionShape()
        element.Representation = product_shape
        context = self.file.createIfcGeometricRepresentationContext()

        representation = self.file.createIfcShapeRepresentation()
        item = self.file.createIfcExtrudedAreaSolid()
        representation.Items = [item]

        shape_aspect = self.file.createIfcShapeAspect(ShapeRepresentations=(representation,), Name=name)
        shape_aspect.PartOfProductDefinitionShape = product_shape

        style = self.file.createIfcSurfaceStyle()
        material = ifcopenshell.api.material.add_material(self.file)
        material_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialConstituentSet")
        constituent = ifcopenshell.api.material.add_constituent(
            self.file, constituent_set=material_set, material=material
        )
        constituent.Name = name
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material_set)

        ifcopenshell.api.style.assign_material_style(self.file, material=material, style=style, context=context)

        assert item.StyledByItem[0].Styles == (style,)
