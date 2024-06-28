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
import ifcopenshell.api.style


class TestAddSurfaceStyle(test.bootstrap.IFC4):
    def test_adding_a_surface_style(self):
        style = self.file.createIfcSurfaceStyle()
        attrs = {"SurfaceColour": {"Name": "", "Red": 1, "Green": 1, "Blue": 1}}
        if self.file.schema != "IFC2X3":
            attrs["Transparency"] = 0.5
        result = ifcopenshell.api.style.add_surface_style(
            self.file,
            style=style,
            ifc_class="IfcSurfaceStyleShading",
            attributes=attrs,
        )
        assert result.is_a("IfcSurfaceStyleShading")
        assert result.SurfaceColour.Red == 1
        assert result.SurfaceColour.Green == 1
        assert result.SurfaceColour.Blue == 1
        if self.file.schema != "IFC2X3":
            assert result.Transparency == 0.5
        assert style.Styles[0] == result

    def test_adding_a_rendering_style(self):
        style = self.file.createIfcSurfaceStyle()
        attrs = {"SurfaceColour": {"Name": "", "Red": 1, "Green": 1, "Blue": 1}}
        if self.file.schema != "IFC2X3":
            attrs["Transparency"] = 0.5
        result = ifcopenshell.api.style.add_surface_style(
            self.file,
            style=style,
            ifc_class="IfcSurfaceStyleRendering",
            attributes=attrs,
        )
        assert result.is_a("IfcSurfaceStyleRendering")
        assert result.SurfaceColour.Red == 1
        assert result.SurfaceColour.Green == 1
        assert result.SurfaceColour.Blue == 1
        if self.file.schema != "IFC2X3":
            assert result.Transparency == 0.5
        assert style.Styles[0] == result

    def test_not_adding_a_style_twice(self):
        style = self.file.createIfcSurfaceStyle()
        attrs = {"SurfaceColour": {"Name": "", "Red": 1, "Green": 1, "Blue": 1}}
        if self.file.schema != "IFC2X3":
            attrs["Transparency"] = 0.5
        ifcopenshell.api.style.add_surface_style(
            self.file,
            style=style,
            ifc_class="IfcSurfaceStyleRendering",
            attributes=attrs,
        )
        result = ifcopenshell.api.style.add_surface_style(
            self.file,
            style=style,
            ifc_class="IfcSurfaceStyleRendering",
            attributes=attrs,
        )
        assert style.Styles[0] == result
        assert len(style.Styles) == 1

    def test_adding_multiple_styles_of_different_types(self):
        style = self.file.createIfcSurfaceStyle()
        attrs = {"SurfaceColour": {"Name": "", "Red": 1, "Green": 1, "Blue": 1}}
        if self.file.schema != "IFC2X3":
            attrs["Transparency"] = 0.5
        result1 = ifcopenshell.api.style.add_surface_style(
            self.file,
            style=style,
            ifc_class="IfcSurfaceStyleShading",
            attributes=attrs,
        )
        result2 = ifcopenshell.api.style.add_surface_style(
            self.file,
            style=style,
            ifc_class="IfcSurfaceStyleWithTextures",
            attributes={},
        )
        assert result1 in style.Styles
        assert result2 in style.Styles
        assert len(style.Styles) == 2

    def test_ensure_shading_and_rendering_are_mutually_exclusive_when_adding(self):
        style = self.file.createIfcSurfaceStyle()
        attrs = {"SurfaceColour": {"Name": "", "Red": 1, "Green": 1, "Blue": 1}}
        if self.file.schema != "IFC2X3":
            attrs["Transparency"] = 0.5
        ifcopenshell.api.style.add_surface_style(
            self.file,
            style=style,
            ifc_class="IfcSurfaceStyleShading",
            attributes=attrs,
        )
        result = ifcopenshell.api.style.add_surface_style(
            self.file,
            style=style,
            ifc_class="IfcSurfaceStyleRendering",
            attributes=attrs,
        )
        assert style.Styles[0] == result
        assert len(style.Styles) == 1


class TestAddSurfaceStyleIFC2X3(test.bootstrap.IFC2X3, TestAddSurfaceStyle):
    pass
