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
from bonsai.bim.ifc import IfcStore
from bonsai.bim.helper import prop_with_search
from bonsai.bim.module.pset.data import (
    ObjectPsetsData,
    ObjectQtosData,
    MaterialPsetsData,
    MaterialSetPsetsData,
    MaterialSetItemPsetsData,
    TaskQtosData,
    ResourceQtosData,
    ResourcePsetsData,
    GroupQtosData,
    GroupPsetData,
    ProfilePsetsData,
    WorkSchedulePsetsData,
)
from bonsai.bim.module.material.data import ObjectMaterialData
from typing import Any, Optional


def draw_property(
    prop: bpy.types.PropertyGroup, layout: bpy.types.UILayout, copy_operator: Optional[str] = None
) -> None:
    if prop.value_type == "IfcPropertySingleValue":
        draw_single_property(prop, layout, copy_operator)
    elif prop.value_type == "IfcPropertyEnumeratedValue":
        draw_enumerated_property(prop, layout, copy_operator)


def draw_single_property(
    prop: bpy.types.PropertyGroup, layout: bpy.types.UILayout, copy_operator: Optional[str] = None
) -> None:
    value_name = prop.metadata.get_value_name(display_only=True)
    if not value_name:
        layout.label(text=prop["Name"])
        return
    layout.prop(
        prop.metadata,
        value_name,
        text=prop.metadata.display_name,
    )
    if prop.metadata.is_uri:
        op = layout.operator("bim.select_uri_attribute", text="", icon="FILE_FOLDER")
        op.data_path = prop.metadata.path_from_id("string_value")
    if prop.metadata.is_optional:
        layout.prop(prop.metadata, "is_null", icon="RADIOBUT_OFF" if prop.metadata.is_null else "RADIOBUT_ON", text="")
    if copy_operator:
        op = layout.operator(f"{copy_operator}", text="", icon="COPYDOWN")
        op.name = prop.metadata.name


def draw_enumerated_property(
    prop: bpy.types.PropertyGroup, layout: bpy.types.UILayout, copy_operator: Optional[str] = None
) -> None:
    value_name = prop.metadata.get_value_name()
    if not value_name:
        layout.label(text=prop.metadata.name)
        return
    if len(prop.enumerated_value.enumerated_values) != 0:
        layout.label(text=prop.metadata.name)
        grid = layout.column_flow(columns=3)
        for e in prop.enumerated_value.enumerated_values:
            grid.prop(e, "is_selected", text=str(e[value_name]))
    if copy_operator:
        op = layout.operator(f"{copy_operator}", text="", icon="COPYDOWN")
        op.name = prop.metadata.name


def get_active_pset_obj_name(context: bpy.types.Context, obj_type: tool.Ifc.OBJECT_TYPE) -> str:
    if obj_type in ("Object", "MaterialSet", "MaterialSetItem"):
        return context.active_object.name
    return ""


