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
from bpy.types import Panel
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.attribute.data import AttributesData


def draw_ui(context, layout, attributes):
    obj = context.active_object
    oprops = obj.BIMObjectProperties
    props = obj.BIMAttributeProperties

    if props.is_editing_attributes:
        row = layout.row(align=True)
        op = row.operator("bim.edit_attributes", icon="CHECKMARK", text="Save Attributes")
        op.obj = obj.name
        op = row.operator("bim.disable_editing_attributes", icon="CANCEL", text="")
        op.obj = obj.name

        bonsai.bim.helper.draw_attributes(props.attributes, layout, copy_operator="bim.copy_attribute_to_selection")
    else:
        row = layout.row()
        op = row.operator("bim.enable_editing_attributes", icon="GREASEPENCIL", text="Edit")
        op.obj = obj.name

        for attribute in attributes:
            row = layout.row(align=True)
            row.label(text=attribute["name"])
            # row.label(text=attribute["value"])
            op = row.operator("bim.select_similar", text=attribute["value"], icon="NONE", emboss=False)
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
        if not context.active_object:
            return False
        if not IfcStore.get_element(context.active_object.BIMObjectProperties.ifc_definition_id):
            return False
        return bool(context.active_object.BIMObjectProperties.ifc_definition_id)

    def draw(self, context):
        if not AttributesData.is_loaded:
            AttributesData.load()
        draw_ui(context, self.layout, AttributesData.data["attributes"])
