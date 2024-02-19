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

import pytest
import test.bootstrap
import ifcopenshell
import ifcopenshell.api


# TODO: test assigning styles without material constituents
class TestAssignMaterialStyle(test.bootstrap.IFC4):
    def test_update_shape_aspect_representaitons_items_styles_if_material_is_part_of_matching_material_constituents(
        self,
    ):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
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
        material = ifcopenshell.api.run("material.add_material", self.file)
        material_set = ifcopenshell.api.run(
            "material.add_material_set", self.file, set_type="IfcMaterialConstituentSet"
        )
        constituent = ifcopenshell.api.run(
            "material.add_constituent", self.file, constituent_set=material_set, material=material
        )
        constituent.Name = name
        ifcopenshell.api.run("material.assign_material", self.file, product=element, material=material_set)

        ifcopenshell.api.run("style.assign_material_style", self.file, material=material, style=style, context=context)

        assert item.StyledByItem[0].Styles == (style,)
