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
import olca
import blenderbim.tool as tool


def refresh():
    LcaData.is_loaded = False


class LcaData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "product_systems": cls.product_systems(),
        }
        cls.is_loaded = True

    @classmethod
    def product_systems(cls):
        if not bpy.context.scene.BIMLCAProperties.is_connected:
            return []
        results = []
        client = olca.Client(context.preferences.addons["blenderbim"].preferences.openlca_port)
        try:
            results = [(ps.name, ps.name, "") for ps in client.get_all(olca.ProductSystem)]
        except:
            pass
        return results
