# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
import bl_ui_utils
import bonsai.bim
import bonsai.tool as tool
from bpy.types import Panel, Menu
from bonsai.bim.helper import prop_with_search
from bonsai.bim.module.model.data import (
    AuthoringData,
    ArrayData,
    StairData,
    SverchokData,
    WindowData,
    DoorData,
    RailingData,
    RoofData,
)
from bonsai.bim.module.model.stair import regenerate_stair_mesh
from bonsai.bim.module.model.railing import update_railing_modifier_bmesh
from bonsai.bim.module.model.roof import update_roof_modifier_bmesh
from collections.abc import Iterable


class BIM_MT_type_manager_menu(bpy.types.Menu):
    bl_label = "Type Manager Menu"
    bl_idname = "BIM_MT_type_manager_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("bim.purge_unused_objects", text="Purge Unused Types", icon="TRASH").object_type = "TYPE"


class BIM_MT_type_menu(bpy.types.Menu):
    bl_label = "Type Menu"
    bl_idname = "BIM_MT_type_menu"
    relating_type_id: bpy.props.IntProperty(name="Relating Type Id")

    def draw(self, context):
        props = tool.Model.get_model_props()
        layout = self.layout
        with bl_ui_utils.layout.operator_context(layout, "INVOKE_REGION_WIN"):
            op = layout.operator("bim.rename_type", icon="GREASEPENCIL", text="Rename Type")
            op.element = props.menu_relating_type_id
        op = layout.operator("bim.select_type", icon="OBJECT_DATA")
        op.relating_type = props.menu_relating_type_id
        op = layout.operator("bim.duplicate_type", icon="DUPLICATE")
        op.element = props.menu_relating_type_id
        layout.separator()
        op = layout.operator("bim.remove_type", icon="X")
        op.element = props.menu_relating_type_id


class LaunchTypeMenu(bpy.types.Operator):
    bl_idname = "bim.launch_type_menu"
    bl_label = "Launch Type Menu"
    relating_type_id: bpy.props.IntProperty(name="Relating Type Id")

    def execute(self, context):
        props = tool.Model.get_model_props()
        props.menu_relating_type_id = self.relating_type_id
        bpy.ops.wm.call_menu(name="BIM_MT_type_menu")
        return {"FINISHED"}


