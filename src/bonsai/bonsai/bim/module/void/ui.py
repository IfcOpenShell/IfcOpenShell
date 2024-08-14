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
import bonsai.tool as tool
from bpy.types import Panel
from bonsai.bim.module.void.data import BooleansData, VoidsData


class BIM_PT_voids(Panel):
    bl_label = "Voids"
    bl_idname = "BIM_PT_voids"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_geometric_relationships"

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get_entity(context.active_object):
            return False
        return True

    def draw(self, context):
        if not VoidsData.is_loaded:
            VoidsData.load()

        props = context.active_object.BIMObjectProperties

        if len(context.selected_objects) == 2:
            row = self.layout.row(align=True)
            op = row.operator("bim.add_opening", icon="ADD", text="Add Opening")

        if VoidsData.data["active_opening"]:
            row = self.layout.row()
            op = row.operator("bim.remove_opening", icon="X", text="Remove Opening")
            op.opening_id = VoidsData.data["active_opening"]

            if not VoidsData.data["fillings"]:
                row = self.layout.row()
                row.label(text="No Fillings", icon="SELECT_INTERSECT")

            for filling in VoidsData.data["fillings"]:
                row = self.layout.row(align=True)
                row.label(text=filling["Name"], icon="SELECT_INTERSECT")
                row.operator("bim.remove_filling", icon="X", text="").filling = filling["id"]
        else:
            if not VoidsData.data["openings"]:
                row = self.layout.row()
                row.label(text="No Openings", icon="SELECT_SUBTRACT")

            for opening in VoidsData.data["openings"]:
                if opening["HasFillings"]:
                    for filling in opening["HasFillings"]:
                        row = self.layout.row(align=True)
                        row.label(text=opening["Name"], icon="SELECT_SUBTRACT")
                        row.label(text=filling["Name"], icon="SELECT_INTERSECT")
                else:
                    row = self.layout.row(align=True)
                    row.label(text=opening["Name"], icon="SELECT_SUBTRACT")
                row.operator("bim.remove_opening", icon="X", text="").opening_id = opening["id"]


class BIM_PT_booleans(Panel):
    bl_label = "Booleans"
    bl_idname = "BIM_PT_booleans"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_geometric_relationships"

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and hasattr(context.active_object.data, "BIMMeshProperties")
            and (
                context.active_object.data.BIMMeshProperties.ifc_definition_id
                or context.active_object.data.BIMMeshProperties.ifc_boolean_id
            )
        )

    def draw(self, context):
        if not BooleansData.is_loaded:
            BooleansData.load()

        if not context.active_object.data:
            return
        layout = self.layout
        props = context.active_object.data.BIMMeshProperties

        if context.active_object.data.BIMMeshProperties.ifc_definition_id:
            row = layout.row(align=True)
            total_booleans = BooleansData.data["total_booleans"]
            manual_booleans = BooleansData.data["manual_booleans"]
            row.label(text=f"{len(total_booleans)} Booleans Found ({len(manual_booleans)} Manual)")
            row.operator("bim.add_boolean", text="", icon="ADD")
            show_boolean_button = row.row(align=True)
            show_boolean_button.operator("bim.show_booleans", text="", icon="HIDE_OFF")
            show_boolean_button.enabled = len(total_booleans) > 0
            row.operator("bim.hide_booleans", text="", icon="HIDE_ON")

            booleans_are_manual = len(manual_booleans) == len(total_booleans)
            op = row.operator(
                "bim.booleans_mark_as_manual", text="", icon="PINNED" if booleans_are_manual else "UNPINNED"
            )
            op.mark_as_manual = not booleans_are_manual

        elif context.active_object.data.BIMMeshProperties.ifc_boolean_id:
            upsteam_obj = context.active_object.data.BIMMeshProperties.obj
            upstream_obj_ifc_id = upsteam_obj.BIMObjectProperties.ifc_definition_id

            row = layout.row(align=True)
            row.label(text=upsteam_obj.name)
            row.operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = upstream_obj_ifc_id

            row = layout.row()
            row.operator("bim.remove_booleans", text="Remove Boolean", icon="X")
