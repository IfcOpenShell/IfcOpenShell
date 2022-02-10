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
import ifcopenshell.api


class TestRemoveSurfaceStyle(test.bootstrap.IFC4):
    def test_removing_a_shading_style(self):
        style = self.file.createIfcSurfaceStyleShading(SurfaceColour=self.file.createIfcColourRgb())
        ifcopenshell.api.run("style.remove_surface_style", self.file, style=style)
        assert len(list(self.file)) == 0

    def test_removing_a_texture_style(self):
        texture = self.file.createIfcImageTexture()
        style = self.file.createIfcSurfaceStyleWithTextures(Textures=[texture])
        ifcopenshell.api.run("style.remove_surface_style", self.file, style=style)
        assert len(list(self.file)) == 0

    def test_removing_a_texture_style_with_all_of_its_coordinates(self):
        texture = self.file.createIfcImageTexture()
        coordinates = self.file.createIfcTextureCoordinateGenerator(Maps=[texture])
        style = self.file.createIfcSurfaceStyleWithTextures(Textures=[texture])
        ifcopenshell.api.run("style.remove_surface_style", self.file, style=style)
        assert len(list(self.file)) == 0
