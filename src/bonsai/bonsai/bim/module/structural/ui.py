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

import itertools
from typing import TYPE_CHECKING, Any, Union

import bpy
from bpy.types import Panel, UIList

import bonsai.bim.helper
import bonsai.tool as tool
from bonsai.bim.helper import draw_attributes, prop_with_search
from bonsai.bim.module.structural.data import (
    BoundaryConditionsData,
    ConnectedStructuralMembersData,
    StructuralAnalysisModelsData,
    StructuralBoundaryConditionsData,
    StructuralConnectionData,
    StructuralItemLoadsData,
    StructuralLoadCasesData,
    StructuralLoadCombinationsData,
    StructuralLoadsData,
    StructuralMemberData,
)

if TYPE_CHECKING:
    from bonsai.bim.module.structural.prop import (
        BIMObjectStructuralProperties,
        BIMStructuralProperties,
        BoundaryCondition,
        StructuralActivity,
        StructuralAnalysisModel,
        StructuralLoad,
    )


def draw_boundary_condition_ui(
    layout: bpy.types.UILayout,
    boundary_condition: dict[str, Any],
    connection_id: int,
    props: BIMObjectStructuralProperties,
) -> None:
    row = layout.row(align=True)
    if not boundary_condition:
        row.label(text="No Boundary Condition Found", icon="CON_TRACKTO")
        row.operator("bim.add_structural_boundary_condition", text="", icon="ADD").connection = connection_id
        return

    if props.active_boundary_condition and props.active_boundary_condition == boundary_condition["id"]:
        row.label(text=boundary_condition["type"], icon="CON_TRACKTO")
        row.operator("bim.edit_structural_boundary_condition", text="", icon="CHECKMARK").connection = connection_id
        row.operator("bim.disable_editing_structural_boundary_condition", text="", icon="CANCEL")
    elif props.active_boundary_condition and props.active_boundary_condition != boundary_condition["id"]:
        row.label(text=boundary_condition["type"], icon="CON_TRACKTO")
        row.operator("bim.remove_structural_boundary_condition", text="", icon="X").connection = connection_id
    else:
        row.label(text=boundary_condition["type"], icon="CON_TRACKTO")
        op = row.operator("bim.enable_editing_structural_boundary_condition", text="", icon="GREASEPENCIL")
        op.boundary_condition = boundary_condition["id"]
        row.operator("bim.remove_structural_boundary_condition", text="", icon="X").connection = connection_id

    if props.active_boundary_condition and props.active_boundary_condition == boundary_condition["id"]:
        draw_boundary_condition_editable_ui(layout, props)
    else:
        draw_boundary_condition_read_only_ui(layout, boundary_condition)


def get_unit_symbol_for_measure(measure_class: str) -> str:
    """The project's unit for a measure class such as IfcLinearStiffnessMeasure, or "" if undeclared."""
    special_type = tool.Pset.get_special_type_for_measure_class(measure_class)
    return tool.Pset.get_unit_symbol_for_special_type(special_type, tool.Ifc.get()) if special_type else ""


def draw_boundary_condition_editable_ui(
    layout: bpy.types.UILayout, props: Union[BIMStructuralProperties, BIMObjectStructuralProperties]
) -> None:
    # Reimplement `draw_attributes` as we need to support multiple types for the same attribute.
    for attribute in props.boundary_condition_attributes:
        if attribute.data_type == "string":
            row = layout.row(align=True)
            bonsai.bim.helper.draw_attribute(attribute, row, enable_search=True)
        else:
            split = layout.split(factor=0.55, align=True)
            split.prop(attribute, "enum_value", text=attribute["name"])
            val_row = split.row(align=True)
            if attribute.enum_value == "IfcBoolean":
                val_row.prop(attribute, "bool_value", text="")
            else:
                val_row.prop(attribute, "float_value", text="")
                if unit := get_unit_symbol_for_measure(attribute.enum_value):
                    val_row.label(text=unit)
            if attribute.is_optional:
                val_row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


def draw_boundary_condition_read_only_ui(layout: bpy.types.UILayout, boundary_condition: dict[str, Any]) -> None:
    for attribute in boundary_condition["attributes"]:
        split = layout.split(factor=0.55, align=True)
        split.label(text=attribute["name"])
        val_row = split.row(align=True)
        if attribute["value"] is None:
            val_row.label(text="Unset (Unknown)")
        elif attribute["is_bool"]:
            val_row.label(text="", icon="CHECKBOX_HLT" if attribute["value"] else "CHECKBOX_DEHLT")
        else:
            val_row.label(text=str(attribute["value"]))


