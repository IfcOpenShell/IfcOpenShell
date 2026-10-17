# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

from unittest.mock import patch

import bpy
import ifcopenshell.geom

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestCreateDrawingHlrPolyOption(NewFile):
    def create_drawing(self, should_use_hlr_poly):
        bpy.ops.bim.create_project()
        tool.Project.save_test_project()
        bpy.ops.mesh.primitive_cube_add(size=2)
        bpy.ops.bim.assign_class(ifc_class="IfcColumn")
        bpy.ops.bim.load_drawings()
        bpy.ops.bim.add_drawing()
        drawing = tool.Ifc.get().by_type("IfcAnnotation")[0]
        bpy.ops.bim.activate_drawing(drawing=drawing.id())
        tool.Drawing.get_document_props().should_use_hlr_poly = should_use_hlr_poly

        used = []
        serializer = ifcopenshell.geom.serializers.svg

        def spy(buffer, settings, *args, **kwargs):
            used.append(settings.get("svg-poly"))
            return serializer(buffer, settings, *args, **kwargs)

        with patch.object(ifcopenshell.geom.serializers, "svg", spy):
            bpy.ops.bim.create_drawing()
        return used

    def test_polygonal_hlr_is_used_when_the_option_is_enabled(self):
        assert self.create_drawing(True) == [True]

    def test_exact_hlr_is_used_when_the_option_is_disabled(self):
        assert self.create_drawing(False) == [False]
