# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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

import bpy
import blenderbim.tool as tool
from bpy.types import Panel, Operator, Menu
from blenderbim.bim.module.model.data import (
    AuthoringData,
    ArrayData,
    StairData,
    SverchokData,
    WindowData,
    DoorData,
    RailingData,
    RoofData,
)
from blenderbim.bim.module.model.prop import get_ifc_class
from blenderbim.bim.module.model.stair import update_stair_modifier
from blenderbim.bim.module.model.window import update_window_modifier_bmesh
from blenderbim.bim.module.model.door import update_door_modifier_bmesh
from blenderbim.bim.module.model.railing import update_railing_modifier_bmesh
from blenderbim.bim.module.model.roof import update_roof_modifier_bmesh
from blenderbim.bim.helper import prop_with_search
from math import degrees


class LaunchTypeManager(bpy.types.Operator):
    bl_idname = "bim.launch_type_manager"
    bl_label = "Launch Type Manager"
    bl_options = {"REGISTER"}
    bl_description = "Display all available Construction Types to add new instances"

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        props = context.scene.BIMModelProperties
        props.type_page = 1
        if get_ifc_class(None, context):
            props.type_class = props.ifc_class
            bpy.ops.bim.load_type_thumbnails(ifc_class=props.ifc_class, offset=0, limit=9)
        return context.window_manager.invoke_popup(self, width=550)

    def draw(self, context):
        props = context.scene.BIMModelProperties

        row = self.layout.row(align=True)
        prop_with_search(row, props, "type_class", text="")
        row.operator("bim.purge_unused_types", icon="TRASH", text="")

        columns = self.layout.column_flow(columns=3)
        row = columns.row()
        row.alignment = "LEFT"
        row.label(text=f"{AuthoringData.data['total_types']} Types", icon="FILE_VOLUME")

        row = columns.row(align=True)
        row.alignment = "CENTER"
        row.prop(props, "type_predefined_type", text="")
        row.prop(props, "type_template", text="")
        row.prop(props, "type_name", text="")
        row.operator("bim.add_type", icon="ADD", text="")

        row = columns.row(align=True)
        row.alignment = "RIGHT"
        if AuthoringData.data["total_pages"] > 1:
            row.label(text=f"Page {props.type_page}/{AuthoringData.data['total_pages']} ")
        if AuthoringData.data["prev_page"]:
            op = row.operator("bim.change_type_page", icon="TRIA_LEFT", text="")
            op.page = AuthoringData.data["prev_page"]
        if AuthoringData.data["next_page"]:
            op = row.operator("bim.change_type_page", icon="TRIA_RIGHT", text="")
            op.page = AuthoringData.data["next_page"]

        flow = self.layout.grid_flow(row_major=True, columns=3, even_columns=True, even_rows=True, align=True)

        for relating_type in AuthoringData.data["paginated_relating_types"]:
            outer_col = flow.column()
            box = outer_col.box()

            row = box.row()
            row.alignment = "CENTER"
            row.label(text=relating_type["name"], icon="FILE_3D")

            row = box.row()
            row.alignment = "CENTER"
            row.label(text=relating_type["description"])

            row = box.row()
            if relating_type["icon_id"]:
                row.template_icon(icon_value=relating_type["icon_id"], scale=4)
            else:
                op = box.operator("bim.load_type_thumbnails", text="Load Thumbnails", icon="FILE_REFRESH")
                op.ifc_class = props.type_class

            row = box.row(align=True)

            text = f"Add {relating_type['predefined_type']}" if relating_type["predefined_type"] else "Add"
            op = row.operator("bim.add_constr_type_instance", icon="ADD", text=text)
            op.from_invoke = True
            op.ifc_class = relating_type["ifc_class"]
            op.relating_type_id = relating_type["id"]

            op = row.operator("bim.select_type", icon="OBJECT_DATA", text="")
            op.relating_type = relating_type["id"]
            op = row.operator("bim.duplicate_type", icon="DUPLICATE", text="")
            op.element = relating_type["id"]
            op = row.operator("bim.remove_type", icon="X", text="")
            op.element = relating_type["id"]


class BIM_PT_authoring(Panel):
    bl_label = "Architectural"
    bl_idname = "BIM_PT_authoring"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        row = self.layout.row(align=True)
        row.operator("bim.generate_space")
        row = self.layout.row(align=True)
        row.operator("bim.generate_spaces_from_walls")


class BIM_PT_GridsSpatialManager(Panel):
    bl_label = "Grids and Containers"
    bl_idname = "BIM_PT_GridsSpatialManager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    bl_category = "BlenderBIM"

    def draw(self, context):
        pass