def draw_psetqto_ui(
    context: bpy.types.Context,
    pset_id: int,
    pset: dict[str, Any],
    props: bpy.types.PropertyGroup,
    layout: bpy.types.UILayout,
    obj_type: tool.Ifc.OBJECT_TYPE,
    allow_removing: bool = True,
    filter_keyword: str = "",
) -> None:

    active_operator = context.active_operator

    filter_keyword = filter_keyword.lower()
    box = layout.box()
    row = box.row(align=True)
    if "is_expanded" not in pset:
        pset["is_expanded"] = True
    icon = "TRIA_DOWN" if pset["is_expanded"] else "TRIA_RIGHT"
    row.operator("bim.toggle_pset_expansion", icon=icon, text="", emboss=False).pset_id = pset_id
    obj_name = get_active_pset_obj_name(context, obj_type)
    if props.active_pset_id == pset_id:
        row.prop(props, "active_pset_name", icon="COPY_ID", text="")
        op = row.operator("bim.edit_pset", icon="CHECKMARK", text="")
        op.pset_id = pset_id
        op.obj = obj_name
        op.obj_type = obj_type
        op = row.operator("bim.disable_pset_editing", icon="CANCEL", text="")
        op.obj = obj_name
        op.obj_type = obj_type
    elif not props.active_pset_id:
        row.label(text=f'{pset["Name"]}', icon="COPY_ID")

        if (shared := pset["shared_pset_uses"]) > 1:
            unshare_pset_row = row.row(align=True)
            unshare_pset_row.alignment = "RIGHT"
            op = unshare_pset_row.operator("bim.unshare_pset", text=str(shared))
            op.description_ = f"Pset is reused by {shared} elements.\n\n"
            op.pset_id = pset_id
            op.obj = obj_name
            op.obj_type = obj_type

        op = row.operator("bim.enable_pset_editing", icon="GREASEPENCIL", text="")
        op.pset_id = pset_id
        op.obj = obj_name
        op.obj_type = obj_type
        if pset["has_template"]:
            row.label(text="", icon="ASSET_MANAGER")
        else:
            op = row.operator("bim.save_pset_as_template", icon="ASSET_MANAGER", text="")
            op.pset_id = pset_id
        remove_pset_row = row.row(align=True)
        op = remove_pset_row.operator("bim.remove_pset", icon="X", text="")
        op.pset_id = pset_id
        op.obj = obj_name
        op.obj_type = obj_type
        remove_pset_row.enabled = allow_removing
    elif props.active_pset_id != pset_id:
        row.label(text=pset["Name"], icon="COPY_ID")
        remove_pset_row = row.row(align=True)
        op = remove_pset_row.operator("bim.remove_pset", icon="X", text="")
        op.pset_id = pset_id
        op.obj = obj_name
        op.obj_type = obj_type
        remove_pset_row.enabled = allow_removing
    if pset["is_expanded"]:
        if props.active_pset_id == pset_id:
            is_parametric_pset = props.active_pset_name in tool.Model.BBIM_PARAMETRIC_PSETS
            if is_parametric_pset:
                box_ = box.box()
                box_.alert = True
                box_.label(text="Warning! This pset should not be edited directly", icon="ERROR")
                box_.label(text="and should be edited from Parametric Geometry UI.")

            for prop in props.properties:
                draw_psetqto_editable_ui(box, props, prop)

            if not props.active_pset_has_template and not is_parametric_pset:
                row = box.row(align=True)
                row.prop(props, "prop_name", text="")
                row.prop(props, "prop_value", text="")
                op = row.operator("bim.add_proposed_prop", text="", icon="ADD")
                op.obj = obj_name
                op.obj_type = obj_type
                op.prop_name = props.prop_name
                op.prop_value = props.prop_value
        else:
            has_props_displayed = False
            for prop in pset["Properties"]:
                if tool.Blender.get_addon_preferences().should_hide_empty_props and (
                    prop["NominalValue"] is None or prop["NominalValue"] == ""
                ):
                    continue
                nominal_value = str(prop["NominalValue"])
                if (
                    filter_keyword
                    and filter_keyword not in prop["Name"].lower()
                    and filter_keyword not in nominal_value.lower()
                ):
                    continue
                has_props_displayed = True
                row = box.row(align=True)
                row.scale_y = 0.8
                row.label(text=prop["Name"])
                op = row.operator("bim.select_similar", text=nominal_value, icon="NONE", emboss=False)
                op.key = '"' + pset["Name"].replace('"', '\\"') + '"."' + prop["Name"].replace('"', '\\"') + '"'
                # calculate sum of all selected objects
                if active_operator:
                    if active_operator.bl_idname == "BIM_OT_select_similar":
                        calculated_sum = getattr(active_operator, "calculated_sum", 0.0)
                        if (
                            op.key == active_operator.key
                            and calculated_sum != 0
                            and isinstance(float(nominal_value), (int, float))
                        ):
                            row.label(text=f"(Sum: {calculated_sum})")
            if not has_props_displayed:
                row = box.row()
                row.scale_y = 0.8
                row.label(text="No Properties")


