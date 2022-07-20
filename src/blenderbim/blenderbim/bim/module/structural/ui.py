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

import bpy
import blenderbim.bim.helper
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.helper import draw_attributes, prop_with_search
from ifcopenshell.api.structural.data import Data
from blenderbim.bim.module.structural.data import StructuralData


def draw_boundary_condition_ui(layout, boundary_condition_id, connection_id, props):
    data = (
        Data.boundary_conditions[boundary_condition_id]
        if boundary_condition_id and boundary_condition_id in Data.boundary_conditions.keys()
        else {}
    )
    row = layout.row(align=True)
    if not data:
        row.label(text="No Boundary Condition Found", icon="CON_TRACKTO")
        row.operator("bim.add_structural_boundary_condition", text="", icon="ADD").connection = connection_id
        return

    if props.active_boundary_condition and props.active_boundary_condition == boundary_condition_id:
        row.label(text=data["type"], icon="CON_TRACKTO")
        row.operator("bim.edit_structural_boundary_condition", text="", icon="CHECKMARK").connection = connection_id
        row.operator("bim.disable_editing_structural_boundary_condition", text="", icon="CANCEL")
    elif props.active_boundary_condition and props.active_boundary_condition != boundary_condition_id:
        row.label(text=data["type"], icon="CON_TRACKTO")
        row.operator("bim.remove_structural_boundary_condition", text="", icon="X").connection = connection_id
    else:
        row.label(text=data["type"], icon="CON_TRACKTO")
        op = row.operator("bim.enable_editing_structural_boundary_condition", text="", icon="GREASEPENCIL")
        op.boundary_condition = data["id"]
        row.operator("bim.remove_structural_boundary_condition", text="", icon="X").connection = connection_id

    if props.active_boundary_condition and props.active_boundary_condition == boundary_condition_id:
        draw_boundary_condition_editable_ui(layout, props)
    else:
        draw_boundary_condition_read_only_ui(layout, data)


def draw_boundary_condition_editable_ui(layout, props):
    for attribute in props.boundary_condition_attributes:
        if attribute.data_type == "string":
            row = layout.row()
            row.prop(attribute, "string_value", text=attribute["name"])
        else:
            row = layout.row(align=True)
            row.prop(attribute, "enum_value", text=attribute["name"])
            if attribute.enum_value == "IfcBoolean":
                row.prop(attribute, "bool_value", text="")
            else:
                row.prop(attribute, "float_value", text="")
        if attribute.is_optional:
            row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


def draw_boundary_condition_read_only_ui(layout, boundary_condition_data):
    for key, value in boundary_condition_data.items():
        if key == "id" or key == "type" or value == None:
            continue
        row = layout.row(align=True)
        row.label(text=key)
        if isinstance(value, bool):
            row.label(text="", icon="CHECKBOX_HLT" if value else "CHECKBOX_DEHLT")
        else:
            row.label(text=str(value))


class BIM_PT_structural_boundary_conditions(Panel):
    bl_label = "IFC Structural Boundary Conditions"
    bl_idname = "BIM_PT_structural_boundary_conditions"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    # bl_parent_id = "BIM_PT_structural_connection"
    bl_parent_id = "BIM_PT_misc_object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        if not IfcStore.get_file().by_id(props.ifc_definition_id).is_a("IfcStructuralConnection"):
            return False
        return True

    def draw(self, context):
        self.oprops = context.active_object.BIMObjectProperties
        self.props = context.active_object.BIMStructuralProperties
        if self.oprops.ifc_definition_id not in Data.connections:
            Data.load(IfcStore.get_file(), self.oprops.ifc_definition_id)

        applied_condition_id = Data.connections[self.oprops.ifc_definition_id]["AppliedCondition"]
        draw_boundary_condition_ui(self.layout, applied_condition_id, self.oprops.ifc_definition_id, self.props)


