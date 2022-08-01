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

import math
from bpy.types import Panel, Operator
from blenderbim.bim.module.model.data import AuthoringData
from blenderbim.bim.helper import prop_with_search, layout_with_margins, close_operator_panel


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
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        props = context.scene.BIMModelProperties
        header_data = self.draw_header(props)
        if props.unfold_relating_types:
            self.draw_by_ifc_class(props, header_data)
        else:
            self.draw_by_ifc_class_and_type(props, header_data)

    def draw_header(self, props):
        layout = self.layout
        inner_layout = layout
        inner_layout.row().separator(factor=0.75)
        split = inner_layout.split(align=True, factor=2.0 / 3)
        col1 = split.column(align=True)
        row = col1.row()
        row.prop(data=props, property="unfold_relating_types", text="Preview All Construction Types")
        col1.row().separator(factor=1)
        row = col1.row()
        row.label(text="Select Construction Type:")
        col1.row().separator(factor=1.5)
        enabled = True
        if AuthoringData.data["ifc_classes"]:
            row = col1.row()
            row.label(text="", icon="FILE_VOLUME")
            prop_with_search(row, props, "ifc_class", text="")
            col1.row().separator()
        else:
            enabled = False
        col2 = split.column(align=True)
        subsplit = col2.split(factor=0.8)
        subcol = [subsplit.column() for _ in range(2)][-1]
        subcol.operator("bim.help_relating_types", text="", icon="QUESTION")
        col2.row().separator(factor=1)
        return {"enabled": enabled, "layout": inner_layout, "col1": col1, "col2": col2}

    def draw_by_ifc_class(self, props, header_data):
        enabled, layout = [header_data[key] for key in ["enabled", "layout"]]
        ifc_class = props.ifc_class
        num_cols = 3
        layout.row().separator(factor=0.25)
        flow = layout.grid_flow(row_major=True, columns=num_cols, even_columns=True, even_rows=True, align=True)
        relating_types = AuthoringData.relating_types()
        num_types = len(relating_types)
        for idx, (relating_type_id, name, desc) in enumerate(relating_types):
            outer_col = flow.column()
            box = outer_col.box()
            row = box.row()
            row.label(text=name, icon="FILE_3D")
            row.alignment = "CENTER"
            row = box.row()
            if enabled:
                preview_constr_types = AuthoringData.data["preview_constr_types"]
                if ifc_class in preview_constr_types:
                    preview_ifc_class = preview_constr_types[ifc_class]
                    if relating_type_id in preview_ifc_class:
                        icon_id = preview_ifc_class[relating_type_id]["icon_id"]
                        row.template_icon(icon_value=icon_id, scale=6.0)
            box.row().separator(factor=0.2)
            row = box.row()
            op = row.operator("bim.add_constr_type_instance", icon="ADD")
            op.from_invoke = True
            op.ifc_class = ifc_class
            if relating_type_id.isnumeric():
                op.relating_type_id = int(relating_type_id)
            factor = 2 if idx + 1 < math.ceil(num_types / num_cols) else 1.5
            outer_col.row().separator(factor=factor)
        last_row_cols = num_types % num_cols
        if last_row_cols != 0:
            for _ in range(num_cols - last_row_cols):
                flow.column()

    def draw_by_ifc_class_and_type(self, props, header_data):
        enabled, col1, col2 = [header_data[key] for key in ["enabled", "col1", "col2"]]
        ifc_class = props.ifc_class
        relating_type_id = props.relating_type_id
        if AuthoringData.data["relating_types_ids"]:
            row = col1.row()
            row.label(text="", icon="FILE_3D")
            prop_with_search(row, props, "relating_type_id", text="")
            col1.row().separator()
        else:
            enabled = False
        col1.row().separator(factor=4.75)
        row = col1.row()
        row.enabled = enabled
        row.label(text="", icon="BLANK1")
        op = row.operator("bim.add_constr_type_instance", icon="ADD")
        op.from_invoke = True
        op.ifc_class = ifc_class
        if relating_type_id.isnumeric():
            op.relating_type_id = int(relating_type_id)
        col2.row().separator(factor=1.25)
        split = col2.split(factor=0.025)
        col = [split.column() for _ in range(2)][-1]
        box = col.box()
        if enabled:
            box.template_icon(icon_value=props.icon_id, scale=5.6)
        col1.row().separator(factor=1)


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

        row = layout_with_margins(layout.row()).row()
        row.label(text="Overview:", icon="KEYTYPE_MOVING_HOLD_VEC")
        self.draw_lines(layout, self.message_summary)
        layout.row().separator()

        row = layout_with_margins(layout.row()).row()
        row.label(text="Further support:", icon="KEYTYPE_MOVING_HOLD_VEC")
        layout.row().separator(factor=0.5)
        row = layout_with_margins(layout).row()
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
        box = layout_with_margins(layout).box()
        for line in lines:
            row = box.row()
            row.label(text=f"  {line}")

    @property
    def message_summary(self):
        return [
            "The Construction Type Browser allows to preview and add new instances to the model.",
            "For further support, please click on the Documentation link below.",
        ]