def draw_psetqto_editable_ui(
    box: bpy.types.UILayout, props: bpy.types.PropertyGroup, prop: bpy.types.PropertyGroup
) -> None:
    row = box.row(align=True)
    draw_property(prop, row, copy_operator="bim.copy_property_to_selection")


class BIM_PT_object_psets(Panel):
    bl_label = "Property Sets"
    bl_idname = "BIM_PT_object_psets"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_tab_object_metadata"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw_header(self, context):
        row = self.layout.row(align=True)
        row.label(text="")  # empty text occupies the left of the row
        row.prop(context.scene.GlobalPsetProperties, "pset_filter", text="", icon="VIEWZOOM")

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        return True

    def draw(self, context):
        if not ObjectPsetsData.is_loaded:
            ObjectPsetsData.load()

        props = context.active_object.PsetProperties
        row = self.layout.row(align=True)
        prop_with_search(row, props, "pset_name", text="")
        op = row.operator("bim.add_pset", icon="ADD", text="")
        op.obj = context.active_object.name
        op.obj_type = "Object"

        if not props.active_pset_id and props.active_pset_name and props.active_pset_type == "PSET":
            draw_psetqto_ui(
                context,
                0,
                {},
                props,
                self.layout,
                "Object",
                filter_keyword=context.scene.GlobalPsetProperties.pset_filter,
            )

        if ObjectPsetsData.data["psets"]:
            if ObjectPsetsData.data["is_occurrence"]:
                self.layout.label(text="Occurrence Properties:")
            else:
                self.layout.label(text="Type Properties:")
            for pset in ObjectPsetsData.data["psets"]:
                draw_psetqto_ui(
                    context,
                    pset["id"],
                    pset,
                    props,
                    self.layout,
                    "Object",
                    filter_keyword=context.scene.GlobalPsetProperties.pset_filter,
                )

        if ObjectPsetsData.data["inherited_psets"]:
            self.layout.label(text="Inherited Type Properties:", icon="CON_CHILDOF")
            for pset in ObjectPsetsData.data["inherited_psets"]:
                draw_psetqto_ui(
                    context,
                    pset["id"],
                    pset,
                    props,
                    self.layout,
                    "Object",
                    allow_removing=False,
                    filter_keyword=context.scene.GlobalPsetProperties.pset_filter,
                )


class BIM_PT_object_qtos(Panel):
    bl_label = "Quantity Sets"
    bl_idname = "BIM_PT_object_qtos"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_tab_object_metadata"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw_header(self, context):
        row = self.layout.row(align=True)
        row.label(text="")  # empty text occupies the left of the row
        row.prop(context.scene.GlobalPsetProperties, "qto_filter", text="", icon="VIEWZOOM")

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        return True

    def draw(self, context):
        if not ObjectQtosData.is_loaded:
            ObjectQtosData.load()

        props = context.active_object.PsetProperties
        row = self.layout.row(align=True)
        prop_with_search(row, props, "qto_name", text="")
        op = row.operator("bim.add_qto", icon="ADD", text="")
        op.obj = context.active_object.name
        op.obj_type = "Object"

        if not props.active_pset_id and props.active_pset_name and props.active_pset_type == "QTO":
            draw_psetqto_ui(
                context,
                0,
                {},
                props,
                self.layout,
                "Object",
                filter_keyword=context.scene.GlobalPsetProperties.qto_filter,
            )

        if ObjectQtosData.data["qtos"]:
            if ObjectQtosData.data["is_occurrence"]:
                self.layout.label(text="Occurrence Quantities:")
            else:
                self.layout.label(text="Type Quantities:")
            for qto in ObjectQtosData.data["qtos"]:
                draw_psetqto_ui(
                    context,
                    qto["id"],
                    qto,
                    props,
                    self.layout,
                    "Object",
                    filter_keyword=context.scene.GlobalPsetProperties.qto_filter,
                )

        if ObjectQtosData.data["inherited_qsets"]:
            self.layout.label(text="Inherited Type Quantities:", icon="CON_CHILDOF")
            for qset in ObjectQtosData.data["inherited_qsets"]:
                draw_psetqto_ui(
                    context,
                    qset["id"],
                    qset,
                    props,
                    self.layout,
                    "Object",
                    allow_removing=False,
                    filter_keyword=context.scene.GlobalPsetProperties.qto_filter,
                )
        layout = self.layout
        qtoprops = context.scene.BIMQtoProperties
        row = layout.row()
        row.prop(qtoprops, "qto_rule", text="")
        row = layout.row()
        row.operator("bim.perform_quantity_take_off")