class BIM_PT_connected_structural_members(Panel):
    bl_label = "IFC Connected Structural Members"
    bl_idname = "BIM_PT_connected_structural_members"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    # bl_parent_id = "BIM_PT_structural_connection"
    bl_parent_id = "BIM_PT_misc_object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        if not IfcStore.get_file().by_id(props.ifc_definition_id).is_a("IfcStructuralConnection"):
            return False
        return True

    def draw(self, context):
        self.oprops = context.active_object.BIMObjectProperties
        self.props = context.active_object.BIMStructuralProperties
        if self.oprops.ifc_definition_id not in Data.connections:
            Data.load(IfcStore.get_file(), self.oprops.ifc_definition_id)

        rel_ids = Data.connections[self.oprops.ifc_definition_id]["ConnectsStructuralMembers"]

        row = self.layout.row(align=True)
        row.prop(self.props, "relating_structural_member", text="", icon="CON_TRACKTO")
        row.operator("bim.add_structural_member_connection", text="", icon="ADD")

        for rel_id in rel_ids:
            rel = Data.connects_structural_members[rel_id]
            row = self.layout.row(align=True)
            row.label(text=f"To Member #{IfcStore.get_file().by_id(rel['RelatingStructuralMember']).Name}")
            if self.props.active_connects_structural_member and self.props.active_connects_structural_member == rel_id:
                row.operator("bim.disable_editing_structural_connection_condition", text="", icon="CANCEL")
                row.enabled = self.props.active_boundary_condition != rel["AppliedCondition"]
                self.draw_editable_ui(context, self.layout, rel)
            elif self.props.active_connects_structural_member:
                op = row.operator("bim.remove_structural_connection_condition", text="", icon="X")
                op.connects_structural_member = rel_id
            else:
                op = row.operator("bim.enable_editing_structural_connection_condition", text="", icon="GREASEPENCIL")
                op.connects_structural_member = rel_id
                op = row.operator("bim.remove_structural_connection_condition", text="", icon="X")
                op.connects_structural_member = rel_id

    def draw_editable_ui(self, context, layout, data):
        box = layout.box()
        row = box.row(align=True)
        draw_boundary_condition_ui(box, data["AppliedCondition"], data["id"], self.props)


