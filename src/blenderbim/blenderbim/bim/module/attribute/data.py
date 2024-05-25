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
import ifcopenshell
import blenderbim.tool as tool


def refresh():
    AttributesData.is_loaded = False


class AttributesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"attributes": cls.attributes()}
        cls.is_loaded = True

    @classmethod
    def attributes(cls):
        results = []
        element = tool.Ifc.get_entity(bpy.context.active_object)
        data = element.get_info()
        if hasattr(element, "GlobalId"):
            excluded_keys = ["id", "type"]
        else:
            excluded_keys = ["type"]
        for key, value in data.items():
            if value is None or isinstance(value, ifcopenshell.entity_instance) or key in excluded_keys:
                continue
            if key == "id":
                key = "STEP ID"
            results.append({"name": key, "value": str(value)})
        return results