class BIM_PT_Grids(Panel):
    bl_label = "Grid Creator"
    bl_idname = "BIM_PT_Grids"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_GridsSpatialManager"

    def draw(self, context):
        self.animation_props = context.scene.BIMAnimationProperties
        row = self.layout.row()
        row.operator("mesh.add_grid", icon="ADD", text="Add Grids")

class BIM_PT_array(bpy.types.Panel):
    bl_label = "IFC Array"
    bl_idname = "BIM_PT_array"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and tool.Ifc.get_entity(context.active_object)

    def draw(self, context):
        if not ArrayData.is_loaded:
            ArrayData.load()

        props = context.active_object.BIMArrayProperties

        if ArrayData.data["parameters"]:
            row = self.layout.row(align=True)
            row.label(text=ArrayData.data["parameters"]["parent_name"], icon="CON_CHILDOF")
            op = row.operator("bim.select_array_parent", icon="OBJECT_DATA", text="")
            op.parent = ArrayData.data["parameters"]["Parent"]
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
                else:
                    row = box.row(align=True)
                    name = f"{array['count']} Items ({array.get('method', 'OFFSET').capitalize()})"
                    row.label(text=name, icon="MOD_ARRAY")
                    row.operator("bim.enable_editing_array", icon="GREASEPENCIL", text="").item = i
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
    bl_label = "IFC Stair"
    bl_idname = "BIM_PT_stair"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        # always display modifier if it's IFC object
        return tool.Ifc.get() and tool.Ifc.get_entity(context.active_object)

    def draw(self, context):
        if not StairData.is_loaded:
            StairData.load()

        props = context.active_object.BIMStairProperties

        if StairData.data["parameters"]:
            row = self.layout.row(align=True)
            row.label(text="Stair parameters", icon="IPO_CONSTANT")

            stair_data = StairData.data["parameters"]["data_dict"]
            if props.is_editing != -1:
                row = self.layout.row(align=True)
                row.operator("bim.finish_editing_stair", icon="CHECKMARK", text="Finish Editing")
                row.operator("bim.cancel_editing_stair", icon="CANCEL", text="")
                row = self.layout.row(align=True)
                for prop_name in props.get_props_kwargs():
                    self.layout.prop(props, prop_name)
                update_stair_modifier(context)
            else:
                row.operator("bim.enable_editing_stair", icon="GREASEPENCIL", text="")
                row.operator("bim.remove_stair", icon="X", text="")
                row = self.layout.row(align=True)
                for prop in props.get_props_kwargs():
                    prop_value = stair_data[prop]
                    prop_value = round(prop_value, 5) if type(prop_value) is float else prop_value
                    row = self.layout.row(align=True)
                    row.label(text=f"{props.bl_rna.properties[prop].name}")
                    row.label(text=str(prop_value))

            # calculated properties
            number_of_rises = props.number_of_treads + 1
            row = self.layout.row(align=True)
            row.label(text="Number of risers")
            row.label(text=str(number_of_rises))
            row = self.layout.row(align=True)
            row.label(text="Tread rise")
            row.label(text=str(round(props.height / number_of_rises, 5)))
            row = self.layout.row(align=True)
            row.label(text="Length")
            row.label(text=str(round(props.tread_run * number_of_rises, 5)))
        else:
            row = self.layout.row()
            row.label(text="No Stair Found")
            row.operator("bim.add_stair", icon="ADD", text="")


