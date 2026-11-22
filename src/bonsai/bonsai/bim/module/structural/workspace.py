# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 @Andrej730
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


import os
from functools import partial

import bpy
from bpy.types import WorkSpaceTool

import bonsai.tool as tool
from bonsai.bim.module.structural.data import StructuralAnalysisModelsData


class StructuralTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.structural_tool"
    bl_label = "Structural Tool"
    bl_description = "Gives you Structure related superpowers"
    # TODO: replace with structural icon
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.structural")
    bl_widget = None
    bl_keymap = tool.Blender.get_default_selection_keypmap() + (
        ("bim.structural_hotkey", {"type": "A", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_A")]}),
        ("bim.structural_hotkey", {"type": "B", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_B")]}),
        ("bim.structural_hotkey", {"type": "C", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_C")]}),
        ("bim.structural_hotkey", {"type": "L", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_L")]}),
        ("bim.structural_hotkey", {"type": "E", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_E")]}),
        ("bim.structural_hotkey", {"type": "P", "value": "PRESS", "ctrl": True}, {"properties": [("hotkey", "C_P")]}),
        ("bim.structural_hotkey", {"type": "P", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_P")]}),
    )

    def draw_settings(context, layout, ws_tool):
        # Unlike operators, Blender doesn't treat workspace tools as a class, so we'll create our own.
        StructuralToolUI.draw(context, layout)


add_layout_hotkey = partial(tool.Blender.add_layout_hotkey_operator, tool_name="structural", module_name=__name__)


# NOTES before adding new operators:
# - add scene.BIMStructuralProperties
# - add StructuralData


class StructuralToolUI:
    @classmethod
    def draw(cls, context, layout):
        cls.layout = layout
        cls.props = tool.Structural.get_structural_props()

        row = cls.layout.row(align=True)
        if not tool.Ifc.get():
            row.label(text="No IFC Project", icon="ERROR")
            return

        if not StructuralAnalysisModelsData.is_loaded:
            StructuralAnalysisModelsData.load()

        cls.draw_type_selection_interface(context)

        if context.active_object and context.selected_objects:
            cls.draw_selected_object_interface(context)

    @classmethod
    def draw_selected_object_interface(cls, context):
        elements = [e for o in context.selected_objects if (e := tool.Ifc.get_entity(o))]
        if not (items := tool.Structural.get_structural_items(elements)):
            return
        row = cls.layout.row(align=True)
        has_connections = any(i.is_a("IfcStructuralConnection") for i in items)
        if has_connections and any(i.is_a("IfcStructuralMember") for i in items):
            add_layout_hotkey(row, "Connect", "S_C", bpy.ops.bim.connect_structural_items.__doc__)
        if has_connections:
            add_layout_hotkey(row, "Support", "S_B", bpy.ops.bim.add_structural_support.__doc__)

        if model := tool.Structural.get_current_structural_analysis_model():
            in_model = [tool.Structural.is_in_structural_analysis_model(i, model) for i in items]
            if not all(in_model):
                add_layout_hotkey(row, "Assign", "C_P", "Assign the selected structural items to the current model")
            if any(in_model):
                add_layout_hotkey(
                    row, "Unassign", "A_P", "Unassign the selected structural items from the current model"
                )

        add_layout_hotkey(row, "Apply Load", "S_L", "Apply a force to the selected structural items")

        active = tool.Ifc.get_entity(context.active_object)
        if active and active.is_a() in ("IfcStructuralCurveMember", "IfcStructuralCurveConnection"):
            props = tool.Structural.get_object_structural_props(context.active_object)
            if props.is_editing_axis:
                row = cls.layout.row(align=True)
                row.prop(props, "axis_angle")
                row.operator("bim.edit_structural_item_axis", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_structural_item_axis", text="", icon="CANCEL")
            else:
                add_layout_hotkey(row, "Edit Axis", "A_E", "Rotate the cross-section of the active curve item")

    @classmethod
    def draw_type_selection_interface(cls, context):
        row = cls.layout.row(align=True)
        row.prop(cls.props, "structural_item_class", text="")
        if tool.Structural.get_structural_item_predefined_types(cls.props.structural_item_class):
            row.prop(cls.props, "structural_item_predefined_type", text="")
        # Next to the class it adds, as the Add of the Wall and Slab tools follows their type
        add_layout_hotkey(row, "Add", "S_A", "Add a structural item of the chosen class at the 3D cursor")

        row = cls.layout.row(align=True)
        if not StructuralAnalysisModelsData.data["models"]:
            row.operator("bim.add_structural_analysis_model", text="Add Analysis Model", icon="ADD")
        elif current := StructuralAnalysisModelsData.data["current_model"]:
            row.menu("BIM_MT_structural_analysis_models", text=current["name"], icon="MOD_SIMPLIFY")
        else:
            row.menu("BIM_MT_structural_analysis_models", text="No Current Analysis Model", icon="ERROR")


class Hotkey(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.structural_hotkey"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    hotkey: bpy.props.StringProperty()
    description: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    @classmethod
    def description(cls, context, properties):
        return properties.description or ""

    def _execute(self, context):
        # self.props = tool.Structural.get_structural_props()
        getattr(self, f"hotkey_{self.hotkey}")()

    def invoke(self, context, event):
        # https://blender.stackexchange.com/questions/276035/how-do-i-make-operators-remember-their-property-values-when-called-from-a-hotkey
        # self.props = tool.Structural.get_structural_props()
        return self.execute(context)

    def draw(self, context):
        pass

    def hotkey_S_A(self):
        bpy.ops.bim.add_structural_item()

    def hotkey_S_B(self):
        bpy.ops.bim.add_structural_support("INVOKE_DEFAULT")

    def hotkey_S_C(self):
        bpy.ops.bim.connect_structural_items()

    def hotkey_S_L(self):
        bpy.ops.bim.apply_structural_load("INVOKE_DEFAULT")

    def hotkey_A_E(self):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj) if obj else None
        if not element or element.is_a() not in ("IfcStructuralCurveMember", "IfcStructuralCurveConnection"):
            self.report({"INFO"}, "Make a curve member or curve connection active to edit its axis.")
            return
        if not tool.Structural.get_object_structural_props(obj).is_editing_axis:
            bpy.ops.bim.enable_editing_structural_item_axis()

    def hotkey_C_P(self):
        bpy.ops.bim.assign_structural_items_to_current_model()

    def hotkey_A_P(self):
        bpy.ops.bim.assign_structural_items_to_current_model(unassign=True)