class BIM_PT_material_psets(Panel):
    bl_label = "Material Property Sets"
    bl_idname = "BIM_PT_material_psets"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_materials"

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if not ifc_file or ifc_file.schema == "IFC2X3":
            return False  # We don't support material psets in IFC2X3 because they suck
        props = context.scene.BIMMaterialProperties
        if props.materials and props.active_material_index < len(props.materials):
            material = props.materials[props.active_material_index]
            if material.ifc_definition_id:
                return True
        return False

    def draw(self, context):
        props = context.scene.BIMMaterialProperties
        if props.materials and props.active_material_index < len(props.materials):
            ifc_definition_id = props.materials[props.active_material_index].ifc_definition_id

        if not MaterialPsetsData.is_loaded:
            MaterialPsetsData.load()
        elif ifc_definition_id != MaterialPsetsData.data["ifc_definition_id"]:
            MaterialPsetsData.load()

        props = context.scene.MaterialPsetProperties
        row = self.layout.row(align=True)
        prop_with_search(row, props, "pset_name", text="")
        op = row.operator("bim.add_pset", icon="ADD", text="")
        op.obj = ""
        op.obj_type = "Material"

        if not props.active_pset_id and props.active_pset_name and props.active_pset_type == "PSET":
            draw_psetqto_ui(context, 0, {}, props, self.layout, "Material")

        for pset in MaterialPsetsData.data["psets"]:
            draw_psetqto_ui(context, pset["id"], pset, props, self.layout, "Material")


class BIM_PT_material_set_psets(Panel):
    bl_label = "Material Set Property Sets"
    bl_idname = "BIM_PT_material_set_psets"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_object_material"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        if not tool.Ifc.get() or tool.Ifc.get().schema == "IFC2X3":
            return False  # We don't support material psets in IFC2X3 because they suck
        if not tool.Ifc.get_entity(context.active_object):
            return False
        if not ObjectMaterialData.is_loaded:
            ObjectMaterialData.load()
        ifc_class = ObjectMaterialData.data["material_class"]
        return bool(ifc_class and "Set" in ifc_class)

    def draw(self, context):
        if not MaterialSetPsetsData.is_loaded:
            MaterialSetPsetsData.load()

        props = context.active_object.MaterialSetPsetProperties
        row = self.layout.row(align=True)
        prop_with_search(row, props, "pset_name", text="")
        op = row.operator("bim.add_pset", icon="ADD", text="")
        op.obj = context.active_object.name
        op.obj_type = "MaterialSet"

        if not props.active_pset_id and props.active_pset_name and props.active_pset_type == "PSET":
            draw_psetqto_ui(context, 0, {}, props, self.layout, "MaterialSet")

        for pset in MaterialSetPsetsData.data["psets"]:
            draw_psetqto_ui(context, pset["id"], pset, props, self.layout, "MaterialSet")


