# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import bonsai.tool as tool
import os


def refresh():
    WebData.is_loaded = False


class WebData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "ifc_file": cls.get_ifc_file_name(),
            "is_dirty": cls.get_is_dirty(),
        }
        cls.is_loaded = True

    @classmethod
    def get_ifc_file_name(cls):
        filename = os.path.basename(bpy.context.scene.BIMProperties.ifc_file)
        return filename

    @classmethod
    def get_is_dirty(cls):
        return bpy.context.scene.BIMProperties.is_dirty
