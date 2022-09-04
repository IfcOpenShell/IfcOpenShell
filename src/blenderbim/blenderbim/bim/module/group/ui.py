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
    bl_parent_id = "BIM_PT_project_setup"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        self.props = context.scene.BIMGroupProperties

        row = self.layout.row(align=True)
        row.label(text=f"{len(Data.groups)} Groups Found", icon="OUTLINER")
        if self.props.is_editing:
            row.operator("bim.add_group", text="", icon="ADD").group = 0
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


class BIM_PT_object_groups(Panel):
    bl_label = "IFC Groups"
    bl_idname = "BIM_PT_object_groups"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_utilities_object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        return IfcStore.get_file() and context.active_object.BIMObjectProperties.ifc_definition_id

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        self.props = context.scene.BIMGroupProperties
        row = self.layout.row(align=True)
        if self.props.is_adding:
            row.label(text="Adding Groups", icon="OUTLINER")
            row.operator("bim.toggle_assigning_group", text="", icon="CANCEL")
            self.layout.template_list(
                "BIM_UL_object_groups",
                "",
                self.props,
                "groups",
                self.props,
                "active_group_index",
            )
        else:
            row.label(text=f"{len(Data.groups)} Groups in IFC Project", icon="OUTLINER")
            row.operator("bim.toggle_assigning_group", text="", icon="ADD")

        groups_object = Data.products.get(context.active_object.BIMObjectProperties.ifc_definition_id, [])
        for group_id in groups_object:
            row = self.layout.row(align=True)
            row.label(text=Data.groups[group_id].get("Name", "Unnamed"))
            op = row.operator("bim.unassign_group", text="", icon="X")
            op.group = group_id

        if not groups_object:
            self.layout.label(text="No Group associated with Active Object")


class BIM_UL_groups(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item:
            row = layout.row(align=True)
            for i in range(0, item.tree_depth):
                row.label(text="", icon="BLANK1")
            if item.has_children:
                op = row.operator(
                    "bim.toggle_group", icon="TRIA_DOWN" if item.is_expanded else "TRIA_RIGHT", text="", emboss=False
                )
                op.ifc_definition_id = item.ifc_definition_id
                op.index = index
                op.option = "Collapse" if item.is_expanded else "Expand"
            else:
                row.label(text="", icon="BLANK1")

            row.label(text=f"*{item.name}") if item.selection_query != "" else row.label(text=item.name)
            group_id = item.ifc_definition_id
            if context.scene.BIMGroupProperties.active_group_id == group_id:
                op = row.operator("bim.select_group_products", text="", icon="RESTRICT_SELECT_OFF")
                op.group = group_id
                row.operator("bim.edit_group", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_group", text="", icon="CANCEL")
            elif context.scene.BIMGroupProperties.active_group_id:
                op = row.operator("bim.select_group_products", text="", icon="RESTRICT_SELECT_OFF")
                op.group = group_id
                op = row.operator("bim.add_group", text="", icon="ADD")
                op.group = group_id
                op = row.operator("bim.remove_group", text="", icon="X")
                op.group = group_id
                if item.selection_query != "":
                    op = row.operator("bim.update_group", text="", icon="FILE_REFRESH")
                    op.group_id = item.ifc_definition_id
                    op.query = item.selection_query
            else:
                op = row.operator("bim.select_group_products", text="", icon="RESTRICT_SELECT_OFF")
                op.group = group_id
                op = row.operator("bim.enable_editing_group", text="", icon="GREASEPENCIL")
                op.group = group_id
                op = row.operator("bim.add_group", text="", icon="ADD")
                op.group = group_id
                op = row.operator("bim.remove_group", text="", icon="X")
                op.group = group_id
                if item.selection_query != "":
                    op = row.operator("bim.update_group", text="", icon="FILE_REFRESH")
                    op.group_id = item.ifc_definition_id
                    op.query = item.selection_query


class BIM_UL_object_groups(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item:
            row = layout.row(align=True)
            for i in range(0, item.tree_depth):
                row.label(text="", icon="BLANK1")
            if item.has_children:
                op = row.operator(
                    "bim.toggle_group", icon="TRIA_DOWN" if item.is_expanded else "TRIA_RIGHT", text="", emboss=False
                )
                op.ifc_definition_id = item.ifc_definition_id
                op.index = index
                op.option = "Collapse" if item.is_expanded else "Expand"
            else:
                row.label(text="", icon="BLANK1")
            row.label(text=item.name)
            op = row.operator("bim.remove_group", text="", icon="X")
            op.group = item.ifc_definition_id
            op = row.operator("bim.assign_group", text="", icon="ADD")
            op.group = item.ifc_definition_id