class BIM_PT_material_set_item_psets(Panel):
    bl_label = "Material Set Item Property Sets"
    bl_idname = "BIM_PT_material_set_item_psets"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_object_material"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        if not tool.Ifc.get() or tool.Ifc.get().schema == "IFC2X3":
            return False  # We don't support material psets in IFC2X3 because they suck
        if not tool.Ifc.get_entity(context.active_object):
            return False
        if not ObjectMaterialData.is_loaded:
            ObjectMaterialData.load()
        ifc_class = ObjectMaterialData.data["material_class"]
        return bool(ifc_class and "Set" in ifc_class)

    def draw(self, context):
        if not MaterialSetItemPsetsData.is_loaded:
            MaterialSetItemPsetsData.load()

        obj = context.active_object
        assert obj
        if not obj.BIMObjectMaterialProperties.active_material_set_item_id:
            self.layout.label(text="No Material Set Item Edited.")
            return

        props = obj.MaterialSetItemPsetProperties
        row = self.layout.row(align=True)
        prop_with_search(row, props, "pset_name", text="")
        op = row.operator("bim.add_pset", icon="ADD", text="")
        op.obj = obj.name
        op.obj_type = "MaterialSetItem"

        if not props.active_pset_id and props.active_pset_name and props.active_pset_type == "PSET":
            draw_psetqto_ui(context, 0, {}, props, self.layout, "MaterialSetItem")

        for pset in MaterialSetItemPsetsData.data["psets"]:
            draw_psetqto_ui(context, pset["id"], pset, props, self.layout, "MaterialSetItem")


class BIM_PT_task_qtos(Panel):
    bl_label = "Task Quantity Sets"
    bl_idname = "BIM_PT_task_qtos"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_work_schedules"
    bl_order = 2

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMWorkScheduleProperties
        if not props.active_work_schedule_id:
            return False
        total_tasks = len(context.scene.BIMTaskTreeProperties.tasks)
        if total_tasks > 0 and props.active_task_index < total_tasks:
            return True
        return False

    def draw(self, context):
        if not TaskQtosData.is_loaded:
            TaskQtosData.load()

        props = context.scene.TaskPsetProperties
        row = self.layout.row(align=True)
        row.prop(props, "qto_name", text="")
        op = row.operator("bim.add_qto", icon="ADD", text="")
        op.obj_type = "Task"

        if not props.active_pset_id and props.active_pset_name and props.active_pset_type == "QTO":
            draw_psetqto_ui(context, 0, {}, props, self.layout, "Task")

        for qto in TaskQtosData.data["qtos"]:
            draw_psetqto_ui(context, qto["id"], qto, props, self.layout, "Task")


class BIM_PT_resource_qtos(Panel):
    bl_label = "Resource Quantity Sets"
    bl_idname = "BIM_PT_resource_qtos"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_resources"

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMResourceProperties
        total_resources = len(context.scene.BIMResourceTreeProperties.resources)
        if total_resources > 0 and props.active_resource_index < total_resources:
            return True
        return False

    def draw(self, context):
        if not ResourceQtosData.is_loaded:
            ResourceQtosData.load()

        props = context.scene.ResourcePsetProperties
        row = self.layout.row(align=True)
        row.prop(props, "qto_name", text="")
        op = row.operator("bim.add_qto", icon="ADD", text="")
        op.obj_type = "Resource"

        if not props.active_pset_id and props.active_pset_name and props.active_pset_type == "QTO":
            draw_psetqto_ui(context, 0, {}, props, self.layout, "Resource")

        for qto in ResourceQtosData.data["qtos"]:
            draw_psetqto_ui(context, qto["id"], qto, props, self.layout, "Resource")


class BIM_PT_resource_psets(Panel):
    bl_label = "Resource Property Sets"
    bl_idname = "BIM_PT_resource_psets"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_resources"

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMResourceProperties
        total_resources = len(context.scene.BIMResourceTreeProperties.resources)
        if total_resources > 0 and props.active_resource_index < total_resources:
            return True
        return False

    def draw(self, context):
        if not ResourcePsetsData.is_loaded:
            ResourcePsetsData.load()

        props = context.scene.ResourcePsetProperties
        row = self.layout.row(align=True)
        prop_with_search(row, props, "pset_name", text="")
        op = row.operator("bim.add_pset", icon="ADD", text="")
        op.obj_type = "Resource"

        if not props.active_pset_id and props.active_pset_name and props.active_pset_type == "PSET":
            draw_psetqto_ui(context, 0, {}, props, self.layout, "Resource")

        for pset in ResourcePsetsData.data["psets"]:
            draw_psetqto_ui(context, pset["id"], pset, props, self.layout, "Resource")