class BIM_PT_sverchok(bpy.types.Panel):
    bl_label = "IFC Sverchok"
    bl_idname = "BIM_PT_sverchok"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"
    bl_options = {"DEFAULT_CLOSED"}

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
    bl_label = "IFC Window"
    bl_idname = "BIM_PT_window"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        # always display modifier if it's IFC object
        return tool.Ifc.get() and tool.Ifc.get_entity(context.active_object)

    def draw(self, context):
        if not WindowData.is_loaded:
            WindowData.load()

        props = context.active_object.BIMWindowProperties

        if WindowData.data["parameters"]:
            row = self.layout.row(align=True)
            row.label(text="Window parameters", icon="OUTLINER_OB_LATTICE")

            window_data = WindowData.data["parameters"]["data_dict"]
            number_of_panels, panels_data = props.window_types_panels[props.window_type]

            if props.is_editing != -1:
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

                update_window_modifier_bmesh(context)

            else:
                row.operator("bim.enable_editing_window", icon="GREASEPENCIL", text="")
                row.operator("bim.remove_window", icon="X", text="")

                box = self.layout.box()
                general_props = props.get_general_kwargs()
                for prop in general_props:
                    prop_value = window_data[prop]
                    prop_value = round(prop_value, 5) if type(prop_value) is float else prop_value
                    row = box.row(align=True)
                    row.label(text=f"{props.bl_rna.properties[prop].name}")
                    row.label(text=str(prop_value))

                lining_props = props.get_lining_kwargs()
                self.layout.label(text="Lining properties")
                lining_box = self.layout.box()
                for prop in lining_props:
                    prop_value = window_data["lining_properties"][prop]
                    prop_value = round(prop_value, 5) if type(prop_value) is float else prop_value
                    row = lining_box.row(align=True)
                    row.label(text=f"{props.bl_rna.properties[prop].name}")
                    row.label(text=str(prop_value))

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

                # TODO: align property values more evenly
                for prop in panel_props:
                    cols[0].row().label(text=f"{props.bl_rna.properties[prop].name}")
                    for panel_i in range(number_of_panels):
                        r = cols[panel_i + 1].row()
                        r.alignment = "CENTER"
                        prop_value = window_data["panel_properties"][prop][panel_i]
                        prop_value = round(prop_value, 5) if type(prop_value) is float else prop_value
                        r.label(text=str(prop_value))
                        r = cols[panel_i + 1].row()

        else:
            row = self.layout.row()
            row.label(text="No Window Found")
            row.operator("bim.add_window", icon="ADD", text="")


class BIM_PT_door(bpy.types.Panel):
    bl_label = "IFC Door"
    bl_idname = "BIM_PT_door"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        # always display modifier if it's IFC object
        return tool.Ifc.get() and tool.Ifc.get_entity(context.active_object)

    def draw(self, context):
        if not DoorData.is_loaded:
            DoorData.load()

        props = context.active_object.BIMDoorProperties

        if DoorData.data["parameters"]:
            row = self.layout.row(align=True)
            row.label(text="Door parameters", icon="OUTLINER_OB_LATTICE")

            door_data = DoorData.data["parameters"]["data_dict"]

            if props.is_editing != -1:
                row = self.layout.row(align=True)
                row.operator("bim.finish_editing_door", icon="CHECKMARK", text="Finish Editing")
                row.operator("bim.cancel_editing_door", icon="CANCEL", text="")

                general_props = props.get_general_kwargs()
                for prop in general_props:
                    self.layout.prop(props, prop)

                lining_props = props.get_lining_kwargs()
                self.layout.label(text="Lining properties")
                for prop in lining_props:
                    self.layout.prop(props, prop)

                panel_props = props.get_panel_kwargs()
                self.layout.label(text="Panel properties")
                for prop in panel_props:
                    self.layout.prop(props, prop)

                update_door_modifier_bmesh(context)

            else:
                row.operator("bim.enable_editing_door", icon="GREASEPENCIL", text="")
                row.operator("bim.remove_door", icon="X", text="")

                box = self.layout.box()
                general_props = props.get_general_kwargs()
                for prop in general_props:
                    prop_value = door_data[prop]
                    prop_value = round(prop_value, 5) if type(prop_value) is float else prop_value
                    row = box.row(align=True)
                    row.label(text=f"{props.bl_rna.properties[prop].name}")
                    row.label(text=str(prop_value))

                lining_props = props.get_lining_kwargs()
                self.layout.label(text="Lining properties")
                lining_box = self.layout.box()
                for prop in lining_props:
                    prop_value = door_data["lining_properties"][prop]
                    prop_value = round(prop_value, 5) if type(prop_value) is float else prop_value
                    row = lining_box.row(align=True)
                    row.label(text=f"{props.bl_rna.properties[prop].name}")
                    row.label(text=str(prop_value))

                panel_props = props.get_panel_kwargs()
                self.layout.label(text="Panel properties")
                panel_box = self.layout.box()
                for prop in panel_props:
                    prop_value = door_data["panel_properties"][prop]
                    prop_value = round(prop_value, 5) if type(prop_value) is float else prop_value
                    row = panel_box.row(align=True)
                    row.label(text=f"{props.bl_rna.properties[prop].name}")
                    row.label(text=str(prop_value))
        else:
            row = self.layout.row()
            row.label(text="No Door Found")
            row.operator("bim.add_door", icon="ADD", text="")