class LaunchTypeManager(bpy.types.Operator):
    bl_idname = "bim.launch_type_manager"
    bl_label = "Launch Type Manager"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Browse, Edit and Manage Types"

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        props = tool.Model.get_model_props()
        props.type_page = 1
        bpy.ops.bim.load_type_thumbnails()
        return context.window_manager.invoke_props_dialog(self, width=550, title="Type Manager", confirm_text="Close")

    def draw(self, context):
        props = tool.Model.get_model_props()
        row = self.layout.row(align=True)
        text = f"{AuthoringData.data['total_types']} {AuthoringData.data['ifc_element_type'] or 'Types'}"
        if AuthoringData.data["ifc_element_type"] and AuthoringData.data["total_types"] > 1:
            text += "s"
        row.label(text=text, icon="FILE_VOLUME")
        row.menu("BIM_MT_type_manager_menu", text="", icon="PREFERENCES")

        row = self.layout.row(align=True)
        op = row.operator(
            "bim.add_element", text=f"Create New {AuthoringData.data['ifc_element_type'] or 'Type'}", icon="ADD"
        )
        op.is_specific_tool = bool(AuthoringData.data["ifc_element_type"])
        op.ifc_product = "IfcElementType"
        op.ifc_class = AuthoringData.data["ifc_element_type"] or props.ifc_class or ""

        row = self.layout.row(align=True)
        row.prop(props, "search_name", icon="FILTER", text="")

        columns = self.layout.column_flow(columns=3)
        if AuthoringData.data["total_pages"] > 0:
            row = columns.row(align=True)
            row.alignment = "RIGHT"
            row2 = row.row(align=True)
            row2.label(text="Page")
            row2.prop(props, "type_page", text="", emboss=False)
            row2.label(text=f"/{AuthoringData.data['total_pages']} ")

            prev_page_op = row.row(align=True)
            op = prev_page_op.operator("bim.change_type_page", icon="TRIA_LEFT", text="")
            op.page = AuthoringData.data["prev_page"] or 0
            prev_page_op.enabled = op.page > 0

            next_page_op = row.row(align=True)
            op = next_page_op.operator("bim.change_type_page", icon="TRIA_RIGHT", text="")
            op.page = AuthoringData.data["next_page"] or 0
            next_page_op.enabled = op.page > 0

        flow = self.layout.grid_flow(row_major=True, columns=3, even_columns=True, even_rows=True, align=True)

        for relating_type in AuthoringData.data["paginated_relating_types"]:
            outer_col = flow.column()
            box = outer_col.box()

            row = box.row()
            op = row.operator("bim.set_active_type", text=relating_type["name"], icon="BLANK1", emboss=False)
            op.relating_type = relating_type["id"]

            op = row.operator("bim.launch_type_menu", icon="PREFERENCES", text="", emboss=True)
            op.relating_type_id = relating_type["id"]

            row = box.row()
            row.alignment = "CENTER"
            op = row.operator("bim.set_active_type", text=relating_type["description"], emboss=False)
            op.relating_type = relating_type["id"]

            if icon_id := AuthoringData.type_thumbnails.get(relating_type["id"], 0):
                # Yep, that's EXACTLY how it's done. And I'm proud of it.
                row1 = box.row()
                row1.ui_units_y = 0.01
                row1.template_icon(icon_value=icon_id, scale=4)
                row2 = box.column(align=True)
                row2.operator("bim.set_active_type", text="", emboss=False).relating_type = relating_type["id"]
                row2.operator("bim.set_active_type", text="", emboss=False).relating_type = relating_type["id"]
                row2.operator("bim.set_active_type", text="", emboss=False).relating_type = relating_type["id"]
                is_current_relating_type = relating_type["id"] == AuthoringData.data["relating_type_data"].get("id")
                if is_current_relating_type:
                    active_row = row2.row()
                    active_row.alignment = "CENTER"
                    active_row.label(text="Active", icon="CHECKMARK")
                else:
                    row2.operator("bim.set_active_type", text="", emboss=False).relating_type = relating_type["id"]
            else:
                row = box.row()
                box.operator("bim.load_type_thumbnails", text="", icon="FILE_REFRESH")

            row = box.row()
            row.alignment = "CENTER"
            op = row.operator("bim.set_active_type", text=relating_type["predefined_type"], emboss=False)
            op.relating_type = relating_type["id"]


class BIM_PT_authoring(Panel):
    bl_label = "Architectural"
    bl_idname = "BIM_PT_authoring"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Bonsai"

    def draw(self, context):
        row = self.layout.row(align=True)
        row.operator("bim.generate_space")
        row = self.layout.row(align=True)
        row.operator("bim.generate_spaces_from_walls")
        row = self.layout.row(align=True)
        row.operator("bim.toggle_space_visibility")