class BIM_PT_group_qtos(Panel):
    bl_label = "Group Quantity Sets"
    bl_idname = "BIM_PT_group_qtos"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_groups"

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMGroupProperties
        total_resources = len(props.groups)
        if total_resources > 0 and props.active_group_index < total_resources:
            return True
        return False

    def draw(self, context):
        if not GroupQtosData.is_loaded:
            GroupQtosData.load()

        props = context.scene.GroupPsetProperties
        row = self.layout.row(align=True)
        row.prop(props, "qto_name", text="")
        op = row.operator("bim.add_qto", icon="ADD", text="")
        op.obj_type = "Group"

        if not props.active_pset_id and props.active_pset_name and props.active_pset_type == "QTO":
            draw_psetqto_ui(context, 0, {}, props, self.layout, "Group")

        for qto in GroupQtosData.data["qtos"]:
            draw_psetqto_ui(context, qto["id"], qto, props, self.layout, "Group")


class BIM_PT_group_psets(Panel):
    bl_label = "Group Property Sets"
    bl_idname = "BIM_PT_group_psets"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_groups"

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMGroupProperties
        total_resources = len(props.groups)
        if total_resources > 0 and props.active_group_index < total_resources:
            return True
        return False

    def draw(self, context):
        if not GroupPsetData.is_loaded:
            GroupPsetData.load()

        props = context.scene.GroupPsetProperties
        row = self.layout.row(align=True)
        prop_with_search(row, props, "pset_name", text="")
        op = row.operator("bim.add_pset", icon="ADD", text="")
        op.obj_type = "Group"

        if not props.active_pset_id and props.active_pset_name and props.active_pset_type == "PSET":
            draw_psetqto_ui(context, 0, {}, props, self.layout, "Group")

        for pset in GroupPsetData.data["psets"]:
            draw_psetqto_ui(context, pset["id"], pset, props, self.layout, "Group")


class BIM_PT_profile_psets(Panel):
    bl_label = "Profile Property Sets"
    bl_idname = "BIM_PT_profile_psets"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_profiles"

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMProfileProperties
        if not props.is_editing:
            return False
        total_profiles = len(context.scene.BIMProfileProperties.profiles)
        if total_profiles > 0 and props.active_profile_index < total_profiles:
            return True
        return False

    def draw(self, context):
        active_profile = tool.Profile.get_active_profile_ui()

        if not active_profile:
            return

        if (
            not ProfilePsetsData.is_loaded
            or active_profile.ifc_definition_id != ProfilePsetsData.data["ifc_definition_id"]
        ):
            ProfilePsetsData.load()

        props = context.scene.ProfilePsetProperties
        row = self.layout.row(align=True)
        prop_with_search(row, props, "pset_name", text="")
        op = row.operator("bim.add_pset", icon="ADD", text="")
        op.obj_type = "Profile"

        if not props.active_pset_id and props.active_pset_name and props.active_pset_type == "PSET":
            draw_psetqto_ui(context, 0, {}, props, self.layout, "Profile")

        for pset in ProfilePsetsData.data["psets"]:
            draw_psetqto_ui(context, pset["id"], pset, props, self.layout, "Profile")


class BIM_PT_work_schedule_psets(Panel):
    bl_label = "Work Schedule Property Sets"
    bl_idname = "BIM_PT_work_schedule_psets"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_work_schedules"
    bl_order = 3

    @classmethod
    def poll(cls, context):
        if not context.scene.BIMWorkScheduleProperties.active_work_schedule_id:
            return False
        return True

    def draw(self, context):
        if not WorkSchedulePsetsData.is_loaded:
            WorkSchedulePsetsData.load()

        props = context.scene.WorkSchedulePsetProperties
        row = self.layout.row(align=True)
        prop_with_search(row, props, "pset_name", text="")
        op = row.operator("bim.add_pset", icon="ADD", text="")
        op.obj_type = "WorkSchedule"

        if not props.active_pset_id and props.active_pset_name and props.active_pset_type == "PSET":
            draw_psetqto_ui(context, 0, {}, props, self.layout, "WorkSchedule")

        for pset in WorkSchedulePsetsData.data["psets"]:
            draw_psetqto_ui(context, pset["id"], pset, props, self.layout, "WorkSchedule")