class BIM_PT_railing(bpy.types.Panel):
    bl_label = "IFC Railing"
    bl_idname = "BIM_PT_railing"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        # always display modifier if it's IFC object
        return tool.Ifc.get() and tool.Ifc.get_entity(context.active_object)

    def draw(self, context):
        if not RailingData.is_loaded:
            RailingData.load()

        props = context.active_object.BIMRailingProperties

        if RailingData.data["parameters"]:
            row = self.layout.row(align=True)
            row.label(text="Railing parameters", icon="OUTLINER_OB_LATTICE")

            railing_data = RailingData.data["parameters"]["data_dict"]

            if props.is_editing != -1:
                row = self.layout.row(align=True)
                row.operator("bim.finish_editing_railing", icon="CHECKMARK", text="Finish Editing")
                row.operator("bim.cancel_editing_railing", icon="CANCEL", text="")

                general_props = props.get_general_kwargs()
                for prop in general_props:
                    self.layout.prop(props, prop)

                update_railing_modifier_bmesh(context)

            elif props.is_editing_path:
                row.operator("bim.finish_editing_railing_path", icon="CHECKMARK", text="")
                row.operator("bim.cancel_editing_railing_path", icon="CANCEL", text="")

            else:
                row.operator("bim.enable_editing_railing", icon="GREASEPENCIL", text="")
                row.operator("bim.enable_editing_railing_path", icon="ANIM", text="")
                # TODO: good for preview but probably should move to .is_editing == -1
                # since it's writing to ifc
                row.operator("bim.flip_railing_path_order", icon="ARROW_LEFTRIGHT", text="")
                row.operator("bim.remove_railing", icon="X", text="")

                box = self.layout.box()
                general_props = props.get_general_kwargs()
                for prop in general_props:
                    prop_value = railing_data[prop]
                    prop_value = round(prop_value, 5) if type(prop_value) is float else prop_value
                    row = box.row(align=True)
                    row.label(text=f"{props.bl_rna.properties[prop].name}")
                    row.label(text=str(prop_value))
        else:
            row = self.layout.row()
            row.label(text="No Railing Found")
            row.operator("bim.add_railing", icon="ADD", text="")


class BIM_PT_roof(bpy.types.Panel):
    bl_label = "IFC Roof"
    bl_idname = "BIM_PT_roof"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        # always display modifier if it's IFC object
        return tool.Ifc.get() and tool.Ifc.get_entity(context.active_object)

    def draw(self, context):
        if not RoofData.is_loaded:
            RoofData.load()

        props = context.active_object.BIMRoofProperties

        if RoofData.data["parameters"]:
            row = self.layout.row(align=True)
            row.label(text="Roof parameters", icon="OUTLINER_OB_LATTICE")

            roof_data = RoofData.data["parameters"]["data_dict"]

            if props.is_editing != -1:
                row = self.layout.row(align=True)
                row.operator("bim.finish_editing_roof", icon="CHECKMARK", text="Finish Editing")
                row.operator("bim.cancel_editing_roof", icon="CANCEL", text="")

                general_props = props.get_general_kwargs()
                for prop in general_props:
                    self.layout.prop(props, prop)

                update_roof_modifier_bmesh(context)

            elif props.is_editing_path:
                row.operator("bim.finish_editing_roof_path", icon="CHECKMARK", text="")
                row.operator("bim.cancel_editing_roof_path", icon="CANCEL", text="")

            else:
                row.operator("bim.enable_editing_roof", icon="GREASEPENCIL", text="")
                row.operator("bim.enable_editing_roof_path", icon="ANIM", text="")
                row.operator("bim.remove_roof", icon="X", text="")

                box = self.layout.box()
                general_props = props.get_general_kwargs()
                for prop in general_props:
                    prop_value = roof_data[prop]
                    prop_value = round(prop_value, 5) if type(prop_value) is float else prop_value
                    row = box.row(align=True)
                    row.label(text=f"{props.bl_rna.properties[prop].name}")
                    if prop in ("angle", "rafter_edge_angle"):
                        prop_value = round(degrees(prop_value), 2)
                    row.label(text=str(prop_value))
        else:
            row = self.layout.row()
            row.label(text="No Roof Found")
            row.operator("bim.add_roof", icon="ADD", text="")


class BIM_MT_model(Menu):
    bl_idname = "BIM_MT_model"
    bl_label = "IFC Objects"

    def draw(self, context):
        layout = self.layout
        layout.operator("bim.add_empty_type", text="Empty Type", icon="EMPTY_AXIS")
        layout.operator("bim.add_potential_half_space_solid", text="Half Space Proxy", icon="ORIENTATION_NORMAL")
        layout.operator("bim.add_potential_opening", text="Opening Proxy", icon="CUBE")


def add_menu(self, context):
    self.layout.menu("BIM_MT_model", icon="FILE_3D")
