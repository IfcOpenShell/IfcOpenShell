
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
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.style.data import Data as StyleData


def sync_name(usecase_path, ifc_file, settings):
    if "Name" not in settings["attributes"]:
        return
    obj = IfcStore.get_element(settings["product"].id())
    if not obj:
        return
    if isinstance(obj, bpy.types.Object):
        new_name = "{}/{}".format(settings["product"].is_a(), settings["attributes"]["Name"] or "Unnamed")
    elif isinstance(obj, bpy.types.Material):
        new_name = settings["attributes"]["Name"] or "Unnamed"
        if obj.BIMMaterialProperties.ifc_style_id:
            IfcStore.get_file().by_id(obj.BIMMaterialProperties.ifc_style_id).Name = new_name
            StyleData.load(IfcStore.get_file(), obj.BIMMaterialProperties.ifc_style_id)
    collection = bpy.data.collections.get(obj.name)
    if collection:
        collection.name = new_name
    obj.name = new_name
