
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

from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.group.data import Data


class BIM_PT_groups(Panel):
    bl_label = "IFC Groups"
    bl_idname = "BIM_PT_groups"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        self.props = context.scene.BIMGroupProperties

        row = self.layout.row(align=True)
        row.label(text="{} Groups Found".format(len(Data.groups)), icon="OUTLINER")
        if self.props.is_editing:
            row.operator("bim.add_group", text="", icon="ADD")
            row.operator("bim.disable_group_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_groups", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_groups",
                "",
                self.props,
                "groups",
                self.props,
                "active_group_index",
            )

        if self.props.active_group_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        for attribute in self.props.group_attributes:
            row = self.layout.row(align=True)
            row.prop(attribute, "string_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")



class BIM_UL_groups(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
            op = row.operator("bim.assign_group_to_many", text="", icon="ADD", emboss=False)
            op.group = item.ifc_definition_id
            op = row.operator("bim.unassign_group_from_many", text="", icon="REMOVE", emboss=False)
            op.group = item.ifc_definition_id

            if context.scene.BIMGroupProperties.active_group_id == item.ifc_definition_id:
                op = row.operator("bim.select_group_products", text="", icon="RESTRICT_SELECT_OFF")
                op.group = item.ifc_definition_id
                row.operator("bim.edit_group", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_group", text="", icon="CANCEL")
            elif context.scene.BIMGroupProperties.active_group_id:
                op = row.operator("bim.select_group_products", text="", icon="RESTRICT_SELECT_OFF")
                op.group = item.ifc_definition_id
                row.operator("bim.remove_group", text="", icon="X").group = item.ifc_definition_id
            else:
                op = row.operator("bim.select_group_products", text="", icon="RESTRICT_SELECT_OFF")
                op.group = item.ifc_definition_id
                op = row.operator("bim.enable_editing_group", text="", icon="GREASEPENCIL")
                op.group = item.ifc_definition_id
                row.operator("bim.remove_group", text="", icon="X").group = item.ifc_definition_id
