# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 @Andrej730
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


import os
import bpy
import blenderbim.tool as tool
from blenderbim.bim.helper import prop_with_search
from blenderbim.bim.module.model.data import AuthoringData
from bpy.types import WorkSpaceTool
from blenderbim.bim.ifc import IfcStore
import blenderbim.bim.handler


# declaring it here to avoid circular import problems
class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}

class CoveringTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.covering_tool"
    bl_label = "Covering Tool"
    bl_description = "Create and edit coverings"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.covering")
    bl_widget = None
    bl_keymap = tool.Blender.get_default_selection_keypmap() + (
        ("bim.covering_hotkey", {"type": "A", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_A")]}),
    )

    @classmethod
    def draw_settings(cls, context, layout, ws_tool):
        CoveringToolUI.draw(context, layout, ifc_element_type="IfcCoveringType")

def add_layout_hotkey(layout, text, hotkey, description):
    args = ["covering", layout, text, hotkey, description]
    tool.Blender.add_layout_hotkey_operator(*args)

class CoveringToolUI:
    @classmethod
    def draw(cls, context, layout, ifc_element_type = None):
        cls.layout = layout
        cls.props = context.scene.BIMModelProperties
        cls.covering_props = context.scene.BIMCoveringProperties

        row = cls.layout.row(align=True)
        if not tool.Ifc.get():
            row.label(text="No IFC Project", icon="ERROR")
            return

        if not AuthoringData.is_loaded:
            AuthoringData.load(ifc_element_type)
        elif AuthoringData.data["ifc_element_type"] != ifc_element_type:
            AuthoringData.load(ifc_element_type)


        if context.region.type == "TOOL_HEADER":
            cls.draw_header_interface()
        elif context.region.type in ("UI", "WINDOW"):
            cls.draw_basic_bim_tool_interface()

        cls.draw_default_interface()



    @classmethod
    def draw_header_interface(cls):
        cls.draw_type_selection_interface()

    @classmethod
    def draw_default_interface(cls):
        if AuthoringData.data["ifc_classes"]:
            row = cls.layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_A")
            active_obj = bpy.context.active_object
            element = tool.Ifc.get_entity(active_obj)

            if AuthoringData.data["predefined_type"] == "FLOORING":
                if element and bpy.context.selected_objects and element.is_a("IfcWall"):
                    op = row.operator("bim.add_instance_flooring_coverings_from_walls")
#                elif element and bpy.context.selected_objects and element.is_a("IfcSpace"):
#                    op. = row.operator("bim.add_istance_flooring_from_spaces"):
                else:
#                    op = row.operator("bim.add_instance_flooring_from_cursor")
                    op = row.operator("bim.add_constr_type_instance", text="Add")
                    op.from_invoke = True
                    if cls.props.relating_type_id.isnumeric():
                        op.relating_type_id = int(cls.props.relating_type_id)

#            elif AuthoringData.data["predefined_type"] == "CEILING":
#                row = cls.layout.row(align=True)
#                row.prop(data=cls.props, property="ceiling_height", text="ceiling height")
#                if element and bpy.context.selected_objects and element.is_a("IfcWall"):
#                    op = row.operator("bim.add_instance_ceiling_coverings_from_walls")
#                elif element and bpy.context.selected_objects and element.is_a("IfcSpace"):
#                    op. = row.operator("bim.add_istance_flooring_from_spaces"):
#                else:
#                    op = row.operator("bim.add_instance_ceiling_from_cursor")
#                    op = row.operator("bim.add_constr_type_instance", text="Add")
#                    op.from_invoke = True
#                    if cls.props.relating_type_id.isnumeric():
#                        op.relating_type_id = int(cls.props.relating_type_id)
            else:
                op = row.operator("bim.add_constr_type_instance", text="Add")
                op.from_invoke = True
                if cls.props.relating_type_id.isnumeric():
                    op.relating_type_id = int(cls.props.relating_type_id)

    @classmethod
    def draw_type_selection_interface(cls):
        # shared by both sidebar and header
        row = cls.layout.row(align=True)
        if AuthoringData.data["ifc_classes"]:
            row = cls.layout.row(align=True)
            row.label(text="", icon="FILE_3D")
            prop_with_search(row, cls.props, "relating_type_id", text="")
            row.operator("bim.launch_type_manager", icon="LIGHTPROBE_GRID", text="")
        else:
            row.label(text=f"No {AuthoringData.data['ifc_element_type']} Found", icon="ERROR")
            row = cls.layout.row()
            row.operator("bim.launch_type_manager", icon="LIGHTPROBE_GRID", text="Launch Type Manager")

    @classmethod
    def draw_basic_bim_tool_interface(cls):
        cls.draw_type_selection_interface()

        if AuthoringData.data["ifc_classes"]:
            if cls.props.ifc_class:
                box = cls.layout.box()
                if AuthoringData.data["type_thumbnail"]:
                    box.template_icon(icon_value=AuthoringData.data["type_thumbnail"], scale=5)
                else:
                    op = box.operator("bim.load_type_thumbnails", text="Load Thumbnails", icon="FILE_REFRESH")
                    op.ifc_class = cls.props.ifc_class


class Hotkey(bpy.types.Operator, Operator):
    bl_idname = "bim.covering_hotkey"
    bl_label = "Hotkey"
    bl_options = {"REGISTER", "UNDO"}
    hotkey: bpy.props.StringProperty()
    description: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    @classmethod
    def description(cls, context, operator):
        return operator.description or ""

    def _execute(self, context):
#        self.props = context.scene.BIMCoveringProperties
        getattr(self, f"hotkey_{self.hotkey}")()

    def invoke(self, context, event):
        # https://blender.stackexchange.com/questions/276035/how-do-i-make-operators-remember-their-property-values-when-called-from-a-hotkey
        # self.props = context.scene.BIMSpatialProperties
        return self.execute(context)

    def draw(self, context):
        pass

    def hotkey_S_A(self):
        active_obj = bpy.context.active_object
        element = tool.Ifc.get_entity(active_obj)
        if element and bpy.context.selected_objects and element.is_a("IfcWall"):
            bpy.ops.bim.add_instance_flooring_coverings_from_walls()
        else:
            bpy.ops.bim.add_constr_type_instance()

