# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api.style


class TestEditSurfaceStyle(test.bootstrap.IFC4):
    def test_editing_a_shading_style(self):
        colour = self.file.createIfcColourRgb(None, 0, 0, 0)
        style = self.file.createIfcSurfaceStyleShading(colour)
        attrs = {"SurfaceColour": {"Red": 1, "Green": 1, "Blue": 1}}
        if self.file.schema != "IFC2X3":
            attrs["Transparency"] = 0.5
        ifcopenshell.api.style.edit_surface_style(
            self.file,
            style=style,
            attributes=attrs,
        )
        assert style.SurfaceColour == colour
        assert list(colour) == [None, 1, 1, 1]
        if self.file.schema != "IFC2X3":
            assert style.Transparency == 0.5

    def test_editing_an_empty_colour_or_factor(self):
        for attribute in [
            "DiffuseColour",
            "TransmissionColour",
            "DiffuseTransmissionColour",
            "ReflectionColour",
            "SpecularColour",
        ]:
            style = self.file.createIfcSurfaceStyleRendering(self.file.createIfcColourRgb(None, 0, 0, 0))
            ifcopenshell.api.style.edit_surface_style(
                self.file,
                style=style,
                attributes={attribute: {"Red": 1, "Green": 1, "Blue": 1}},
            )
            assert list(getattr(style, attribute)) == [None, 1, 1, 1]

    def test_editing_an_existing_colour_to_another_colour(self):
        for attribute in [
            "DiffuseColour",
            "TransmissionColour",
            "DiffuseTransmissionColour",
            "ReflectionColour",
            "SpecularColour",
        ]:
            colour = self.file.createIfcColourRgb(None, 0, 0, 0)
            style = self.file.createIfcSurfaceStyleRendering(self.file.createIfcColourRgb(None, 0, 0, 0))
            setattr(style, attribute, colour)
            ifcopenshell.api.style.edit_surface_style(
                self.file,
                style=style,
                attributes={attribute: {"Red": 1, "Green": 1, "Blue": 1}},
            )
            assert list(colour) == [None, 1, 1, 1]

    def test_editing_an_existing_colour_to_a_factor(self):
        for attribute in [
            "DiffuseColour",
            "TransmissionColour",
            "DiffuseTransmissionColour",
            "ReflectionColour",
            "SpecularColour",
        ]:
            colour = self.file.createIfcColourRgb(None, 0, 0, 0)
            colour_id = colour.id()
            style = self.file.createIfcSurfaceStyleRendering(self.file.createIfcColourRgb(None, 0, 0, 0))
            setattr(style, attribute, colour)
            ifcopenshell.api.style.edit_surface_style(self.file, style=style, attributes={attribute: 0.5})
            with pytest.raises(RuntimeError):
                self.file.by_id(colour_id)
            assert getattr(style, attribute).wrappedValue == 0.5

    def test_editing_an_existing_factor_to_another_factor(self):
        for attribute in [
            "DiffuseColour",
            "TransmissionColour",
            "DiffuseTransmissionColour",
            "ReflectionColour",
            "SpecularColour",
        ]:
            style = self.file.createIfcSurfaceStyleRendering(self.file.createIfcColourRgb(None, 0, 0, 0))
            setattr(style, attribute, self.file.createIfcNormalisedRatioMeasure(0.5))
            ifcopenshell.api.style.edit_surface_style(self.file, style=style, attributes={attribute: 0.4})
            assert getattr(style, attribute).wrappedValue == 0.4

    def test_editing_an_existing_factor_to_a_colour(self):
        for attribute in [
            "DiffuseColour",
            "TransmissionColour",
            "DiffuseTransmissionColour",
            "ReflectionColour",
            "SpecularColour",
        ]:
            style = self.file.createIfcSurfaceStyleRendering(self.file.createIfcColourRgb(None, 0, 0, 0))
            setattr(style, attribute, self.file.createIfcNormalisedRatioMeasure(0.5))
            ifcopenshell.api.style.edit_surface_style(
                self.file,
                style=style,
                attributes={attribute: {"Red": 1, "Green": 1, "Blue": 1}},
            )
            assert list(getattr(style, attribute)) == [None, 1, 1, 1]

    def test_editing_a_specular_highlight_as_an_exponent(self):
        style = self.file.createIfcSurfaceStyleRendering(self.file.createIfcColourRgb(None, 0, 0, 0))
        ifcopenshell.api.style.edit_surface_style(
            self.file,
            style=style,
            attributes={"SpecularHighlight": {"IfcSpecularExponent": 2}},
        )
        assert style.SpecularHighlight.is_a("IfcSpecularExponent")
        assert style.SpecularHighlight.wrappedValue == 2

    def test_editing_a_specular_highlight_as_a_roughness(self):
        style = self.file.createIfcSurfaceStyleRendering(self.file.createIfcColourRgb(None, 0, 0, 0))
        ifcopenshell.api.style.edit_surface_style(
            self.file,
            style=style,
            attributes={"SpecularHighlight": {"IfcSpecularRoughness": 0.5}},
        )
        assert style.SpecularHighlight.is_a("IfcSpecularRoughness")
        assert style.SpecularHighlight.wrappedValue == 0.5

    def test_editing_texture_style(self):
        style = self.file.createIfcSurfaceStyleWithTextures()
        textures = ({"Mode": "DIFFUSE", "RepeatS": True, "RepeatT": True, "URLReference": "diffuse.jpg"},)
        textures = ifcopenshell.api.style.add_surface_textures(self.file, textures=textures)
        ifcopenshell.api.style.edit_surface_style(
            self.file,
            style=style,
            attributes={"Textures": textures},
        )
        assert set(style.Textures) == set(textures)

    def test_editing_lighting_style(self):
        style = self.file.createIfcSurfaceStyleLighting()
        attributes = (
            "DiffuseTransmissionColour",
            "DiffuseReflectionColour",
            "TransmissionColour",
            "ReflectanceColour",
        )
        attributes = {a: {"Red": 1, "Green": 1, "Blue": 1} for a in attributes}
        ifcopenshell.api.style.edit_surface_style(
            self.file,
            style=style,
            attributes=attributes,
        )
        for attribute in attributes:
            assert tuple(getattr(style, attribute)) == (None, 1, 1, 1)


class TestEditSurfaceStyleIFC2X3(test.bootstrap.IFC2X3, TestEditSurfaceStyle):
    pass