class BIM_PT_structural_member(Panel):
    bl_label = "IFC Structural Member"
    bl_idname = "BIM_PT_structural_member"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_misc_object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        if not IfcStore.get_file().by_id(props.ifc_definition_id).is_a("IfcStructuralMember"):
            return False
        return True

    def draw(self, context):
        self.oprops = context.active_object.BIMObjectProperties
        self.props = context.active_object.BIMStructuralProperties
        self.file = IfcStore.get_file()

        if self.file.by_id(self.oprops.ifc_definition_id).is_a("IfcStructuralCurveMember"):
            if self.props.is_editing_axis:
                row = self.layout.row(align=True)
                row.prop(self.props, "axis_angle")
                row.operator("bim.edit_structural_item_axis", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_structural_item_axis", text="", icon="CANCEL")
            else:
                row = self.layout.row()
                row.operator("bim.enable_editing_structural_item_axis", text="Edit Axis", icon="GREASEPENCIL")
        else:
            row = self.layout.row()
            row.label(text="TODO")


class BIM_PT_structural_connection(Panel):
    bl_label = "IFC Structural Connection"
    bl_idname = "BIM_PT_structural_connection"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_misc_object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if not IfcStore.get_element(props.ifc_definition_id):
            return False
        if not IfcStore.get_file().by_id(props.ifc_definition_id).is_a("IfcStructuralConnection"):
            return False
        return True

    def draw(self, context):
        self.oprops = context.active_object.BIMObjectProperties
        self.props = context.active_object.BIMStructuralProperties
        self.file = IfcStore.get_file()

        if self.file.by_id(self.oprops.ifc_definition_id).is_a("IfcStructuralCurveConnection"):
            if self.props.is_editing_axis:
                row = self.layout.row(align=True)
                row.prop(self.props, "axis_angle")
                row.operator("bim.edit_structural_item_axis", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_structural_item_axis", text="", icon="CANCEL")
            else:
                row = self.layout.row()
                row.operator("bim.enable_editing_structural_item_axis", text="Edit Axis", icon="GREASEPENCIL")

        elif self.file.by_id(self.oprops.ifc_definition_id).is_a("IfcStructuralPointConnection"):
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
            row.label(text="TODO")


class BIM_PT_structural_analysis_models(Panel):
    bl_label = "IFC Structural Analysis Models"
    bl_idname = "BIM_PT_structural_analysis_models"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_structural"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        if not StructuralData.is_loaded:
            StructuralData.load()
        self.props = context.scene.BIMStructuralProperties

        row = self.layout.row(align=True)
        row.label(
            text="{} Structural Analysis Models Found".format(StructuralData.number_of_structural_analysis_models),
            icon="MOD_SIMPLIFY",
        )
        if self.props.is_editing:
            row.operator("bim.add_structural_analysis_model", text="", icon="ADD")
            row.operator("bim.disable_structural_analysis_model_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_structural_analysis_models", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_structural_analysis_models",
                "",
                self.props,
                "structural_analysis_models",
                self.props,
                "active_structural_analysis_model_index",
            )

        if self.props.active_structural_analysis_model_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        draw_attributes(self.props.structural_analysis_model_attributes, self.layout)


class BIM_UL_structural_analysis_models(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)

            if context.active_object:
                oprops = context.active_object.BIMObjectProperties
                if (
                    oprops.ifc_definition_id in StructuralData.products
                    and item.ifc_definition_id in StructuralData.products[oprops.ifc_definition_id]
                ):
                    op = row.operator(
                        "bim.unassign_structural_analysis_model", text="", icon="KEYFRAME_HLT", emboss=False
                    )
                    op.structural_analysis_model = item.ifc_definition_id
                else:
                    op = row.operator("bim.assign_structural_analysis_model", text="", icon="KEYFRAME", emboss=False)
                    op.structural_analysis_model = item.ifc_definition_id

            if context.scene.BIMStructuralProperties.active_structural_analysis_model_id == item.ifc_definition_id:
                row.operator("bim.edit_structural_analysis_model", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_structural_analysis_model", text="", icon="CANCEL")
            elif context.scene.BIMStructuralProperties.active_structural_analysis_model_id:
                op = row.operator("bim.remove_structural_analysis_model", text="", icon="X")
                op.structural_analysis_model = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_structural_analysis_model", text="", icon="GREASEPENCIL")
                op.structural_analysis_model = item.ifc_definition_id
                op = row.operator("bim.remove_structural_analysis_model", text="", icon="X")
                op.structural_analysis_model = item.ifc_definition_id


class BIM_PT_structural_load_cases(Panel):
    bl_label = "IFC Structural Load Cases"
    bl_idname = "BIM_PT_structural_load_cases"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_structural"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        self.props = context.scene.BIMStructuralProperties

        if not Data.is_loaded:
            Data.load(IfcStore.get_file())

        row = self.layout.row()
        row.operator("bim.add_structural_load_case", icon="ADD")

        for load_case_id, load_case in Data.load_cases.items():
            self.draw_load_case_ui(load_case_id, load_case)

    def draw_load_case_ui(self, load_case_id, load_case):
        row = self.layout.row(align=True)
        row.label(text=load_case["Name"] or "Unnamed", icon="CON_CLAMPTO")

        if self.props.active_load_case_id and self.props.active_load_case_id == load_case_id:
            if self.props.load_case_editing_type == "ATTRIBUTES":
                row.operator("bim.edit_structural_load_case", text="", icon="CHECKMARK")
            elif self.props.load_case_editing_type == "GROUPS":
                row.operator("bim.add_structural_load_group", text="", icon="ADD").load_case = load_case_id
            row.operator("bim.disable_editing_structural_load_case", text="", icon="CANCEL")
        elif self.props.active_load_case_id:
            row.operator("bim.remove_structural_load_case", text="", icon="X").load_case = load_case_id
        else:
            row.operator(
                "bim.enable_editing_structural_load_case_groups", text="", icon="GHOST_ENABLED"
            ).load_case = load_case_id
            row.operator(
                "bim.enable_editing_structural_load_case", text="", icon="GREASEPENCIL"
            ).load_case = load_case_id
            row.operator("bim.remove_structural_load_case", text="", icon="X").load_case = load_case_id

        if self.props.active_load_case_id == load_case_id:
            if self.props.load_case_editing_type == "ATTRIBUTES":
                self.draw_editable_load_case_ui()
            elif self.props.load_case_editing_type == "GROUPS":
                self.draw_editable_load_case_group_ui(load_case)

    def draw_editable_load_case_ui(self):
        draw_attributes(self.props.load_case_attributes, self.layout)

    def draw_editable_load_case_group_ui(self, load_case):
        box = self.layout.box()
        if not len(load_case["IsGroupedBy"]):
            row = box.row(align=True)
            row.label(text="No Load Groups Found")
        for load_group_id in load_case["IsGroupedBy"]:
            load_group = Data.load_groups[load_group_id]
            row = box.row(align=True)
            row.label(text=load_group["Name"] or "Unnamed", icon="GHOST_ENABLED")
            op = row.operator("bim.enable_editing_structural_load_group_activities", text="", icon="GHOST_ENABLED")
            op.load_group = load_group_id
            row.operator("bim.remove_structural_load_group", text="", icon="X").load_group = load_group_id

            if self.props.active_load_group_id == load_group_id:
                if self.props.load_group_editing_type == "ACTIVITY":
                    self.draw_editable_load_group_activities_ui(box, load_group)

    def draw_editable_load_group_activities_ui(self, layout, load_group):
        row = layout.row(align=True)
        row.prop(self.props, "applicable_structural_load_types", text="")
        row.prop(self.props, "applicable_structural_loads", text="")
        op = row.operator("bim.add_structural_activity", text="", icon="ADD")
        op.load_group = load_group["id"]
        layout.template_list(
            "BIM_UL_structural_activities",
            "",
            self.props,
            "load_group_activities",
            self.props,
            "active_load_group_activity_index",
        )


class BIM_UL_structural_activities(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
            row.label(text=item.applied_load_class)


class BIM_PT_structural_loads(Panel):
    bl_label = "IFC Structural Loads"
    bl_idname = "BIM_PT_structural_loads"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_structural"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        self.props = context.scene.BIMStructuralProperties

        row = self.layout.row(align=True)
        row.label(text="{} Structural Loads Found".format(len(Data.structural_loads)), icon="ANIM_DATA")
        if self.props.is_editing_loads:
            row.operator(
                "bim.toggle_filter_structural_loads",
                text="FILTER - OFF" if not self.props.filtered_structural_loads else "FILTER - ON",
                icon="FILTER",
            )
            row.operator("bim.disable_structural_load_editing_ui", text="", icon="SCREEN_BACK")

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

        if self.props.active_structural_load_id:
            blenderbim.bim.helper.draw_attributes(self.props.structural_load_attributes, self.layout)


class BIM_UL_structural_loads(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=f"{item.name} ({item.number_of_inverse_references})")
            row.label(text=Data.structural_loads[item.ifc_definition_id]["type"])

            if context.scene.BIMStructuralProperties.active_structural_load_id == item.ifc_definition_id:
                row.operator("bim.edit_structural_load", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_structural_load", text="", icon="CANCEL")
            elif context.scene.BIMStructuralProperties.active_structural_load_id:
                op = row.operator("bim.remove_structural_load", text="", icon="X")
                op.structural_load = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_structural_load", text="", icon="GREASEPENCIL")
                op.structural_load = item.ifc_definition_id
                op = row.operator("bim.remove_structural_load", text="", icon="X")
                op.structural_load = item.ifc_definition_id


class BIM_PT_boundary_conditions(Panel):
    bl_label = "IFC Boundary Conditions"
    bl_idname = "BIM_PT_boundary_conditions"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_structural"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        self.props = context.scene.BIMStructuralProperties

        row = self.layout.row(align=True)
        row.label(text="{} Boundary Conditions Found".format(len(Data.boundary_conditions)), icon="CON_TRACKTO")
        if self.props.is_editing_boundary_conditions:
            row.operator(
                "bim.toggle_filter_boundary_conditions",
                text="FILTER - OFF" if not self.props.filtered_boundary_conditions else "FILTER - ON",
                icon="FILTER",
            )
            row.operator("bim.disable_boundary_condition_editing_ui", text="", icon="SCREEN_BACK")

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
            # blenderbim.bim.helper.draw_attributes(self.props.boundary_condition_attributes, self.layout)


class BIM_UL_boundary_conditions(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=f"{item.name} ({item.number_of_inverse_references})")
            row.label(text=Data.boundary_conditions[item.ifc_definition_id]["type"])

            if context.scene.BIMStructuralProperties.active_boundary_condition_id == item.ifc_definition_id:
                row.operator("bim.edit_boundary_condition", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_boundary_condition", text="", icon="CANCEL")
            elif context.scene.BIMStructuralProperties.active_boundary_condition_id:
                op = row.operator("bim.remove_boundary_condition", text="", icon="X")
                op.boundary_condition = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_boundary_condition", text="", icon="GREASEPENCIL")
                op.boundary_condition = item.ifc_definition_id
                op = row.operator("bim.remove_boundary_condition", text="", icon="X")
                op.boundary_condition = item.ifc_definition_id
