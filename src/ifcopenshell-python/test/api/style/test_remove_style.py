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
import ifcopenshell.api.material
import ifcopenshell.api.style


class TestRemoveStyle(test.bootstrap.IFC4):
    def test_removing_a_style(self):
        shading = self.file.createIfcSurfaceStyleShading()
        style = self.file.createIfcSurfaceStyle(Styles=[shading])
        ifcopenshell.api.style.remove_style(self.file, style=style)
        assert len(list(self.file)) == 0

    def test_removing_any_styled_items_referencing_the_style(self):
        shading = self.file.createIfcSurfaceStyleShading()
        style = self.file.createIfcSurfaceStyle(Styles=[shading])
        styled_item = self.file.createIfcStyledItem(Styles=[style])
        ifcopenshell.api.style.remove_style(self.file, style=style)
        assert len(list(self.file)) == 0

    def test_remove_non_surface_styles(self):
        STYLE_TYPES = [
            "IfcCurveStyle",
            "IfcFillAreaStyle",
            "IfcTextStyle",
        ]
        for style_type in STYLE_TYPES:
            style = self.file.create_entity(style_type)
            ifcopenshell.api.style.remove_style(self.file, style=style)
            assert len(self.file.by_type("IfcPresentationStyle")) == 0

    def test_remove_curve_style_with_curve_style_hatching(self):
        element = self.file.create_entity("IfcWall")
        material = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material)
        curve_style = self.file.create_entity("IfcCurveStyle")
        fill_style = self.file.create_entity("IfcFillAreaStyleHatching", HatchLineAppearance=curve_style)
        style = self.file.create_entity("IfcFillAreaStyle", FillStyles=[fill_style])
        self.file.create_entity(
            "IfcMaterialDefinitionRepresentation",
            RepresentedMaterial=material,
            Representations=[
                self.file.create_entity(
                    "IfcStyledRepresentation",
                    Items=[self.file.create_entity("IfcStyledItem", Styles=[style])],
                )
            ],
        )
        ifcopenshell.api.style.remove_style(self.file, curve_style)
        assert len(self.file.by_type("IfcPresentationStyle")) == 0
        assert len(self.file.by_type("IfcMaterialDefinitionRepresentation")) == 0
        assert len(self.file.by_type("IfcStyledRepresentation")) == 0

    def test_remove_fill_area_with_fill_area_style_hatching(self):
        element = self.file.create_entity("IfcWall")
        material = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material)
        curve_style = self.file.create_entity("IfcCurveStyle")
        fill_style = self.file.create_entity("IfcFillAreaStyleHatching", HatchLineAppearance=curve_style)
        style = self.file.create_entity("IfcFillAreaStyle", FillStyles=[fill_style])
        self.file.create_entity(
            "IfcMaterialDefinitionRepresentation",
            RepresentedMaterial=material,
            Representations=[
                self.file.create_entity(
                    "IfcStyledRepresentation",
                    Items=[self.file.create_entity("IfcStyledItem", Styles=[style])],
                )
            ],
        )
        ifcopenshell.api.style.remove_style(self.file, style)
        assert len(self.file.by_type("IfcPresentationStyle")) == 0
        assert len(self.file.by_type("IfcMaterialDefinitionRepresentation")) == 0
        assert len(self.file.by_type("IfcStyledRepresentation")) == 0


class TestRemoveStyleIFC2X3(test.bootstrap.IFC2X3, TestRemoveStyle):
    pass
