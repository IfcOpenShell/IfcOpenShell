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

import bonsai.tool as tool
import bonsai.bim.module.type.prop as type_prop
from bpy.types import Panel
from bonsai.bim.ifc import IfcStore
from bonsai.bim.helper import prop_with_search
from bonsai.bim.module.type.data import TypeData


class BIM_PT_type(Panel):
    bl_label = "Type"
    bl_idname = "BIM_PT_type"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_tab_object_metadata"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        element = tool.Ifc.get_entity(context.active_object)
        if not element:
            return False
        if not element.is_a("IfcProduct") and not element.is_a("IfcTypeProduct"):
            return True
        return True

    def draw(self, context):
        if not TypeData.is_loaded:
            TypeData.load()

        oprops = context.active_object.BIMObjectProperties

        if TypeData.data["is_product"]:
            self.draw_product_ui(context)
        else:
            self.draw_type_ui(context)

    def draw_type_ui(self, context):
        props = context.active_object.BIMTypeProperties
        oprops = context.active_object.BIMObjectProperties
        row = self.layout.row(align=True)
        row.label(text=f"{TypeData.data['total_instances']} Typed Objects")
        select_type_objects_row = row.row(align=True)
        select_type_objects_row.operator("bim.select_type_objects", icon="RESTRICT_SELECT_OFF", text="")
        select_type_objects_row.enabled = int(TypeData.data["total_instances"]) > 0
        op = row.operator("bim.duplicate_type", icon="DUPLICATE", text="")
        op.element = context.active_object.BIMObjectProperties.ifc_definition_id
        row.operator("bim.auto_rename_occurrences", icon="ITALIC", text="")

    def draw_product_ui(self, context):
        layout = self.layout
        props = context.active_object.BIMTypeProperties
        oprops = context.active_object.BIMObjectProperties

        if props.is_editing_type:
            row = layout.row(align=True)
            row_object = layout.row(align=True)

            row.prop(props, "relating_type_class", text="")
            if type_prop.get_relating_type(None, context):
                prop_with_search(row, props, "relating_type", text="")
                row.operator("bim.assign_type", icon="CHECKMARK", text="")
                row_object.prop(props, "relating_type_object", icon="COPYDOWN")
            else:
                row.label(text="No Types Found")
            row.operator("bim.disable_editing_type", icon="CANCEL", text="")
        else:
            row = layout.row(align=True)
            if TypeData.data["relating_type"]:
                row.label(text=TypeData.data["relating_type"]["name"])
                op = row.operator("bim.select_type", icon="OBJECT_DATA", text="")
                op.relating_type = 0  # will only select the relating types of only the selected objects
                row.operator("bim.select_similar_type", icon="RESTRICT_SELECT_OFF", text="")
                row.operator("bim.enable_editing_type", icon="GREASEPENCIL", text="")
                row.operator("bim.unassign_type", icon="X", text="")
            else:
                row.label(text="No Relating Type")
                row.operator("bim.enable_editing_type", icon="GREASEPENCIL", text="")


def add_object_button(self, context):
    self.layout.operator("bim.add_constr_type_instance", icon="PLUGIN")
