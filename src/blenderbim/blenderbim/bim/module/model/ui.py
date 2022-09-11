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

from bpy.types import Panel, Operator
from blenderbim.bim.module.model.data import AuthoringData
from blenderbim.bim.helper import prop_with_search, close_operator_panel


class BIM_PT_authoring(Panel):
    bl_label = "Architectural"
    bl_idname = "BIM_PT_authoring"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        row = self.layout.row(align=True)
        row.operator("bim.join_wall", icon="MOD_SKIN", text="T").join_type = "T"
        row.operator("bim.join_wall", icon="MOD_SKIN", text="L").join_type = "L"
        row.operator("bim.join_wall", icon="MOD_SKIN", text="V").join_type = "V"
        row.operator("bim.join_wall", icon="X", text="").join_type = ""
        row = self.layout.row(align=True)
        row.operator("bim.align_wall", icon="ANCHOR_TOP", text="Ext.").align_type = "EXTERIOR"
        row.operator("bim.align_wall", icon="ANCHOR_CENTER", text="C/L").align_type = "CENTERLINE"
        row.operator("bim.align_wall", icon="ANCHOR_BOTTOM", text="Int.").align_type = "INTERIOR"
        row = self.layout.row(align=True)
        row.operator("bim.flip_wall", icon="ORIENTATION_NORMAL", text="Flip")
        row.operator("bim.split_wall", icon="MOD_PHYSICS", text="Split")


class DisplayConstrTypesUI(Operator):
    bl_idname = "bim.display_constr_types_ui"
    bl_label = "Browse Construction Types"
    bl_options = {"REGISTER"}
    bl_description = "Display all available Construction Types to add new instances"

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=550)

    def draw(self, context):
        props = context.scene.BIMModelProperties
        if AuthoringData.data["ifc_classes"]:
            row = self.layout.row()
            row.label(text="", icon="FILE_VOLUME")
            prop_with_search(row, props, "ifc_class_browser", text="")
        ifc_class = props.ifc_class_browser
        num_cols = 3
        self.layout.row().separator(factor=0.25)
        flow = self.layout.grid_flow(row_major=True, columns=num_cols, even_columns=True, even_rows=True, align=True)
        relating_types = AuthoringData.relating_types_browser()
        num_types = len(relating_types)
        for idx, (relating_type_id, name, desc) in enumerate(relating_types):
            outer_col = flow.column()
            box = outer_col.box()
            row = box.row()
            row.label(text=name, icon="FILE_3D")
            row.alignment = "CENTER"
            row = box.row()
            preview_constr_types = AuthoringData.data["preview_constr_types"]
            if ifc_class in preview_constr_types:
                preview_ifc_class = preview_constr_types[ifc_class]
                if relating_type_id in preview_ifc_class:
                    icon_id = preview_ifc_class[relating_type_id]["icon_id"]
                    row.template_icon(icon_value=icon_id, scale=6.0)
            row = box.row()
            op = row.operator("bim.add_constr_type_instance", icon="ADD")
            op.from_invoke = True
            op.ifc_class = ifc_class
            if relating_type_id.isnumeric():
                op.relating_type_id = int(relating_type_id)
        last_row_cols = num_types % num_cols
        if last_row_cols != 0:
            for _ in range(num_cols - last_row_cols):
                flow.column()
        row = self.layout.row()
        row.alignment = "RIGHT"
        row.operator("bim.help_relating_types", text="", icon="QUESTION")


class HelpConstrTypes(Operator):
    bl_idname = "bim.help_relating_types"
    bl_label = "Construction Types Help"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Click to read some contextual help"

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=510)

    def draw(self, context):
        layout = self.layout
        layout.row().separator(factor=0.5)
        row = layout.row()
        row.alignment = "CENTER"
        row.label(text="BlenderBIM Help", icon="BLENDER")
        layout.row().separator(factor=0.5)

        row = layout.row().row()
        row.label(text="Overview:", icon="KEYTYPE_MOVING_HOLD_VEC")
        self.draw_lines(layout, self.message_summary)
        layout.row().separator()

        row = layout.row().row()
        row.label(text="Further support:", icon="KEYTYPE_MOVING_HOLD_VEC")
        layout.row().separator(factor=0.5)
        row = layout.row()
        op = row.operator("bim.open_upstream", text="Homepage", icon="HOME")
        op.page = "home"
        op = row.operator("bim.open_upstream", text="Docs", icon="DOCUMENTS")
        op.page = "docs"
        op = row.operator("bim.open_upstream", text="Wiki", icon="CURRENT_FILE")
        op.page = "wiki"
        op = row.operator("bim.open_upstream", text="Community", icon="COMMUNITY")
        op.page = "community"
        layout.row().separator()

    def draw_lines(self, layout, lines):
        box = layout.box()
        for line in lines:
            row = box.row()
            row.label(text=f"  {line}")

    @property
    def message_summary(self):
        return [
            "The Construction Type Browser allows to preview and add new instances to the model.",
            "For further support, please click on the Documentation link below.",
        ]
