# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import bpy
import bonsai.tool as tool
import bonsai.bim.module.type.prop as type_prop
import ifcopenshell.util.unit
from bpy.types import WorkSpaceTool
from bonsai.bim.module.model.data import AuthoringData, RailingData, RoofData


class CadTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "EDIT_MESH"

    bl_idname = "bim.cad_tool"
    bl_label = "CAD Tool"
    bl_description = "Gives you CAD authoring related superpowers"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.cad")
    bl_widget = None
    bl_keymap = tool.Blender.get_default_selection_keypmap() + (
        ("bim.cad_hotkey", {"type": "C", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_C")]}),
        ("bim.cad_hotkey", {"type": "E", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_E")]}),
        ("bim.cad_hotkey", {"type": "F", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_F")]}),
        ("bim.cad_hotkey", {"type": "O", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_O")]}),
        ("bim.cad_hotkey", {"type": "Q", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_Q")]}),
        ("bim.cad_hotkey", {"type": "R", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_R")]}),
        ("bim.cad_hotkey", {"type": "T", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_T")]}),
        ("bim.cad_hotkey", {"type": "V", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_V")]}),
        ("bim.cad_hotkey", {"type": "X", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_X")]}),
    )

    def draw_settings(context, layout, workspace_tool):
        obj = context.active_object
        if not obj or not obj.data:
            return
        if hasattr(obj.data, "BIMMeshProperties") and obj.data.BIMMeshProperties.subshape_type == "PROFILE":
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_Q")
            element = tool.Ifc.get_entity(obj)
            if element:
                if element.is_a("IfcProfileDef"):
                    row.operator("bim.edit_arbitrary_profile", text="Save Profile")
                    row.operator("bim.align_view_to_profile", text="", icon="AXIS_FRONT")
                    row.operator("bim.disable_editing_arbitrary_profile", text="", icon="CANCEL")
                elif element.is_a("IfcRelSpaceBoundary"):
                    row.operator("bim.edit_boundary_geometry", text="Save Profile")
                    row.operator("bim.disable_editing_boundary_geometry", text="", icon="CANCEL")
                else:
                    row.operator("bim.edit_extrusion_profile", text="Save Profile")
                    row.operator("bim.align_view_to_profile", text="", icon="AXIS_FRONT")
                    row.operator("bim.disable_editing_extrusion_profile", text="", icon="CANCEL")

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_E")
            row.operator("bim.cad_hotkey", text="Extend").hotkey = "S_E"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_T")
            row.operator("bim.cad_hotkey", text="Mitre").hotkey = "S_T"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_F")
            row.operator("bim.cad_hotkey", text="Fillet").hotkey = "S_F"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_O")
            row.operator("bim.cad_hotkey", text="Offset").hotkey = "S_O"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_R")
            row.operator("bim.add_rectangle", text="Rectangle")

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_C")
            row.operator("bim.add_ifccircle", text="Circle")

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_V")
            row.operator("bim.set_arc_index", text="3-Point Arc")

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_X")
            row.operator("bim.reset_vertex", text="Reset Vertex")

        elif hasattr(obj.data, "BIMMeshProperties") and obj.data.BIMMeshProperties.subshape_type == "AXIS":
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_Q")
            row.operator("bim.edit_extrusion_axis", text="Save Axis")
            row.operator("bim.disable_editing_extrusion_axis", text="", icon="CANCEL")

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_E")
            row.operator("bim.cad_hotkey", text="Extend").hotkey = "S_E"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_T")
            row.operator("bim.cad_hotkey", text="Mitre").hotkey = "S_T"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_F")
            row.operator("bim.cad_hotkey", text="Fillet").hotkey = "S_F"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_O")
            row.operator("bim.cad_hotkey", text="Offset").hotkey = "S_O"

        else:
            if (
                (RailingData.is_loaded or not RailingData.load())
                and RailingData.data["pset_data"]
                and context.active_object.BIMRailingProperties.is_editing_path
            ):
                row = layout.row(align=True)
                row.label(text="", icon=f"EVENT_TAB")
                row.operator("bim.finish_editing_railing_path")
                row.operator("bim.cancel_editing_railing_path", icon="CANCEL", text="")

            elif (
                (RoofData.is_loaded or not RoofData.load())
                and RoofData.data["pset_data"]
                and context.active_object.BIMRoofProperties.is_editing_path
            ):
                row = layout.row(align=True)
                row.label(text="", icon=f"EVENT_TAB")
                row.operator("bim.finish_editing_roof_path")
                row.operator("bim.cancel_editing_roof_path", icon="CANCEL", text="")

                row = layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_R")
                row.operator("bim.cad_hotkey", text="Set Gable Roof Angle").hotkey = "S_R"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_E")
            row.operator("bim.cad_hotkey", text="Extend").hotkey = "S_E"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_T")
            row.operator("bim.cad_hotkey", text="Mitre").hotkey = "S_T"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_F")
            row.operator("bim.cad_hotkey", text="Fillet").hotkey = "S_F"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_O")
            row.operator("bim.cad_hotkey", text="Offset").hotkey = "S_O"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="2-Point Arc", icon="EVENT_C")

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_V")
            row.operator("bim.cad_hotkey", text="3-Point Arc").hotkey = "S_V"


class CadHotkey(bpy.types.Operator):
    bl_idname = "bim.cad_hotkey"
    bl_label = "CAD Hotkey"
    bl_options = {"REGISTER", "UNDO"}
    hotkey: bpy.props.StringProperty()

    def execute(self, context):
        self.props = context.scene.BIMCadProperties
        getattr(self, f"hotkey_{self.hotkey}")()
        return {"FINISHED"}

    def draw(self, context):
        props = context.scene.BIMCadProperties
        if self.hotkey == "S_C":
            if self.is_profile():
                row = self.layout.row()
                row.prop(props, "radius")

        elif self.hotkey == "S_F":
            if not self.is_profile():
                row = self.layout.row()
                row.prop(props, "resolution")
            row = self.layout.row()
            row.prop(props, "radius")

        elif self.hotkey == "S_O":
            row = self.layout.row()
            row.prop(props, "distance")

        elif self.hotkey == "S_R":
            if self.is_profile():
                row = self.layout.row()
                row.prop(props, "x")
                row = self.layout.row()
                row.prop(props, "y")
            elif (
                (RoofData.is_loaded or not RoofData.load())
                and RoofData.data["pset_data"]
                and bpy.context.active_object.BIMRoofProperties.is_editing_path
            ):
                self.layout.row().prop(props, "gable_roof_edge_angle")
                self.layout.row().prop(props, "gable_roof_separate_verts")

        elif self.hotkey == "S_V":
            if not self.is_profile():
                row = self.layout.row()
                row.prop(props, "resolution")

    def hotkey_S_C(self):
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        if self.is_profile():
            bpy.ops.bim.add_ifccircle(radius=self.props.radius / si_conversion)
        else:
            bpy.ops.bim.cad_arc_from_2_points()

    def hotkey_S_E(self):
        bpy.ops.bim.cad_trim_extend()

    def hotkey_S_F(self):
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        if self.is_profile():
            bpy.ops.bim.add_ifcarcindex_fillet(radius=self.props.radius / si_conversion)
        else:
            bpy.ops.bim.cad_fillet(resolution=self.props.resolution, radius=self.props.radius / si_conversion)

    def hotkey_S_O(self):
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        bpy.ops.bim.cad_offset(distance=self.props.distance / si_conversion)

    def hotkey_S_Q(self):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if bpy.context.active_object.data.BIMMeshProperties.subshape_type == "PROFILE":
            if element.is_a("IfcProfileDef"):
                bpy.ops.bim.edit_arbitrary_profile()
            elif element.is_a("IfcRelSpaceBoundary"):
                bpy.ops.bim.edit_boundary_geometry()
            else:
                bpy.ops.bim.edit_extrusion_profile()
        elif bpy.context.active_object.data.BIMMeshProperties.subshape_type == "AXIS":
            bpy.ops.bim.edit_extrusion_axis()

    def hotkey_S_R(self):
        if self.is_profile():
            si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            bpy.ops.bim.add_rectangle(x=self.props.x / si_conversion, y=self.props.y / si_conversion)
        elif (
            (RoofData.is_loaded or not RoofData.load())
            and RoofData.data["pset_data"]
            and bpy.context.active_object.BIMRoofProperties.is_editing_path
        ):
            bpy.ops.bim.set_gable_roof_edge_angle(
                angle=self.props.gable_roof_edge_angle, separate_verts=self.props.gable_roof_separate_verts
            )

    def hotkey_S_T(self):
        bpy.ops.bim.cad_mitre()

    def hotkey_S_V(self):
        if self.is_profile():
            bpy.ops.bim.set_arc_index()
        else:
            bpy.ops.bim.cad_arc_from_3_points(resolution=self.props.resolution)

    def hotkey_S_X(self):
        if self.is_profile():
            bpy.ops.bim.reset_vertex()

    def is_profile(self):
        obj = bpy.context.active_object
        return (
            obj
            and obj.data
            and hasattr(obj.data, "BIMMeshProperties")
            and obj.data.BIMMeshProperties.subshape_type == "PROFILE"
        )
