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
import ifcopenshell.api.style


class TestRemoveSurfaceStyleIFC2X3(test.bootstrap.IFC2X3):
    def test_removing_a_shading_style(self):
        style = self.file.createIfcSurfaceStyleShading(SurfaceColour=self.file.createIfcColourRgb(None, 1, 1, 1))
        ifcopenshell.api.style.remove_surface_style(self.file, style=style)
        assert len(list(self.file)) == 0

    def test_removing_a_texture_style(self):
        texture = self.file.createIfcImageTexture()
        style = self.file.createIfcSurfaceStyleWithTextures(Textures=[texture])
        ifcopenshell.api.style.remove_surface_style(self.file, style=style)
        assert len(list(self.file)) == 0

    def test_removing_a_rendering_style(self):
        style = self.file.createIfcSurfaceStyleRendering(
            SurfaceColour=self.file.createIfcColourRgb(None, 1, 1, 1),
            Transparency=0.0,
            DiffuseColour=self.file.createIfcColourRgb(None, 1, 1, 1),
            TransmissionColour=self.file.createIfcNormalisedRatioMeasure(0.5),
            SpecularHighlight=self.file.createIfcSpecularRoughness(0.5),
            ReflectanceMethod="NOTDEFINED",
        )
        # See issue #2046, IfcOpenShell exhibits different behaviour - we can
        # remove entity_instances() without an ID if we create them afresh, but
        # will segfault if we load them stale.
        g = ifcopenshell.file.from_string(self.file.wrapped_data.to_string())
        ifcopenshell.api.style.remove_surface_style(g, style=g.by_type("IfcSurfaceStyleRendering")[0])
        assert len(list(g)) == 0


class TestRemoveSurfaceStyleIFC4(test.bootstrap.IFC4, TestRemoveSurfaceStyleIFC2X3):
    # IfcTextureCoordinateGenerator doesn't have Maps in IFC2X3
    def test_removing_a_texture_style_with_all_of_its_coordinates(self):
        texture = self.file.createIfcImageTexture()
        coordinates = self.file.createIfcTextureCoordinateGenerator(Maps=[texture])
        style = self.file.createIfcSurfaceStyleWithTextures(Textures=[texture])
        ifcopenshell.api.style.remove_surface_style(self.file, style=style)
        assert len(list(self.file)) == 0
