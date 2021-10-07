import pytest
import test.bootstrap
import ifcopenshell.api


class TestEditSurfaceStyle(test.bootstrap.IFC4):
    def test_editing_a_shading_style(self):
        colour = self.file.createIfcColourRgb(None, 0, 0, 0)
        style = self.file.createIfcSurfaceStyleShading(colour)
        ifcopenshell.api.run(
            "style.edit_surface_style",
            self.file,
            style=style,
            attributes={"SurfaceColour": {"Red": 1, "Green": 1, "Blue": 1}, "Transparency": 0.5},
        )
        assert style.SurfaceColour == colour
        assert list(colour) == [None, 1, 1, 1]
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
            ifcopenshell.api.run(
                "style.edit_surface_style",
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
            ifcopenshell.api.run(
                "style.edit_surface_style",
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
            ifcopenshell.api.run("style.edit_surface_style", self.file, style=style, attributes={attribute: 0.5})
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
            ifcopenshell.api.run("style.edit_surface_style", self.file, style=style, attributes={attribute: 0.4})
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
            ifcopenshell.api.run(
                "style.edit_surface_style",
                self.file,
                style=style,
                attributes={attribute: {"Red": 1, "Green": 1, "Blue": 1}},
            )
            assert list(getattr(style, attribute)) == [None, 1, 1, 1]
