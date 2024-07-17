# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blenderbim.tool as tool
import os


def refresh():
    WebData.is_loaded = False


class WebData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "IFC_File": cls.ifc_file_name(),
        }
        cls.is_loaded = True

    @classmethod
    def ifc_file_name(cls):
        filename = os.path.basename(bpy.context.scene.BIMProperties.ifc_file)
        return filename