class BIM_PT_structural_boundary_conditions(Panel):
    bl_label = "Structural Boundary Conditions"
    bl_idname = "BIM_PT_structural_boundary_conditions"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_object_structural"

    @classmethod
    def poll(cls, context):
        if not (obj := context.active_object):
            return False
        ifc_id = tool.Blender.get_ifc_definition_id(obj)
        if not ifc_id:
            return False
        if not (tool.Ifc.get_object_by_identifier(ifc_id)):
            return False
        if not tool.Ifc.get().by_id(ifc_id).is_a("IfcStructuralConnection"):
            return False
        return True

    def draw(self, context):
        if not StructuralBoundaryConditionsData.is_loaded:
            StructuralBoundaryConditionsData.load()

        obj = context.active_object
        assert obj
        self.props = tool.Structural.get_object_structural_props(obj)

        draw_boundary_condition_ui(
            self.layout,
            StructuralBoundaryConditionsData.data["boundary_condition"],
            StructuralBoundaryConditionsData.data["connection_id"],
            self.props,
        )


class BIM_PT_connected_structural_members(Panel):
    bl_label = "Connected Structural Members"
    bl_idname = "BIM_PT_connected_structural_members"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_object_structural"

    @classmethod
    def poll(cls, context):
        if not (obj := context.active_object):
            return False
        ifc_id = tool.Blender.get_ifc_definition_id(obj)
        if not ifc_id:
            return False
        if not (tool.Ifc.get_object_by_identifier(ifc_id)):
            return False
        if not tool.Ifc.get().by_id(ifc_id).is_a("IfcStructuralConnection"):
            return False
        return True

    def draw(self, context):
        if not ConnectedStructuralMembersData.is_loaded:
            ConnectedStructuralMembersData.load()

        obj = context.active_object
        assert obj
        self.props = tool.Structural.get_object_structural_props(obj)

        row = self.layout.row(align=True)
        row.prop(self.props, "relating_structural_member", text="", icon="CON_TRACKTO")
        row.operator("bim.add_structural_member_connection", text="", icon="ADD")

        for connection in ConnectedStructuralMembersData.data["connections"]:
            row = self.layout.row(align=True)
            row.label(text=f"To Member #{connection['member_name']}")
            if (
                self.props.active_connects_structural_member
                and self.props.active_connects_structural_member == connection["id"]
            ):
                row.operator("bim.disable_editing_structural_connection_condition", text="", icon="CANCEL")
                row.enabled = not connection["is_active_condition"]
                draw_boundary_condition_ui(self.layout.box(), connection["condition"], connection["id"], self.props)
            elif self.props.active_connects_structural_member:
                op = row.operator("bim.remove_structural_connection_condition", text="", icon="X")
                op.connects_structural_member = connection["id"]
            else:
                op = row.operator("bim.enable_editing_structural_connection_condition", text="", icon="GREASEPENCIL")
                op.connects_structural_member = connection["id"]
                op = row.operator("bim.remove_structural_connection_condition", text="", icon="X")
                op.connects_structural_member = connection["id"]