class BIM_PT_array(bpy.types.Panel):
    bl_label = "Array"
    bl_idname = "BIM_PT_array"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_parametric_geometry"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and tool.Ifc.get_entity(context.active_object)

    def draw(self, context):
        if not ArrayData.is_loaded:
            ArrayData.load()

        obj = context.active_object
        assert obj
        props = tool.Model.get_array_props(obj)

        if ArrayData.data["parameters"]:
            row = self.layout.row(align=True)
            row.label(text=ArrayData.data["parameters"]["parent_name"], icon="CON_CHILDOF")
            row.operator("bim.select_array_parent", icon="OBJECT_DATA", text="")
            row.operator("bim.select_all_array_objects", icon="RESTRICT_SELECT_OFF", text="")

            if ArrayData.data["parameters"]["data_dict"]:
                row.operator("bim.add_array", icon="ADD", text="")

            for i, array in enumerate(ArrayData.data["parameters"]["data_dict"]):
                box = self.layout.box()
                if props.is_editing == i:
                    row = box.row(align=True)
                    row.prop(props, "count", icon="MOD_ARRAY")
                    row.operator("bim.edit_array", icon="CHECKMARK", text="").item = i
                    row.operator("bim.disable_editing_array", icon="CANCEL", text="")
                    row = box.row(align=True)
                    row.prop(props, "method")
                    row = box.row(align=True)
                    row.prop(props, "use_local_space")
                    row.prop(props, "sync_children")
                    col = box.column()
                    row = col.row(align=True)
                    row.prop(props, "x")
                    row.operator("bim.input_cursor_x_array", icon="CURSOR", text="")
                    row = col.row(align=True)
                    row.prop(props, "y")
                    row.operator("bim.input_cursor_y_array", icon="CURSOR", text="")
                    row = col.row(align=True)
                    row.prop(props, "z")
                    row.operator("bim.input_cursor_z_array", icon="CURSOR", text="")
                    row = col.row(align=True)
                    row.prop(props, "relating_array_object", icon="COPYDOWN")
                else:
                    row = box.row(align=True)
                    name = f"{array['count']} Items ({array.get('method', 'OFFSET').capitalize()})"
                    row.label(text=name, icon="MOD_ARRAY")
                    row.operator("bim.enable_editing_array", icon="GREASEPENCIL", text="").item = i
                    apply_button = row.row(align=True)
                    apply_button.operator("bim.apply_array", text="", icon="CHECKMARK")
                    apply_button.enabled = i == len(ArrayData.data["parameters"]["data_dict"]) - 1
                    row.operator("bim.remove_array", icon="X", text="").item = i
                    row = box.row(align=True)
                    icon = "EMPTY_ARROWS" if array.get("use_local_space", False) else "EMPTY_AXIS"
                    row.label(text=f"X: {array['x']}", icon=icon)
                    row.label(text=f"Y: {array['y']}")
                    row.label(text=f"Z: {array['z']}")
        else:
            row = self.layout.row()
            row.label(text="No Array Found")
            row.operator("bim.add_array", icon="ADD", text="")


class BIM_PT_stair(bpy.types.Panel):
    bl_label = "Stair"
    bl_idname = "BIM_PT_stair"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_parametric_geometry"

    @classmethod
    def poll(cls, context):
        return tool.Blender.Modifier.is_eligible_for_stair_modifier(context.active_object)

    def draw(self, context):
        if not StairData.is_loaded:
            StairData.load()

        obj = context.active_object
        assert obj
        props = tool.Model.get_stair_props(obj)

        if StairData.data["pset_data"]:
            row = self.layout.row(align=True)
            row.label(text="Stair parameters", icon="IPO_CONSTANT")

            if props.is_editing:
                calculated_params = tool.Model.get_active_stair_calculated_params()
                row = self.layout.row(align=True)
                row.operator("bim.finish_editing_stair", icon="CHECKMARK", text="Finish Editing")
                row.operator("bim.cancel_editing_stair", icon="CANCEL", text="")
                row = self.layout.row(align=True)
                for prop_name in props.get_props_kwargs():
                    prop_value = getattr(props, prop_name)
                    if isinstance(prop_value, Iterable) and not isinstance(prop_value, str):
                        prop_readable_name = props.bl_rna.properties[prop_name].name
                        self.layout.label(text=f"{prop_readable_name}:")
                        self.layout.prop(props, prop_name, text="")
                    else:
                        self.layout.prop(props, prop_name)
                    if prop_name == "height":  # Weak but we just want to insert this inside props drawing
                        row_length = self.layout.row(align=True)
                        row_length.prop(props, "total_length_target")
                        row_length.prop(
                            props,
                            "total_length_lock",
                            text="",
                            icon="LOCKED" if props.total_length_lock else "UNLOCKED",
                        )
                regenerate_stair_mesh(obj)
            else:
                calculated_params = StairData.data["calculated_params"]
                row.operator("bim.enable_editing_stair", icon="GREASEPENCIL", text="")
                row.operator("bim.remove_stair", icon="X", text="")
                row = self.layout.row(align=True)
                for prop_name, prop_value in StairData.data["general_params"].items():
                    row = self.layout.row(align=True)
                    if isinstance(prop_value, Iterable) and not isinstance(prop_value, str):
                        row.label(text=f"{prop_name}:")
                        row = self.layout.row(align=True)
                        for prop_value_item in prop_value:
                            row.label(text=str(prop_value_item))
                    else:
                        row.label(text=prop_name)
                        row.label(text=str(prop_value))

            # calculated properties
            for prop_name, prop_value in calculated_params.items():
                row = self.layout.row(align=True)
                row.label(text=prop_name)
                row.label(text=str(prop_value))
        else:
            row = self.layout.row()
            row.label(text="No Stair Found")
            row.operator("bim.add_stair", icon="ADD", text="")


