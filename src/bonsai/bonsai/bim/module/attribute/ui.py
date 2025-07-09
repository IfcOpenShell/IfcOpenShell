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

from __future__ import annotations
import bonsai.bim.helper
import bpy.types
from bpy.types import Panel
from bonsai.bim.module.attribute.data import AttributesData
import bonsai.tool as tool
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bonsai.bim.module.attribute.prop import BIMExplorerProperties, ExplorerEntity


def draw_ui(context: bpy.types.Context, layout: bpy.types.UILayout, attributes) -> None:
    obj = context.active_object
    assert obj
    props = tool.Blender.get_object_attribute_props(obj)

    if props.is_editing_attributes:
        row = layout.row(align=True)
        row.operator("bim.edit_attributes", icon="CHECKMARK", text="Save Attributes")
        row.operator("bim.disable_editing_attributes", icon="CANCEL", text="")

        bonsai.bim.helper.draw_attributes(
            props.attributes, layout, copy_operator="bim.copy_attribute_to_selection", enable_search=True
        )
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


class BIM_PT_explorer(Panel):
    bl_label = "Explorer"
    bl_idname = "BIM_PT_explorer"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_project_setup"

    def draw(self, context, *, is_popup=False):
        assert (layout := self.layout)
        props = tool.Attribute.get_explorer_props()

        if is_popup:
            layout.label(text=props.ifc_class)
        else:
            if not props.is_loaded:
                row = layout.row(align=True)
                row.label(text="Explorer UI is not Loaded.")
                row.prop(props, "is_loaded", text="", icon="IMPORT")
                return

            row = layout.row(align=True)
            row.prop(props, "ifc_class", text="")
            row.prop(props, "is_loaded", text="", icon="CANCEL")

        active_entity = props.active_entity
        row = layout.row(align=True)
        row.label(text=f"{len(props.entities)} entities found")
        row.operator("bim.explorer_add_entity", text="", icon="ADD")

        if active_entity:
            if active_entity.ifc_definition_id == props.editing_entity_id:
                row.operator("bim.explorer_disable_editing_entity", icon="CANCEL", text="")
            else:
                row.operator("bim.explorer_enable_editing_entity", icon="GREASEPENCIL", text="")
            # TODO: 'Remove' button?

        layout.template_list("BIM_UL_explorer", "", props, "entities", props, "active_entity_index")

        if props.editing_entity_id:
            box = self.layout.box()
            # In popup we accept edits automatically for the convenience.
            # Othrewise it seems very unintuitive, when you need to click confirmation twice.
            if not is_popup:
                row = box.row(align=True)
                row.operator("bim.explorer_edit_entity", icon="CHECKMARK")
                row.operator("bim.explorer_disable_editing_entity", icon="CANCEL", text="")
            bonsai.bim.helper.draw_attributes(props.entity_attributes, box, enable_search=True)


class BIM_UL_explorer(bpy.types.UIList):
    def draw_item(
        self,
        context: bpy.types.Context,
        layout: bpy.types.UILayout,
        data: BIMExplorerProperties,
        item: ExplorerEntity,
        icon,
        active_data,
        active_propname,
    ) -> None:
        row = layout.row(align=True)

        if item.ifc_definition_id == data.editing_entity_id:
            row.label(text=item.name, icon="GREASEPENCIL")
        else:
            row.label(text=item.name)
