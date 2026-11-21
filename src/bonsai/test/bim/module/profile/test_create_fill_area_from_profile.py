# This file was generated with the assistance of an AI coding tool.
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

import bpy
import ifcopenshell.api.profile

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestCreateFillAreaFromProfile(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        bpy.ops.bim.add_drawing()
        camera = next(o for o in bpy.data.objects if o.type == "CAMERA")
        bpy.context.scene.camera = camera
        tool.Drawing.get_document_props().active_drawing_id = tool.Ifc.get_entity(camera).id()
        ifc = tool.Ifc.get()
        profile = ifcopenshell.api.profile.add_parameterized_profile(ifc, ifc_class="IfcRectangleProfileDef")
        profile.ProfileName = "Rect"
        profile.XDim = profile.YDim = 0.5
        bpy.ops.bim.load_profiles()

        bpy.ops.bim.create_fill_area_from_profile()

        assert len(ifc.by_type("IfcAnnotationFillArea")) == 1
