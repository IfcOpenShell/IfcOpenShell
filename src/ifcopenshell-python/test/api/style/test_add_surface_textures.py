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


# TODO: add ifc2x3 tests after add_surface_textures will support ifc2x3
class TestAddSurfaceTexture(test.bootstrap.IFC4):
    def get_default_texture_data(self):
        return [
            {"Mode": "DIFFUSE", "RepeatS": True, "RepeatT": True, "URLReference": "diffuse.jpg"},
            {"Mode": "NORMAL", "RepeatS": False, "RepeatT": False, "URLReference": "normal.jpg"},
            {"Mode": "METALLICROUGHNESS", "RepeatS": True, "RepeatT": True, "URLReference": "metallic_roughness.jpg"},
            {"Mode": "OCCLUSION", "RepeatS": True, "RepeatT": True, "URLReference": "ambient_occlusion.jpg"},
        ]

    def compare_texture_to_data(self, texture, data, uv_maps=[]):
        texture_data = texture.get_info()
        for attribute in ("Mode", "RepeatS", "RepeatT", "URLReference"):
            assert texture_data[attribute] == data.get(attribute, None)

        uv_mode = data.get("uv_mode", None)
        if uv_mode is None:
            assert texture.IsMappedBy == ()
        elif uv_mode == "Generated":
            assert len(texture.IsMappedBy) == 1
            assert texture.IsMappedBy[0].Mode == "COORD"
        elif uv_mode == "Camera":
            assert len(texture.IsMappedBy) == 1
            assert texture.IsMappedBy[0].Mode == "COORD-EYE"
        elif uv_mode == "UV":
            assert set(texture.IsMappedBy) == set(uv_maps)

    def test_add_surface_textures_from_data(self):
        texture_data = self.get_default_texture_data()

        textures = ifcopenshell.api.style.add_surface_textures(self.file, textures=texture_data)
        assert len(list(self.file)) == len(texture_data)

        for texture, data in zip(textures, texture_data):
            self.compare_texture_to_data(texture, data)

    def test_add_surface_textures_from_data_with_uv_mode(self):
        texture_data = self.get_default_texture_data()
        texture_data[0]["uv_mode"] = "Generated"
        texture_data[1]["uv_mode"] = "Camera"
        texture_data[2]["uv_mode"] = "UV"
        texture_data[3]["uv_mode"] = None

        textures = ifcopenshell.api.style.add_surface_textures(self.file, textures=texture_data)
        for texture, data in zip(textures, texture_data):
            self.compare_texture_to_data(texture, data)

    # NOTE: IfcTextureCoordinate doesn't have Maps in IFC2X3
    def test_add_surface_textures_from_data_with_uv_maps(self):
        texture_data = self.get_default_texture_data()
        texture_data[0]["uv_mode"] = "Generated"
        texture_data[1]["uv_mode"] = "Camera"
        texture_data[2]["uv_mode"] = "UV"
        texture_data[3]["uv_mode"] = None

        uv_maps = [self.file.create_entity("IfcTextureCoordinateGenerator", Maps=[], Mode="COORD") for i in range(5)]
        textures = ifcopenshell.api.style.add_surface_textures(self.file, textures=texture_data, uv_maps=uv_maps)
        for texture, data in zip(textures, texture_data):
            self.compare_texture_to_data(texture, data, uv_maps)