class BIM_PT_sverchok(bpy.types.Panel):
    bl_label = "Sverchok"
    bl_idname = "BIM_PT_sverchok"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_parametric_geometry"

    @classmethod
    def poll(cls, context):
        # always display modifier if it's IFC object
        return tool.Ifc.get() and tool.Ifc.get_entity(context.active_object)

    def draw(self, context):
        if not SverchokData.is_loaded:
            SverchokData.load()

        if not SverchokData.data["has_sverchok"]:
            self.layout.label(text="Requires Sverchok Add-on", icon="ERROR")
            return

        props = context.active_object.BIMSverchokProperties
        self.layout.prop_search(props, "node_group", bpy.data, "node_groups")
        self.layout.operator("bim.create_new_sverchok_graph", icon="ADD")

        self.layout.operator("bim.update_data_from_sverchok", icon="FILE_REFRESH")

        row = self.layout.row()
        row.operator("bim.delete_sverchok_graph", icon="X")
        row.enabled = bool(props.node_group)

        self.layout.operator("bim.import_sverchok_graph", text="Import JSON", icon="RNA")

        row = self.layout.row()
        row.operator("bim.export_sverchok_graph", text="Export to JSON", icon="FILE_BACKUP")
        row.enabled = bool(props.node_group)


class BIM_PT_window(bpy.types.Panel):
    bl_label = "Window"
    bl_idname = "BIM_PT_window"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_parametric_geometry"

    @classmethod
    def poll(cls, context):
        return tool.Blender.Modifier.is_eligible_for_window_modifier(context.active_object)

    def draw(self, context):
        if not WindowData.is_loaded:
            WindowData.load()

        obj = context.active_object
        assert obj
        props = tool.Model.get_window_props(obj)

        if WindowData.data["pset_data"]:
            row = self.layout.row(align=True)
            row.label(text="Window parameters", icon="OUTLINER_OB_LATTICE")

            if props.is_editing:
                number_of_panels, panels_data = props.window_types_panels[props.window_type]
                row = self.layout.row(align=True)
                row.operator("bim.finish_editing_window", icon="CHECKMARK", text="Finish Editing")
                row.operator("bim.cancel_editing_window", icon="CANCEL", text="")

                general_props = props.get_general_kwargs()
                for prop in general_props:
                    self.layout.prop(props, prop)

                lining_props = props.get_lining_kwargs()
                self.layout.label(text="Lining properties")
                for prop in lining_props:
                    self.layout.prop(props, prop)

                panel_props = props.get_panel_kwargs()
                self.layout.label(text="Panel properties")

                panel_box = self.layout.box()
                row = panel_box.row()
                cols = [row.column(align=True) for i in range(number_of_panels + 1)]

                cols[0].label(text="")

                for panel_i in range(number_of_panels):
                    r = cols[panel_i + 1].row()
                    r.alignment = "CENTER"
                    r.label(text=f"#{panel_i}")
                    r = cols[panel_i + 1].row()

                for prop in panel_props:
                    cols[0].label(text=f"{props.bl_rna.properties[prop].name}")
                    for panel_i in range(number_of_panels):
                        cols[panel_i + 1].prop(props, prop, index=panel_i, text="")

                self.layout.use_property_split = True
                self.layout.label(text="Material Properties")
                row = prop_with_search(self.layout, props, "lining_material")
                tool.Model.draw_material_ui_select(row, props.lining_material)
                row = prop_with_search(self.layout, props, "framing_material", text="Panel Material")
                tool.Model.draw_material_ui_select(row, props.framing_material)
                row = prop_with_search(self.layout, props, "glazing_material")
                tool.Model.draw_material_ui_select(row, props.glazing_material)
            else:
                row.operator("bim.enable_editing_window", icon="GREASEPENCIL", text="")
                row.operator("bim.remove_window", icon="X", text="")

                box = self.layout.box()
                general_params = WindowData.data["general_params"]
                window_type_prop = props.bl_rna.properties["window_type"].name
                number_of_panels, panels_data = props.window_types_panels[general_params[window_type_prop]]
                for prop_name, prop_value in general_params.items():
                    row = box.row(align=True)
                    row.label(text=prop_name)
                    row.label(text=str(prop_value))

                self.layout.label(text="Lining properties")
                box = self.layout.box()
                for prop_name, prop_value in WindowData.data["lining_params"].items():
                    row = box.row(align=True)
                    row.label(text=prop_name)
                    row.label(text=str(prop_value))

                panel_props = WindowData.data["panel_params"]
                self.layout.label(text="Panel properties")

                panel_box = self.layout.box()
                row = panel_box.row()
                cols = [row.column(align=True) for i in range(number_of_panels + 1)]
                cols[0].label(text="")

                for panel_i in range(number_of_panels):
                    r = cols[panel_i + 1].row()
                    r.alignment = "CENTER"
                    r.label(text=f"#{panel_i}")
                    r = cols[panel_i + 1].row()

                for prop_name in panel_props:
                    cols[0].row().label(text=prop_name)
                    for panel_i in range(number_of_panels):
                        r = cols[panel_i + 1].row()
                        r.alignment = "CENTER"
                        prop_value = panel_props[prop_name][panel_i]
                        r.label(text=str(prop_value))
                        r = cols[panel_i + 1].row()
        else:
            row = self.layout.row()
            row.label(text="No Window Found")
            row.operator("bim.add_window", icon="ADD", text="")


