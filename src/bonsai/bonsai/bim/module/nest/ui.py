# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

from bpy.types import Panel
from bonsai.bim.module.nest.data import NestData
from bonsai.bim.ifc import IfcStore


class BIM_PT_nest(Panel):
    bl_label = "Nest"
    bl_idname = "BIM_PT_nest"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_tab_object_metadata"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        if not IfcStore.get_file().by_id(props.ifc_definition_id).is_a("IfcObjectDefinition"):
            return False
        return True

    def draw(self, context):
        layout = self.layout
        if not NestData.is_loaded:
            NestData.load()

        props = context.active_object.BIMObjectNestProperties

        if props.is_editing:
            row = layout.row(align=True)
            row.prop(props, "relating_object", text="")
            if props.relating_object:
                op = row.operator("bim.nest_assign_object", icon="CHECKMARK", text="")
                op.relating_object = props.relating_object.BIMObjectProperties.ifc_definition_id
            row.operator("bim.disable_editing_nest", icon="CANCEL", text="")
        else:
            row = layout.row(align=True)
            if NestData.data["has_relating_object"]:
                row.label(text=NestData.data["relating_object_label"], icon="TRIA_UP")
                op = row.operator("bim.select_nest", icon="RESTRICT_SELECT_OFF", text="")
                op.obj = context.active_object.name
                row.operator("bim.enable_editing_nest", icon="GREASEPENCIL", text="")
                op = row.operator("bim.nest_unassign_object", icon="X", text="")
            else:
                row.label(text="No Host", icon="TRIA_UP")
                row.operator("bim.enable_editing_nest", icon="GREASEPENCIL", text="")

        row = layout.row(align=True)
        total_components = NestData.data["total_components"]
        if total_components == 0:
            row.label(text="No Components", icon="TRIA_DOWN")
        elif total_components == 1:
            row.label(text="1 Component", icon="TRIA_DOWN")
        else:
            row.label(text=f"{total_components} Components", icon="TRIA_DOWN")

        if NestData.data["has_related_objects"]:
            op = row.operator("bim.select_components", icon="RESTRICT_SELECT_OFF", text="")
            op.obj = context.active_object.name
