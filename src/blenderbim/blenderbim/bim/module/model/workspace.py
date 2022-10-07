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

import os
import bpy
import blenderbim.tool as tool
import blenderbim.bim.module.type.prop as type_prop
from blenderbim.bim.helper import prop_with_search, close_operator_panel
from bpy.types import WorkSpaceTool
from blenderbim.bim.module.model.data import AuthoringData
from blenderbim.bim.module.model import prop


class BimTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"

    bl_idname = "bim.bim_tool"
    bl_label = "BIM Tool"
    bl_description = "Gives you BIM authoring related superpowers"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.bim")
    bl_widget = None
    # https://docs.blender.org/api/current/bpy.types.KeyMapItems.html
    bl_keymap = (
        # ("bim.wall_tool_op", {"type": 'MOUSEMOVE', "value": 'ANY'}, {"properties": []}),
        # ("mesh.add_wall", {"type": 'LEFTMOUSE', "value": 'PRESS'}, {"properties": []}),
        ("bim.hotkey", {"type": "A", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_A")]}),
        ("bim.hotkey", {"type": "C", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_C")]}),
        ("bim.hotkey", {"type": "E", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_E")]}),
        ("bim.hotkey", {"type": "F", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_F")]}),
        ("bim.hotkey", {"type": "G", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_G")]}),
        ("bim.hotkey", {"type": "M", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_M")]}),
        ("bim.hotkey", {"type": "O", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_O")]}),
        ("bim.hotkey", {"type": "R", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_R")]}),
        ("bim.hotkey", {"type": "S", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_S")]}),
        ("bim.hotkey", {"type": "T", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_T")]}),
        ("bim.hotkey", {"type": "V", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_V")]}),
        ("bim.hotkey", {"type": "X", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_X")]}),
        ("bim.hotkey", {"type": "Y", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_Y")]}),
        ("bim.hotkey", {"type": "D", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_D")]}),
        ("bim.hotkey", {"type": "O", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_O")]}),
    )

    def draw_settings(context, layout, something):
        props = context.scene.BIMModelProperties
        is_tool_header = context.region.type == "TOOL_HEADER"
        is_sidebar = context.region.type == "UI"

        row = layout.row(align=True)
        if not tool.Ifc.get():
            row.label(text="No IFC Project", icon="ERROR")
            return

        if not AuthoringData.is_loaded:
            AuthoringData.load()

        ifc_classes = AuthoringData.data["ifc_classes"] if "ifc_classes" in AuthoringData.data else False
        relating_types_ids = (
            AuthoringData.data["relating_types_ids"] if "relating_types_ids" in AuthoringData.data else False
        )

        if ifc_classes and relating_types_ids and not props.icon_id and not is_tool_header:
            # hack Dion won't like to show a preview also on the first time the sidebar is shown
            bpy.app.timers.register(lambda: prop.update_ifc_class(props, "lost_context"))
            bpy.app.timers.register(lambda: prop.update_relating_type(props, "lost_context"))

        ifc_class = props.ifc_class
        relating_type_id = props.relating_type_id

        if is_tool_header:
            row = layout.row(align=True)
            if ifc_classes:
                row.label(text="", icon="FILE_VOLUME")
                row.prop(data=props, property="ifc_class", text="")
            else:
                row.label(text="No Construction Class", icon="FILE_VOLUME")
            row = layout.row(align=True)
            if relating_types_ids:
                row.label(text="", icon="FILE_3D")
                prop_with_search(row, props, "relating_type_id", text="")
            else:
                row.label(text="No Construction Type", icon="FILE_3D")
            if ifc_classes:
                row = layout.row()
                row.operator("bim.display_constr_types", icon="TRIA_DOWN", text="")

                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_A")
                op = row.operator("bim.add_constr_type_instance", text="Add")
                op.from_invoke = True
                op.ifc_class = ifc_class
                if relating_type_id.isnumeric():
                    op.relating_type_id = int(relating_type_id)
        else:
            row = layout.row(align=True)
            if ifc_classes:
                row.label(text="", icon="FILE_VOLUME")
                prop_with_search(row, props, "ifc_class", text="")
            else:
                row.label(text="No Construction Class", icon="FILE_VOLUME")
            row = layout.row(align=True)
            if relating_types_ids:
                row.label(text="", icon="FILE_3D")
                prop_with_search(row, props, "relating_type_id", text="")
            else:
                row.label(text="No Construction Type", icon="FILE_3D")
            if is_sidebar and ifc_classes and relating_types_ids:
                box = layout.box()
                box.template_icon(icon_value=props.icon_id, scale=8)

            if ifc_classes:
                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_A")
                op = row.operator("bim.add_constr_type_instance", text="Add")
                op.from_invoke = True
                op.ifc_class = ifc_class
                if relating_type_id.isnumeric():
                    op.relating_type_id = int(relating_type_id)

        if ifc_classes:
            if ifc_class == "IfcWallType":
                row = layout.row(align=True)
                row.prop(data=props, property="extrusion_depth", text="Height")
                op = row.operator("bim.change_extrusion_depth", icon="FILE_REFRESH", text="")
                op.depth = props.extrusion_depth

                row = layout.row(align=True)
                row.prop(data=props, property="length", text="Length")
                op = row.operator("bim.change_layer_length", icon="FILE_REFRESH", text="")
                op.length = props.length

                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_E")
                row.operator("bim.hotkey", text="Extend").hotkey = "S_E"
                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_T")
                row.operator("bim.hotkey", text="Butt").hotkey = "S_T"
                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_Y")
                row.operator("bim.hotkey", text="Mitre").hotkey = "S_Y"
                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_M")
                row.operator("bim.hotkey", text="Merge").hotkey = "S_M"
                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_F")
                row.operator("bim.hotkey", text="Flip").hotkey = "S_F"
                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_S")
                row.operator("bim.hotkey", text="Split").hotkey = "S_S"
                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_G")
                row.operator("bim.hotkey", text="Regen").hotkey = "S_G"
                row.operator("bim.join_wall", icon="X", text="").join_type = ""
            if ifc_class == "IfcSlabType":
                if not context.active_object:
                    pass
                elif context.active_object.mode == "OBJECT":
                    row = layout.row(align=True)
                    row.label(text="", icon="EVENT_SHIFT")
                    row.label(text="", icon="EVENT_E")
                    row.operator("bim.hotkey", text="Edit Profile").hotkey = "S_E"

            if ifc_class in ("IfcColumnType", "IfcBeamType", "IfcMemberType"):
                row = layout.row(align=True)
                row.prop(data=props, property="cardinal_point", text="Axis")
                op = row.operator("bim.change_cardinal_point", icon="FILE_REFRESH", text="")
                op.cardinal_point = int(props.cardinal_point)

                row = layout.row(align=True)
                label = "Height" if ifc_class == "IfcColumnType" else "Length"
                row.prop(data=props, property="extrusion_depth", text=label)
                op = row.operator("bim.change_profile_depth", icon="FILE_REFRESH", text="")
                op.depth = props.extrusion_depth

                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_E")
                row.operator("bim.hotkey", text="Extend").hotkey = "S_E"
                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_T")
                row.operator("bim.hotkey", text="Butt").hotkey = "S_T"
                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_Y")
                row.operator("bim.hotkey", text="Mitre").hotkey = "S_Y"
                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_R")
                row.operator("bim.hotkey", text="Rotate 90").hotkey = "S_R"
                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_G")
                row.operator("bim.hotkey", text="Regen").hotkey = "S_G"
                row.operator("bim.extend_profile", icon="X", text="").join_type = ""

            if ifc_class in ("IfcWindowType", "IfcDoorType"):
                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_G")
                row.operator("bim.hotkey", text="Regen").hotkey = "S_G"

            if props.ifc_class in (
                "IfcCableCarrierSegmentType",
                "IfcCableSegmentType",
                "IfcDuctSegmentType",
                "IfcPipeSegmentType",
            ):
                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="Extend", icon="EVENT_E")

        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="", icon="EVENT_O")
        if len(context.selected_objects) == 2:
            row.operator("bim.add_opening", text="Apply Void")
        else:
            row.operator("bim.add_potential_opening", text="Add Void")
        if AuthoringData.data["is_voidable_element"]:
            if AuthoringData.data["has_visible_openings"]:
                row.operator("bim.edit_openings", icon="CHECKMARK", text="")
                row.operator("bim.hide_openings", icon="CANCEL", text="")
            else:
                row.operator("bim.show_openings", icon="HIDE_OFF", text="")

        row = layout.row(align=True)
        row.label(text="Align")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="Align Exterior", icon="EVENT_X")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="Align Centerline", icon="EVENT_C")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="Align Interior", icon="EVENT_V")
        row = layout.row(align=True)

        row = layout.row(align=True)
        row.label(text="Mode")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_ALT")
        row.label(text="Opening", icon="EVENT_O")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_ALT")
        row.label(text="Decomposition", icon="EVENT_D")


class Hotkey(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.hotkey"
    bl_label = "Hotkey"
    bl_options = {"REGISTER", "UNDO"}
    hotkey: bpy.props.StringProperty()
    x: bpy.props.FloatProperty(name="X", default=0.5)
    y: bpy.props.FloatProperty(name="Y", default=0.5)
    z: bpy.props.FloatProperty(name="Z", default=0.5)

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def _execute(self, context):
        self.props = context.scene.BIMModelProperties
        self.has_ifc_class = True
        try:
            self.has_ifc_class = bool(self.props.ifc_class)
        except:
            pass
        getattr(self, f"hotkey_{self.hotkey}")()
        return {"FINISHED"}

    def invoke(self, context, event):
        # https://blender.stackexchange.com/questions/276035/how-do-i-make-operators-remember-their-property-values-when-called-from-a-hotkey
        self.props = context.scene.BIMModelProperties
        self.x = self.props.x
        self.y = self.props.y
        self.z = self.props.z
        return self.execute(context)

    def draw(self, context):
        props = context.scene.BIMModelProperties
        if self.hotkey == "S_O":
            row = self.layout.row()
            row.prop(self, "x")
            row = self.layout.row()
            row.prop(self, "y")
            row = self.layout.row()
            row.prop(self, "z")

    def hotkey_S_A(self):
        bpy.ops.bim.add_constr_type_instance()

    def hotkey_S_C(self):
        if self.has_ifc_class and self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.align_wall(align_type="CENTERLINE")
        else:
            bpy.ops.bim.align_product(align_type="CENTERLINE")

    def hotkey_S_E(self):
        if not self.has_ifc_class:
            return
        if self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.join_wall(join_type="T")
        elif self.props.ifc_class == "IfcSlabType":
            if not bpy.context.active_object:
                pass
            elif bpy.context.active_object.mode == "OBJECT":
                bpy.ops.bim.enable_editing_extrusion_profile()
        elif self.props.ifc_class in ["IfcColumnType", "IfcBeamType", "IfcMemberType"]:
            bpy.ops.bim.extend_profile(join_type="T")

    def hotkey_S_F(self):
        if self.has_ifc_class and self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.flip_wall()

    def hotkey_S_G(self):
        if self.has_ifc_class and self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.recalculate_wall()
        elif self.props.ifc_class in ["IfcColumnType", "IfcBeamType", "IfcMemberType"]:
            bpy.ops.bim.recalculate_profile()
        elif self.props.ifc_class in ["IfcWindowType", "IfcDoorType"]:
            bpy.ops.bim.recalculate_fill()

    def hotkey_S_M(self):
        if self.has_ifc_class and self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.merge_wall()

    def hotkey_S_R(self):
        if not self.has_ifc_class:
            return
        if self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.rotate_90(axis="Z")
        elif self.props.ifc_class == "IfcColumnType":
            bpy.ops.bim.rotate_90(axis="Z")
        elif self.props.ifc_class in ["IfcBeamType", "IfcMemberType"]:
            bpy.ops.bim.rotate_90(axis="Y")

    def hotkey_S_S(self):
        if self.has_ifc_class and self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.split_wall()

    def hotkey_S_T(self):
        if not self.has_ifc_class:
            return
        if self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.join_wall(join_type="L")
        elif self.props.ifc_class in ["IfcColumnType", "IfcBeamType", "IfcMemberType"]:
            bpy.ops.bim.extend_profile(join_type="L")

    def hotkey_S_V(self):
        if self.has_ifc_class and self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.align_wall(align_type="INTERIOR")
        else:
            bpy.ops.bim.align_product(align_type="POSITIVE")

    def hotkey_S_X(self):
        if self.has_ifc_class and self.props.ifc_class == "IfcWallType":
            if bpy.ops.bim.align_wall.poll():
                bpy.ops.bim.align_wall(align_type="EXTERIOR")
        else:
            bpy.ops.bim.align_product(align_type="NEGATIVE")

    def hotkey_S_Y(self):
        if self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.join_wall(join_type="V")
        elif self.props.ifc_class in ["IfcColumnType", "IfcBeamType", "IfcMemberType"]:
            bpy.ops.bim.extend_profile(join_type="V")

    def hotkey_S_O(self):
        if len(bpy.context.selected_objects) == 2:
            bpy.ops.bim.add_opening()
        else:
            bpy.ops.bim.add_potential_opening(x=self.x, y=self.y, z=self.z)
            self.props.x = self.x
            self.props.y = self.y
            self.props.z = self.z

    def hotkey_A_D(self):
        bpy.ops.bim.toggle_decomposition_parenting()

    def hotkey_A_O(self):
        if AuthoringData.data["has_visible_openings"]:
            bpy.ops.bim.hide_openings()
        else:
            bpy.ops.bim.show_openings()