class BIM_PT_door(bpy.types.Panel):
    bl_label = "Door"
    bl_idname = "BIM_PT_door"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_parametric_geometry"

    @classmethod
    def poll(cls, context):
        return tool.Blender.Modifier.is_eligible_for_door_modifier(context.active_object)

    def draw(self, context):
        if not DoorData.is_loaded:
            DoorData.load()

        obj = context.active_object
        assert obj
        props = tool.Model.get_door_props(obj)

        if DoorData.data["pset_data"]:
            row = self.layout.row(align=True)
            row.label(text="Door parameters", icon="OUTLINER_OB_LATTICE")

            if props.is_editing:
                row = self.layout.row(align=True)
                row.operator("bim.finish_editing_door", icon="CHECKMARK", text="Finish Editing")
                row.operator("bim.cancel_editing_door", icon="CANCEL", text="")

                general_props = props.get_general_kwargs()
                for prop in general_props:
                    self.layout.prop(props, prop)

                lining_props = props.get_lining_kwargs()
                self.layout.label(text="Lining Properties")
                for prop in lining_props:
                    self.layout.prop(props, prop)

                panel_props = props.get_panel_kwargs()
                self.layout.label(text="Panel Properties")
                for prop in panel_props:
                    self.layout.prop(props, prop)

                self.layout.use_property_split = True
                self.layout.label(text="Material Properties")

                row = prop_with_search(self.layout, props, "lining_material")
                tool.Model.draw_material_ui_select(row, props.lining_material)
                row = prop_with_search(self.layout, props, "framing_material", text="Panel Material")
                tool.Model.draw_material_ui_select(row, props.framing_material)
                if props.transom_thickness:
                    row = prop_with_search(self.layout, props, "glazing_material")
                    tool.Model.draw_material_ui_select(row, props.framing_material)
            else:
                row.operator("bim.enable_editing_door", icon="GREASEPENCIL", text="")
                row.operator("bim.remove_door", icon="X", text="")

                box = self.layout.box()
                for prop_name, prop_value in DoorData.data["general_params"].items():
                    row = box.row(align=True)
                    row.label(text=prop_name)
                    row.label(text=str(prop_value))

                self.layout.label(text="Lining properties")
                lining_box = self.layout.box()
                for prop_name, prop_value in DoorData.data["lining_params"].items():
                    row = lining_box.row(align=True)
                    row.label(text=prop_name)
                    row.label(text=str(prop_value))

                self.layout.label(text="Panel properties")
                panel_box = self.layout.box()
                for prop_name, prop_value in DoorData.data["panel_params"].items():
                    row = panel_box.row(align=True)
                    row.label(text=prop_name)
                    row.label(text=str(prop_value))
        else:
            row = self.layout.row()
            row.label(text="No Door Found")
            row.operator("bim.add_door", icon="ADD", text="")


