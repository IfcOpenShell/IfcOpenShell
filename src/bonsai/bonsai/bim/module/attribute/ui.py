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

import bonsai.bim.helper
import bpy.types
from bpy.types import Panel
from bonsai.bim.module.attribute.data import AttributesData
import bonsai.tool as tool


def draw_ui(context: bpy.types.Context, layout: bpy.types.UILayout, attributes) -> None:
    obj = context.active_object
    assert obj
    props = tool.Blender.get_object_attribute_props(obj)

    if props.is_editing_attributes:
        row = layout.row(align=True)
        row.operator("bim.edit_attributes", icon="CHECKMARK", text="Save Attributes")
        row.operator("bim.disable_editing_attributes", icon="CANCEL", text="")

        bonsai.bim.helper.draw_attributes(props.attributes, layout, copy_operator="bim.copy_attribute_to_selection")
    else:
        row = layout.row()
        op = row.operator("bim.enable_editing_attributes", icon="GREASEPENCIL", text="Edit")

        for attribute in attributes:
            row = layout.row(align=True)
            row.label(text=attribute["name"])
            value = bonsai.bim.helper.get_display_value(attribute["value"])
            op = row.operator("bim.select_similar", text=value, icon="NONE", emboss=False)
            op.key = attribute["name"]

    # TODO: reimplement, see #1222
    # if "IfcSite/" in context.active_object.name or "IfcBuilding/" in context.active_object.name:
    #    self.draw_addresses_ui()


class BIM_PT_object_attributes(Panel):
    bl_label = "Attributes"
    bl_idname = "BIM_PT_object_attributes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_tab_object_metadata"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get_entity(context.active_object)

    def draw(self, context):
        if not AttributesData.is_loaded:
            AttributesData.load()
        draw_ui(context, self.layout, AttributesData.data["attributes"])
