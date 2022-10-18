# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
import blenderbim.bim.handler
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore


def sync_name(usecase_path, ifc_file, settings):
    if usecase_path == "attribute.edit_attributes":
        element = settings["product"]
    elif usecase_path == "style.edit_presentation_style":
        element = settings["style"]

    if "Name" not in settings["attributes"]:
        return
    obj = tool.Ifc.get_object(element)
    if not obj:
        return
    if isinstance(obj, bpy.types.Object):
        new_name = "{}/{}".format(element.is_a(), settings["attributes"]["Name"] or "Unnamed")
    elif isinstance(obj, bpy.types.Material):
        new_name = settings["attributes"]["Name"] or "Unnamed"
        material = tool.Ifc.get_entity(obj)
        if material and material != element:
            material.Name = new_name
        style = tool.Style.get_style(obj)
        if style and style != element:
            style.Name = new_name
    collection = bpy.data.collections.get(obj.name)
    if collection:
        collection.name = new_name
    obj.name = new_name
    blenderbim.bim.handler.refresh_ui_data()


class ConstrTypeEntityNotFound(Exception):
    pass

