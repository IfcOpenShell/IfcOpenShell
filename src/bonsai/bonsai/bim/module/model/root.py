# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.file
import bonsai.bim.handler
import bonsai.tool as tool
from bonsai.bim.ifc import IFC_CONNECTED_TYPE
from typing import Any


def sync_name(usecase_path: str, ifc_file: ifcopenshell.file, settings: dict[str, Any]) -> None:
    if usecase_path == "attribute.edit_attributes":
        element = settings["product"]
    elif usecase_path == "style.edit_presentation_style":
        element = settings["style"]
    else:
        raise Exception(f"Unsupported usecase: '{usecase_path}'.")

    element: ifcopenshell.entity_instance
    if "Name" not in settings["attributes"]:
        return
    obj = tool.Ifc.get_object(element)
    if not obj:
        return
    obj: IFC_CONNECTED_TYPE
    if isinstance(obj, bpy.types.Object):
        new_name = "{}/{}".format(element.is_a(), settings["attributes"]["Name"] or "Unnamed")
        collection = obj.BIMObjectProperties.collection
        if collection:
            collection.name = new_name
    elif isinstance(obj, bpy.types.Material):
        new_name = settings["attributes"]["Name"] or "Unnamed"
    obj.name = new_name
    bonsai.bim.handler.refresh_ui_data()