class BIM_PT_structural_member(Panel):
    bl_label = "Structural Member"
    bl_idname = "BIM_PT_structural_member"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_object_structural"

    @classmethod
    def poll(cls, context):
        if not (obj := context.active_object):
            return False
        ifc_id = tool.Blender.get_ifc_definition_id(obj)
        if not ifc_id:
            return False
        if not tool.Ifc.get_object_by_identifier(ifc_id):
            return False
        if not tool.Ifc.get().by_id(ifc_id).is_a("IfcStructuralMember"):
            return False
        return True

    def draw(self, context):
        if not StructuralMemberData.is_loaded:
            StructuralMemberData.load()

        obj = context.active_object
        assert obj
        self.props = tool.Structural.get_object_structural_props(obj)

        if StructuralMemberData.data["active_object_class"] == "IfcStructuralCurveMember":
            if self.props.is_editing_axis:
                row = self.layout.row(align=True)
                row.prop(self.props, "axis_angle")
                row.operator("bim.edit_structural_item_axis", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_structural_item_axis", text="", icon="CANCEL")
            else:
                row = self.layout.row()
                row.operator("bim.enable_editing_structural_item_axis", text="Edit Axis", icon="GREASEPENCIL")
        elif StructuralMemberData.data["active_object_class"] == "IfcStructuralSurfaceMember":
            box = self.layout.box()
            row = box.row(align=True)
            pt = StructuralMemberData.data.get("predefined_type") or "NOTDEFINED"
            row.label(text=f"Type: {pt}", icon="MESH_PLANE")
            row = box.row(align=True)
            thickness = StructuralMemberData.data.get("thickness")
            if thickness is not None:
                unit_symbol = StructuralMemberData.data.get("length_unit") or ""
                suffix = f" {unit_symbol}" if unit_symbol else ""
                row.label(text=f"Thickness: {thickness:g}{suffix}")
            else:
                row.label(text="Thickness: Unset (edit in Attributes)", icon="ERROR")
        else:
            row = self.layout.row()
            row.label(text=StructuralMemberData.data["active_object_class"] or "Structural Member")


def get_load_case_eye(load_case: int) -> str:
    """An open eye for the load case whose loads are shown, closed for the others"""
    props = tool.Structural.get_structural_props()
    shown = props.show_loads and props.load_group_to_show == str(load_case)
    return "HIDE_OFF" if shown else "HIDE_ON"


class BIM_PT_structural_item_models(Panel):
    bl_label = "Analysis Models"
    bl_idname = "BIM_PT_structural_item_models"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_object_structural"

    @classmethod
    def poll(cls, context):
        if not (obj := context.active_object) or not tool.Ifc.get():
            return False
        element = tool.Ifc.get_entity(obj)
        return bool(element and element.is_a("IfcStructuralItem"))

    def draw(self, context):
        if not StructuralAnalysisModelsData.is_loaded:
            StructuralAnalysisModelsData.load()
        data = StructuralAnalysisModelsData.data
        if not data["models"]:
            self.layout.label(text="No analysis models", icon="INFO")
        current = data["current_model"]["id"] if data["current_model"] else None
        for model in data["models"]:
            row = self.layout.row(align=True)
            # Ticking applies to every selected structural item, as the assign operators do.
            if model["id"] in data["active_model_ids"]:
                op = row.operator("bim.unassign_structural_analysis_model", text="", icon="CHECKBOX_HLT", emboss=False)
            else:
                op = row.operator("bim.assign_structural_analysis_model", text="", icon="CHECKBOX_DEHLT", emboss=False)
            op.structural_analysis_model = model["id"]
            row.label(text=model["name"] + (" (current)" if model["id"] == current else ""))


class BIM_PT_structural_item_loads(Panel):
    bl_label = "Applied Loads"
    bl_idname = "BIM_PT_structural_item_loads"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_object_structural"

    @classmethod
    def poll(cls, context):
        if not (obj := context.active_object) or not tool.Ifc.get():
            return False
        element = tool.Ifc.get_entity(obj)
        return bool(element and element.is_a("IfcStructuralItem"))

    def draw_header(self, context):
        self.layout.operator("bim.apply_structural_load", text="", icon="ADD")

    def draw(self, context):
        if not StructuralItemLoadsData.is_loaded:
            StructuralItemLoadsData.load()
        layout = self.layout
        load_cases = StructuralItemLoadsData.data["load_cases"]
        if not load_cases:
            layout.label(text="No loads applied", icon="INFO")
        for load_case in load_cases:
            box = layout.box()
            row = box.row(align=True)
            row.label(text=load_case["name"], icon="CON_CLAMPTO")
            if load_case["resultant"]:
                row.label(text=load_case["resultant"])
            if load_case["id"]:
                row.operator(
                    "bim.show_structural_load_case", text="", icon=get_load_case_eye(load_case["id"]), emboss=False
                ).load_case = load_case["id"]
            for load in load_case["loads"]:
                row = box.row(align=True)
                name = f"{load['group']}: {load['name']}" if load["group"] else load["name"]
                row.label(text=name, icon="FORCE_FORCE")
                row.operator("bim.edit_structural_load_values", text="", icon="GREASEPENCIL").activity = load[
                    "activity"
                ]
                row.operator("bim.remove_structural_activity", text="", icon="X").activity = load["activity"]
        if unloaded := StructuralItemLoadsData.data["unloaded_cases"]:
            layout.label(text=f"No loads in: {', '.join(unloaded)}")


class BIM_PT_structural_connection(Panel):
    bl_label = "Structural Connection"
    bl_idname = "BIM_PT_structural_connection"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_object_structural"

    @classmethod
    def poll(cls, context):
        if not (obj := context.active_object):
            return False
        ifc_id = tool.Blender.get_ifc_definition_id(obj)
        if not ifc_id:
            return False
        if not tool.Ifc.get_object_by_identifier(ifc_id):
            return False
        if not tool.Ifc.get().by_id(ifc_id).is_a("IfcStructuralConnection"):
            return False
        return True

    def draw(self, context):
        if not StructuralConnectionData.is_loaded:
            StructuralConnectionData.load()

        obj = context.active_object
        assert obj
        self.props = tool.Structural.get_object_structural_props(obj)

        if StructuralConnectionData.data["active_object_class"] == "IfcStructuralCurveConnection":
            if self.props.is_editing_axis:
                row = self.layout.row(align=True)
                row.prop(self.props, "axis_angle")
                row.operator("bim.edit_structural_item_axis", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_structural_item_axis", text="", icon="CANCEL")
            else:
                row = self.layout.row()
                row.operator("bim.enable_editing_structural_item_axis", text="Edit Axis", icon="GREASEPENCIL")
        elif StructuralConnectionData.data["active_object_class"] == "IfcStructuralPointConnection":
            if self.props.is_editing_connection_cs:
                row = self.layout.row(align=True)
                row.label(text="Editing Connection CS")
                row.operator("bim.edit_structural_connection_cs", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_structural_connection_cs", text="", icon="CANCEL")
                row = self.layout.row(align=True)
                row.prop(self.props, "ccs_x_angle", text="X Angle")
                row = self.layout.row(align=True)
                row.prop(self.props, "ccs_y_angle", text="Y Angle")
                row = self.layout.row(align=True)
                row.prop(self.props, "ccs_z_angle", text="Z Angle")
            else:
                row = self.layout.row()
                row.operator(
                    "bim.enable_editing_structural_connection_cs", text="Edit Connection CS", icon="GREASEPENCIL"
                )
        else:
            row = self.layout.row()
            row.label(text=StructuralConnectionData.data["active_object_class"] or "Structural Connection")


class BIM_PT_structural_analysis_models(Panel):
    bl_label = "Structural Analysis Models"
    bl_idname = "BIM_PT_structural_analysis_models"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_structural"

    @classmethod
    def poll(cls, context):
        file = tool.Ifc.get()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        if not StructuralAnalysisModelsData.is_loaded:
            StructuralAnalysisModelsData.load()

        self.props = tool.Structural.get_structural_props()

        row = self.layout.row(align=True)
        row.label(
            text=f"{StructuralAnalysisModelsData.data['total_models']} Structural Analysis Models Found",
            icon="MOD_SIMPLIFY",
        )
        if self.props.is_editing:
            row.operator("bim.add_structural_analysis_model", text="", icon="ADD")
            row.operator("bim.disable_structural_analysis_model_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_structural_analysis_models", text="", icon="GREASEPENCIL")

        if current_model := StructuralAnalysisModelsData.data["current_model"]:
            self.layout.label(text=f"Current Model: {current_model['name']}", icon="RADIOBUT_ON")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_structural_analysis_models",
                "",
                self.props,
                "structural_analysis_models",
                self.props,
                "active_structural_analysis_model_index",
            )
            self.draw_served_buildings()

        if self.props.active_structural_analysis_model_id:
            draw_attributes(self.props.structural_analysis_model_attributes, self.layout)

    def draw_served_buildings(self) -> None:
        index = self.props.active_structural_analysis_model_index
        if not 0 <= index < len(self.props.structural_analysis_models):
            return
        model_id = self.props.structural_analysis_models[index].ifc_definition_id
        box = self.layout.box()
        box.label(text="Serves Buildings", icon="HOME")
        for building_id, name in StructuralAnalysisModelsData.data["served_buildings"].get(model_id, []):
            row = box.row(align=True)
            row.label(text=name)
            op = row.operator("bim.unassign_structural_analysis_model_from_building", text="", icon="X")
            op.structural_analysis_model = model_id
            op.building = building_id
        if not StructuralAnalysisModelsData.data["buildings"]:
            box.label(text="No building in the project", icon="INFO")
        elif StructuralAnalysisModelsData.data["unserved_buildings"].get(model_id):
            row = box.row(align=True)
            prop_with_search(row, self.props, "building", text="")
            op = row.operator("bim.assign_structural_analysis_model_to_building", text="", icon="ADD")
            op.structural_analysis_model = model_id


class BIM_UL_structural_analysis_models(UIList):
    def draw_item(
        self,
        context: bpy.types.Context,
        layout: bpy.types.UILayout,
        data: BIMStructuralProperties,
        item: StructuralAnalysisModel,
        icon,
        active_data,
        active_propname,
    ):
        if item:
            row = layout.row(align=True)
            current_model = StructuralAnalysisModelsData.data["current_model"]
            if current_model and current_model["id"] == item.ifc_definition_id:
                row.label(text="", icon="RADIOBUT_ON")
            else:
                op = row.operator(
                    "bim.set_current_structural_analysis_model", text="", icon="RADIOBUT_OFF", emboss=False
                )
                op.structural_analysis_model = item.ifc_definition_id
            row.label(text=item.name)

            if data.active_structural_analysis_model_id == item.ifc_definition_id:
                row.operator("bim.edit_structural_analysis_model", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_structural_analysis_model", text="", icon="CANCEL")
            elif data.active_structural_analysis_model_id:
                op = row.operator("bim.remove_structural_analysis_model", text="", icon="X")
                op.structural_analysis_model = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_structural_analysis_model", text="", icon="GREASEPENCIL")
                op.structural_analysis_model = item.ifc_definition_id
                op = row.operator("bim.remove_structural_analysis_model", text="", icon="X")
                op.structural_analysis_model = item.ifc_definition_id


def draw_apply_load_button(layout: bpy.types.UILayout, props, group_id: int) -> None:
    """The button applying the chosen load to the selected items, saying which, or that none would take it"""
    ifc_file = tool.Ifc.get()
    try:
        load = ifc_file.by_id(int(props.applicable_structural_loads)) if props.applicable_structural_loads else None
        group = ifc_file.by_id(group_id)
    except (RuntimeError, ValueError):
        load, group = None, None
    targets = tool.Structural.get_load_targets(bpy.context.selected_objects, load, group)
    names = [t.Name or "Unnamed" for t in targets]
    if not targets:
        text = "Select items to apply it to"
    elif len(names) <= 3:
        text = f"Apply to {', '.join(names)}"
    else:
        text = f"Apply to {len(names)} items"
    row = layout.row(align=True)
    row.enabled = bool(targets)
    row.operator("bim.add_structural_activity", text=text, icon="ADD").load_group = group_id


class BIM_PT_structural_load_cases(Panel):
    bl_label = "Structural Load Cases"
    bl_idname = "BIM_PT_structural_load_cases"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_structural"

    @classmethod
    def poll(cls, context):
        file = tool.Ifc.get()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        if not StructuralLoadCasesData.is_loaded:
            StructuralLoadCasesData.load()

        self.props = tool.Structural.get_structural_props()

        row = self.layout.row()
        row.operator("bim.add_structural_load_case", icon="ADD")

        for load_case in StructuralLoadCasesData.data["load_cases"]:
            self.draw_load_case_ui(load_case)

    def draw_load_case_ui(self, load_case):
        row = self.layout.row(align=True)
        label_text = load_case["name"]
        if load_case.get("self_weight"):
            sw = load_case["self_weight"]
            label_text += f" (SW: {sw[0]:g}, {sw[1]:g}, {sw[2]:g})"
        row.label(text=label_text, icon="CON_CLAMPTO")
        op = row.operator(
            "bim.show_structural_load_case", text="", icon=get_load_case_eye(load_case["id"]), emboss=False
        )
        op.load_case = load_case["id"]

        if self.props.active_load_case_id and self.props.active_load_case_id == load_case["id"]:
            row.operator("bim.edit_structural_load_case", text="", icon="CHECKMARK")
            row.operator("bim.add_structural_load_group", text="", icon="ADD").load_case = load_case["id"]
            row.operator("bim.disable_editing_structural_load_case", text="", icon="CANCEL")
        elif self.props.active_load_case_id:
            row.operator("bim.remove_structural_load_case", text="", icon="X").load_case = load_case["id"]
        else:
            row.operator("bim.enable_editing_structural_load_case", text="", icon="GREASEPENCIL").load_case = load_case[
                "id"
            ]
            row.operator("bim.remove_structural_load_case", text="", icon="X").load_case = load_case["id"]

        if self.props.active_load_case_id == load_case["id"]:
            self.draw_editable_load_case_ui()
            self.draw_load_case_models_ui(load_case)
            self.draw_editable_load_case_group_ui(load_case)

    def draw_load_case_models_ui(self, load_case):
        box = self.layout.box()
        box.label(text="Analysis Models", icon="MOD_SIMPLIFY")
        for model in StructuralLoadCasesData.data["models"]:
            row = box.row(align=True)
            if model["id"] in load_case["model_ids"]:
                op = row.operator("bim.unassign_structural_load_case", text="", icon="CHECKBOX_HLT", emboss=False)
            else:
                op = row.operator("bim.assign_structural_load_case", text="", icon="CHECKBOX_DEHLT", emboss=False)
            op.load_case = load_case["id"]
            op.structural_analysis_model = model["id"]
            row.label(text=model["name"])

    def draw_load_case_attributes_ui(self, layout):
        draw_attributes(self.props.load_case_attributes, layout)
        box = layout.box()
        box.prop(self.props, "load_case_has_self_weight", text="Self-Weight")
        if self.props.load_case_has_self_weight:
            row = box.row(align=True)
            row.prop(self.props, "load_case_self_weight", text="")
            row.operator("bim.set_self_weight_downwards", text="", icon="LOOP_BACK")

    def draw_editable_load_case_ui(self):
        bonsai.bim.helper.draw_expandable_panel(
            self.layout,
            bpy.context,
            "Attributes",
            lambda layout, context: self.draw_load_case_attributes_ui(layout),
            panel_id="structural_load_case_attributes",
        )

    def draw_editable_load_case_group_ui(self, load_case):
        box = self.layout.box()
        box.label(text="Applied Loads", icon="FORCE_FORCE")
        # Listed by item, each item's in the order they are drawn tip to tail.
        for item, activities in itertools.groupby(load_case["activities"], key=lambda activity: activity["item"]):
            activities = list(activities)
            if len(activities) > 1:
                box.row(align=True).label(text=activities[0]["item_name"], icon="FORCE_FORCE")
            for activity in activities:
                row = box.row(align=True)
                row.label(text=activity["name"])
                row.operator("bim.edit_structural_load_values", text="", icon="GREASEPENCIL").activity = activity["id"]
                row.operator("bim.remove_structural_activity", text="", icon="X").activity = activity["id"]
        row = box.row(align=True)
        row.prop(self.props, "applicable_structural_load_types", text="")
        row.prop(self.props, "applicable_structural_loads", text="")
        draw_apply_load_button(box, self.props, load_case["id"])

        if not load_case["load_groups"]:
            row = box.row(align=True)
            row.label(text="No Load Groups Found")
        for load_group in load_case["load_groups"]:
            row = box.row(align=True)
            row.label(text=load_group["name"], icon="OUTLINER_COLLECTION")
            op = row.operator("bim.enable_editing_structural_load_group_activities", text="", icon="FORCE_FORCE")
            op.load_group = load_group["id"]
            row.operator("bim.remove_structural_load_group", text="", icon="X").load_group = load_group["id"]

            if self.props.active_load_group_id == load_group["id"]:
                if self.props.load_group_editing_type == "ACTIVITY":
                    self.draw_editable_load_group_activities_ui(box, load_group)

    def draw_editable_load_group_activities_ui(self, layout, load_group):
        row = layout.row(align=True)
        row.prop(self.props, "applicable_structural_load_types", text="")
        row.prop(self.props, "applicable_structural_loads", text="")
        draw_apply_load_button(layout, self.props, load_group["id"])
        layout.template_list(
            "BIM_UL_structural_activities",
            "",
            self.props,
            "load_group_activities",
            self.props,
            "active_load_group_activity_index",
        )


class BIM_PT_structural_load_combinations(Panel):
    bl_label = "Structural Load Combinations"
    bl_idname = "BIM_PT_structural_load_combinations"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_structural"

    @classmethod
    def poll(cls, context):
        file = tool.Ifc.get()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        if not StructuralLoadCombinationsData.is_loaded:
            StructuralLoadCombinationsData.load()
        if not StructuralLoadCasesData.is_loaded:
            StructuralLoadCasesData.load()

        self.props = tool.Structural.get_structural_props()

        row = self.layout.row()
        row.operator("bim.add_structural_load_combination", icon="ADD")

        for combination in StructuralLoadCombinationsData.data["load_combinations"]:
            self.draw_combination_ui(combination)

    def draw_combination_ui(self, combination: dict[str, Any]) -> None:
        row = self.layout.row(align=True)
        text = combination["name"]
        if combination["purpose"]:
            text += f" ({combination['purpose']})"
        # An empty combination has nothing to add up, and analysis programs refuse it.
        row.label(text=text, icon="ERROR" if not combination["total_load_cases"] else "MOD_ARRAY")
        op = row.operator(
            "bim.show_structural_load_case", text="", icon=get_load_case_eye(combination["id"]), emboss=False
        )
        op.load_case = combination["id"]

        active_id = self.props.active_load_combination_id
        if active_id == combination["id"]:
            row.operator("bim.edit_structural_load_combination", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_structural_load_combination", text="", icon="CANCEL")
        else:
            if not active_id:
                op = row.operator("bim.enable_editing_structural_load_combination", text="", icon="GREASEPENCIL")
                op.load_combination = combination["id"]
            op = row.operator("bim.remove_structural_load_combination", text="", icon="X")
            op.load_combination = combination["id"]

        if active_id == combination["id"]:
            draw_attributes(self.props.load_combination_attributes, self.layout)
            self.draw_factors_ui()
            self.draw_models_ui(combination)

    def draw_factors_ui(self) -> None:
        box = self.layout.box()
        box.label(text="Load Cases and Factors", icon="CON_CLAMPTO")
        if not self.props.load_combination_factors:
            box.label(text="No Load Cases Found")
        for factor in self.props.load_combination_factors:
            row = box.row(align=True)
            row.prop(factor, "is_included", text=factor.name)
            sub = row.row(align=True)
            sub.enabled = factor.is_included
            sub.prop(factor, "factor", text="")

    def draw_models_ui(self, combination: dict[str, Any]) -> None:
        box = self.layout.box()
        box.label(text="Analysis Models", icon="MOD_SIMPLIFY")
        for model in StructuralLoadCasesData.data["models"]:
            row = box.row(align=True)
            if model["id"] in combination["model_ids"]:
                op = row.operator("bim.unassign_structural_load_case", text="", icon="CHECKBOX_HLT", emboss=False)
            else:
                op = row.operator("bim.assign_structural_load_case", text="", icon="CHECKBOX_DEHLT", emboss=False)
            op.load_case = combination["id"]
            op.structural_analysis_model = model["id"]
            row.label(text=model["name"])


class BIM_UL_structural_activities(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: BIMStructuralProperties,
        item: StructuralActivity,
        icon,
        active_data,
        active_propname,
    ):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
            row.label(text=item.applied_load_class)
            row.operator(
                "bim.edit_structural_load_values", text="", icon="GREASEPENCIL"
            ).activity = item.ifc_definition_id
            op = row.operator("bim.remove_structural_activity", text="", icon="X")
            op.activity = item.ifc_definition_id


class BIM_PT_show_structural_activities(Panel):
    bl_label = "Show Loads"
    bl_idname = "BIM_PT_show_structural_activities"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_structural"

    @classmethod
    def poll(cls, context):
        file = tool.Ifc.get()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        self.props = tool.Structural.get_structural_props()

        row = self.layout.row(align=True)
        # The same setting as in the viewport's overlays.
        row.prop(self.props, "show_loads", text="Show Loads", icon="HIDE_OFF")
        row = self.layout.row(align=True)
        row.prop(self.props, "reference_frame")
        row = self.layout.row(align=True)
        row.prop(self.props, "activity_type")
        row = self.layout.row(align=True)
        row.prop(self.props, "load_group_to_show")
        row = self.layout.row(align=True)
        row.prop(self.props, "force_display")
        row = self.layout.row(align=True)
        row.prop(self.props, "force_scale")
        row.prop(self.props, "show_force_angles")
        if self.props.show_force_angles:
            row = self.layout.row(align=True)
            row.prop(self.props, "angle_reference")
        row = self.layout.row(align=True)
        row.prop(self.props, "force_decimals")
        row.prop(self.props, "angle_decimals")


class BIM_PT_structural_loads(Panel):
    bl_label = "Load Definitions"
    bl_description = "Load values that applied loads use. One definition can be shared by several applied loads"
    bl_idname = "BIM_PT_structural_loads"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_structural"

    @classmethod
    def poll(cls, context):
        file = tool.Ifc.get()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        if not StructuralLoadsData.is_loaded:
            StructuralLoadsData.load()

        self.props = tool.Structural.get_structural_props()

        row = self.layout.row(align=True)
        row.label(text=f"{StructuralLoadsData.data['total_loads']} Load Definitions", icon="ANIM_DATA")
        if self.props.is_editing_loads:
            row.operator(
                "bim.toggle_filter_structural_loads",
                text="FILTER - OFF" if not self.props.filtered_structural_loads else "FILTER - ON",
                icon="FILTER",
            )
            row.operator("bim.disable_structural_load_editing_ui", text="", icon="CANCEL")

            row = self.layout.row(align=True)
            prop_with_search(row, self.props, "structural_load_types", text="")
            row.operator("bim.add_structural_load", text="", icon="ADD").ifc_class = self.props.structural_load_types
        else:
            row.operator("bim.load_structural_loads", text="", icon="GREASEPENCIL")

        if self.props.is_editing_loads:
            self.layout.template_list(
                "BIM_UL_structural_loads",
                "",
                self.props,
                "structural_loads",
                self.props,
                "active_structural_load_index",
            )
            self.layout.prop(self.props, "show_unused_loads_only")

        if self.props.active_structural_load_id:
            bonsai.bim.helper.draw_attributes(self.props.structural_load_attributes, self.layout)


class BIM_UL_structural_loads(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: BIMStructuralProperties,
        item: StructuralLoad,
        icon,
        active_data,
        active_propname,
    ):
        if item:
            row = layout.row(align=True)
            row.label(text=f"{item.name} ({item.number_of_inverse_references})")
            row.label(text=StructuralLoadsData.data["load_classes"][item.ifc_definition_id])

            if data.active_structural_load_id == item.ifc_definition_id:
                row.operator("bim.edit_structural_load", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_structural_load", text="", icon="CANCEL")
            elif data.active_structural_load_id:
                op = row.operator("bim.remove_structural_load", text="", icon="X")
                op.structural_load = item.ifc_definition_id
            else:
                op = row.operator("bim.edit_structural_load_values", text="", icon="GREASEPENCIL")
                op.structural_load = item.ifc_definition_id
                op = row.operator("bim.remove_structural_load", text="", icon="X")
                op.structural_load = item.ifc_definition_id


class BIM_PT_boundary_conditions(Panel):
    bl_label = "Boundary Conditions"
    bl_idname = "BIM_PT_boundary_conditions"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_structural"

    @classmethod
    def poll(cls, context):
        file = tool.Ifc.get()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        if not BoundaryConditionsData.is_loaded:
            BoundaryConditionsData.load()

        self.props = tool.Structural.get_structural_props()
        assert self.layout

        row = self.layout.row(align=True)
        row.label(
            text=f"{BoundaryConditionsData.data['total_conditions']} Boundary Conditions Found", icon="CON_TRACKTO"
        )
        if self.props.is_editing_boundary_conditions:
            row.operator(
                "bim.toggle_filter_boundary_conditions",
                text="FILTER - OFF" if not self.props.filtered_boundary_conditions else "FILTER - ON",
                icon="FILTER",
            )
            row.operator("bim.disable_boundary_condition_editing_ui", text="", icon="CANCEL")

            row = self.layout.row(align=True)
            prop_with_search(row, self.props, "boundary_condition_types", text="")
            row.operator(
                "bim.add_boundary_condition", text="", icon="ADD"
            ).ifc_class = self.props.boundary_condition_types
        else:
            row.operator("bim.load_boundary_conditions", text="", icon="GREASEPENCIL")

        if self.props.is_editing_boundary_conditions:
            self.layout.template_list(
                "BIM_UL_boundary_conditions",
                "",
                self.props,
                "boundary_conditions",
                self.props,
                "active_boundary_condition_index",
            )

            if self.props.active_boundary_condition_id:
                draw_boundary_condition_editable_ui(self.layout, self.props)


class BIM_UL_boundary_conditions(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: BIMStructuralProperties,
        item: BoundaryCondition,
        icon,
        active_data,
        active_propname,
    ):
        if item:
            row = layout.row(align=True)
            row.label(text=f"{item.name} ({item.number_of_inverse_references})")
            row.label(text=BoundaryConditionsData.data["condition_classes"][item.ifc_definition_id])

            if data.active_boundary_condition_id == item.ifc_definition_id:
                row.operator("bim.edit_boundary_condition", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_boundary_condition", text="", icon="CANCEL")
            elif data.active_boundary_condition_id:
                op = row.operator("bim.remove_boundary_condition", text="", icon="X")
                op.boundary_condition = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_boundary_condition", text="", icon="GREASEPENCIL")
                op.boundary_condition = item.ifc_definition_id
                op = row.operator("bim.remove_boundary_condition", text="", icon="X")
                op.boundary_condition = item.ifc_definition_id