class BIM_PT_bulk_property_editor(Panel):
    bl_label = "Bulk Property Editor"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_misc"

    def draw(self, context):
        pass


class BIM_PT_rename_parameters(Panel):
    bl_label = "Bulk Rename Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_bulk_property_editor"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        props = context.scene.RenameProperties

        row = layout.row()
        op = row.operator("bim.add_property_to_edit", icon="ADD")
        op.option = "RenameProperties"

        if props:
            for index, prop in enumerate(props):
                row = layout.row(align=True)
                prop_with_search(row, prop, "pset_name", text="")
                row.prop(prop, "existing_property_name", text="")
                row.prop(prop, "new_property_name", text="")
                op = row.operator("bim.remove_property_to_edit", icon="X", text="")
                op.index = index
                op.option = "RenameProperties"

        if props:
            row = layout.row(align=True)
            row.operator("bim.rename_parameters", icon="CHECKMARK")
            clear = row.operator("bim.clear_list", icon="CANCEL", text="")
            clear.option = "RenameProperties"


class BIM_PT_add_edit_custom_properties(Panel):
    bl_label = "Bulk Add / Edit Custom Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 2
    bl_parent_id = "BIM_PT_bulk_property_editor"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        props = context.scene.AddEditProperties

        row = layout.row()
        op = row.operator("bim.add_property_to_edit", icon="ADD")
        op.option = "AddEditProperties"
        op.index = -1

        if props:
            for index, prop in enumerate(props):
                row = layout.row(align=True)
                prop_with_search(row, prop, "pset_name", text="")
                row.prop(prop, "property_name", text="")
                if prop.template_type == "IfcPropertySingleValue":
                    row.prop(prop, prop.get_value_name(), text="")
                prop_with_search(row, prop, "primary_measure_type", text="")
                row.prop(prop, "template_type", text="")
                op = row.operator("bim.remove_property_to_edit", icon="X", text="")
                op.index = index
                op.option = "AddEditProperties"

                if prop.template_type == "IfcPropertyEnumeratedValue":
                    op = row.operator("bim.add_property_to_edit", icon="ADD", text="Add Enum")
                    op.option = "AddEditProperties"
                    op.index = index
                    for index2, prop2 in enumerate(prop.enum_values):
                        row = layout.row()
                        row.separator()
                        row.separator()
                        row.prop(prop2, prop.get_value_name(), text=f"#{index2}")
                        row.prop(prop2, "is_selected")
                        op = row.operator("bim.remove_property_to_edit", icon="X", text="")
                        op.index = index
                        op.index2 = index2
                        op.option = "AddEditProperties"

        if props:
            row = layout.row(align=True)
            op = row.operator("bim.add_edit_custom_property", icon="CHECKMARK", text="Apply Changes")
            clear = row.operator("bim.clear_list", icon="CANCEL", text="")
            clear.option = "AddEditProperties"


class BIM_PT_delete_psets(Panel):
    bl_label = "Bulk Remove Psets"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 3
    bl_parent_id = "BIM_PT_bulk_property_editor"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        props = context.scene.DeletePsets

        row = layout.row()
        op = row.operator("bim.add_property_to_edit", icon="ADD")
        op.option = "DeletePsets"

        if props:
            for index, prop in enumerate(props):
                row = layout.row(align=True)
                prop_with_search(row, prop, "pset_name", text="")
                op = row.operator("bim.remove_property_to_edit", icon="X", text="")
                op.index = index
                op.option = "DeletePsets"

        if props:
            row = layout.row(align=True)
            op = row.operator("bim.bulk_remove_psets", icon="CHECKMARK", text="Apply Changes")
            clear = row.operator("bim.clear_list", icon="CANCEL", text="")
            clear.option = "DeletePsets"
