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
import bpy
import bonsai.tool as tool
from bpy.types import Panel, UIList
from bonsai.bim.module.void.data import BooleansData, VoidsData
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    import bpy._typing.rna_enums as rna_enums


OPENING_ICON = "SELECT_SUBTRACT"
FILLING_ICON = "SELECT_INTERSECT"
VOIDED_ELEMENT_ICON = "SELECT_EXTEND"


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

        row = self.layout.row(align=True)
        op = row.operator("bim.add_opening", icon="ADD", text="Add Opening")

        if VoidsData.data["active_opening"]:
            row = self.layout.row()
            op = row.operator("bim.remove_opening", icon="X", text="Remove Opening")
            op.opening_id = VoidsData.data["active_opening"]

            if not VoidsData.data["fillings"]:
                row = self.layout.row()
                row.label(text="No Fillings", icon=FILLING_ICON)

            for filling in VoidsData.data["fillings"]:
                row = self.layout.row(align=True)
                self.draw_selectable_element_ui(row, filling, "filling", FILLING_ICON)
                row.operator("bim.remove_filling", icon="X", text="").filling = filling["id"]

            if voided := VoidsData.data["voided_element"]:
                row = self.layout.row(align=True)
                self.draw_selectable_element_ui(row, voided, "voided", VOIDED_ELEMENT_ICON)

        else:
            if not VoidsData.data["openings"]:
                row = self.layout.row()
                row.label(text="No Openings", icon=OPENING_ICON)

            for opening in VoidsData.data["openings"]:
                if opening["HasFillings"]:
                    for filling in opening["HasFillings"]:
                        row = self.layout.row(align=True)
                        row.label(text=opening["Name"], icon=OPENING_ICON)
                        self.draw_selectable_element_ui(row, filling, "filling", FILLING_ICON)
                else:
                    row = self.layout.row(align=True)
                    row.label(text=opening["Name"], icon=OPENING_ICON)
                row.operator("bim.remove_opening", icon="X", text="").opening_id = opening["id"]

            if (opening := VoidsData.data["filled_voids"]) is None:
                row = self.layout.row()
                row.label(text="No Voids Filled", icon=VOIDED_ELEMENT_ICON)
            else:
                row = self.layout.row()
                row.label(text="Voided Element:", icon=VOIDED_ELEMENT_ICON)
                row = self.layout.row(align=True)
                row.label(text=opening["Name"], icon=OPENING_ICON)
                voided_element = opening["VoidsElements"]
                if voided_element is not None:
                    self.draw_selectable_element_ui(row, voided_element, "voided", VOIDED_ELEMENT_ICON)

    def draw_selectable_element_ui(
        self, layout: bpy.types.UILayout, element_data: dict[str, Any], object_hint: str, icon: rna_enums.IconItems
    ) -> None:
        layout.label(text=element_data["Name"], icon=icon)
        op = layout.operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF")
        op.ifc_id = element_data["id"]
        op.tooltip = f"Select {object_hint} object."


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
            (obj := context.active_object) is not None
            and isinstance(data := obj.data, bpy.types.Mesh)
            and (mesh_props := tool.Geometry.get_mesh_props(data))
            and (mesh_props.ifc_definition_id or mesh_props.ifc_boolean_id)
        )

    def draw(self, context):
        if not BooleansData.is_loaded:
            BooleansData.load()

        obj = context.active_object
        assert obj
        mesh = obj.data
        assert isinstance(mesh, bpy.types.Mesh)

        layout = self.layout
        props = tool.Feature.get_boolean_props()

        if tool.Geometry.get_mesh_props(mesh).ifc_definition_id:
            row = layout.row(align=True)
            total_booleans = BooleansData.data["total_booleans"]
            manual_booleans = BooleansData.data["manual_booleans"]
            row.label(text=f"{len(total_booleans)} Booleans Found ({len(manual_booleans)} Manual)")
            if props.is_editing:
                row.operator("bim.disable_editing_booleans", icon="CANCEL", text="")
            else:
                row.operator("bim.enable_editing_booleans", icon="IMPORT", text="")
            booleans_are_manual = len(manual_booleans) == len(total_booleans)
            op = row.operator(
                "bim.booleans_mark_as_manual", text="", icon="PINNED" if booleans_are_manual else "UNPINNED"
            )
            op.mark_as_manual = not booleans_are_manual

        if not props.is_editing:
            return

        row = layout.row(align=True)
        row.prop(props, "operator", text="")
        row.operator("bim.add_boolean", text="", icon="ADD")

        row = layout.row(align=True)
        row.alignment = "RIGHT"
        row.operator("bim.select_boolean", text="", icon="RESTRICT_SELECT_OFF")
        row.operator("bim.remove_boolean", text="", icon="X")

        self.layout.template_list("BIM_UL_booleans", "", props, "booleans", props, "active_boolean_index")


class BIM_UL_booleans(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            if item.operator == "DIFFERENCE":
                icon = "SELECT_DIFFERENCE"
            elif item.operator == "INTERSECTION":
                icon = "SELECT_INTERSECT"
            elif item.operator == "UNION":
                icon = "SELECT_EXTEND"
            elif "IfcHalfSpaceSolid" in item.name:
                icon = "NORMALS_FACE"
            else:
                icon = "MESH_DATA"
            row = layout.row(align=True)
            for i in range(0, item.level):
                row.label(text="", icon="BLANK1")
            row.label(text=item.name, icon=icon)