class BIM_PT_railing(bpy.types.Panel):
    bl_label = "Railing"
    bl_idname = "BIM_PT_railing"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_parametric_geometry"

    @classmethod
    def poll(cls, context):
        return tool.Blender.Modifier.is_eligible_for_railing_modifier(context.active_object)

    def draw(self, context):
        if not RailingData.is_loaded:
            RailingData.load()

        obj = context.active_object
        assert obj
        props = tool.Model.get_railing_props(obj)

        if RailingData.data["pset_data"]:
            row = self.layout.row(align=True)
            row.label(text="Railing parameters", icon="OUTLINER_OB_LATTICE")

            if props.is_editing:
                row = self.layout.row(align=True)
                row.operator("bim.finish_editing_railing", icon="CHECKMARK", text="Finish Editing")
                row.operator("bim.cancel_editing_railing", icon="CANCEL", text="")

                general_props = props.get_general_kwargs()
                for prop in general_props:
                    if prop == "support_spacing" and props.use_manual_supports:
                        row = self.layout.row()
                        row.prop(props, prop)
                        row.active = False
                        continue
                    self.layout.prop(props, prop)

                update_railing_modifier_bmesh(context)

            elif props.is_editing_path:
                row.operator("bim.finish_editing_railing_path", icon="CHECKMARK", text="")
                row.operator("bim.cancel_editing_railing_path", icon="CANCEL", text="")

            else:
                row.operator("bim.enable_editing_railing", icon="GREASEPENCIL", text="")
                row.operator("bim.copy_railing_parameters", icon="COPYDOWN", text="")
                row.operator("bim.enable_editing_railing_path", icon="ANIM", text="")
                # TODO: good for preview but probably should move to .is_editing == True
                # since it's writing to ifc
                row.operator("bim.flip_railing_path_order", icon="ARROW_LEFTRIGHT", text="")
                row.operator("bim.remove_railing", icon="X", text="")

                box = self.layout.box()
                for prop_name, prop_value in RailingData.data["general_params"].items():
                    row = box.row(align=True)
                    row.label(text=prop_name)
                    row.label(text=str(prop_value))
        else:
            row = self.layout.row()
            row.label(text="No Railing Found")
            row.operator("bim.add_railing", icon="ADD", text="")


class BIM_PT_roof(bpy.types.Panel):
    bl_label = "Roof"
    bl_idname = "BIM_PT_roof"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_parametric_geometry"

    @classmethod
    def poll(cls, context):
        return tool.Blender.Modifier.is_eligible_for_roof_modifier(context.active_object)

    def draw(self, context):
        if not RoofData.is_loaded:
            RoofData.load()

        obj = context.active_object
        assert obj
        props = tool.Model.get_roof_props(obj)

        if RoofData.data["pset_data"]:
            row = self.layout.row(align=True)
            row.label(text="Roof parameters", icon="OUTLINER_OB_LATTICE")

            if props.is_editing:
                row = self.layout.row(align=True)
                row.operator("bim.finish_editing_roof", icon="CHECKMARK", text="Finish Editing")
                row.operator("bim.cancel_editing_roof", icon="CANCEL", text="")

                general_props = props.get_general_kwargs()
                for prop in general_props:
                    self.layout.prop(props, prop)

                update_roof_modifier_bmesh(obj)
            elif props.is_editing_path:
                row.operator("bim.finish_editing_roof_path", icon="CHECKMARK", text="")
                row.operator("bim.cancel_editing_roof_path", icon="CANCEL", text="")
            else:
                row.operator("bim.enable_editing_roof", icon="GREASEPENCIL", text="")
                row.operator("bim.copy_roof_parameters", icon="COPYDOWN", text="")
                row.operator("bim.enable_editing_roof_path", icon="ANIM", text="")
                row.operator("bim.remove_roof", icon="X", text="")

                box = self.layout.box()
                for prop_name, prop_value in RoofData.data["general_params"].items():
                    row = box.row(align=True)
                    row.label(text=prop_name)
                    row.label(text=str(prop_value))
        else:
            row = self.layout.row()
            row.label(text="No Roof Found")
            row.operator("bim.add_roof", icon="ADD", text="")


def add_menu(self: bpy.types.Menu, context: bpy.types.Context) -> None:
    self.layout.operator_context = "INVOKE_REGION_WIN"
    self.layout.operator("bim.add_element", icon_value=bonsai.bim.icons["IFC"].icon_id, text="IFC Element")
    self.layout.separator()
