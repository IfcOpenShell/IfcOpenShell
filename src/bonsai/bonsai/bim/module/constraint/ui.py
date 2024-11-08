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

from bpy.types import Panel, UIList
from bonsai.bim.ifc import IfcStore
from bonsai.bim.helper import draw_attributes
from bonsai.bim.module.constraint.data import ConstraintsData, ObjectConstraintsData


class BIM_PT_constraints(Panel):
    bl_label = "Constraints"
    bl_idname = "BIM_PT_constraints"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_project_setup"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not ConstraintsData.is_loaded:
            ConstraintsData.load()

        self.props = context.scene.BIMConstraintProperties

        if not self.props.is_editing or self.props.is_editing == "IfcObjective":
            row = self.layout.row(align=True)
            row.label(text=f"{ConstraintsData.data['total_objectives']} Objectives Found", icon="LIGHT")
            if self.props.is_editing == "IfcObjective":
                row.operator("bim.disable_constraint_editing_ui", text="", icon="CHECKMARK")
                row.operator("bim.add_objective", text="", icon="ADD")
            else:
                row.operator("bim.load_objectives", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_constraints",
                "",
                self.props,
                "constraints",
                self.props,
                "active_constraint_index",
            )

        if self.props.active_constraint_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        draw_attributes(self.props.constraint_attributes, self.layout)


class BIM_PT_object_constraints(Panel):
    bl_label = "Constraints"
    bl_idname = "BIM_PT_object_constraints"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_misc"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        if not IfcStore.get_element(context.active_object.BIMObjectProperties.ifc_definition_id):
            return False
        return bool(context.active_object.BIMObjectProperties.ifc_definition_id)

    def draw(self, context):
        if not ObjectConstraintsData.is_loaded:
            ObjectConstraintsData.load()

        obj = context.active_object
        self.oprops = obj.BIMObjectProperties
        self.sprops = context.scene.BIMConstraintProperties
        self.props = obj.BIMObjectConstraintProperties
        self.file = IfcStore.get_file()

        self.draw_add_ui()

        if not ObjectConstraintsData.data["constraints"]:
            row = self.layout.row(align=True)
            row.label(text="No Constraints", icon="LIGHT")

        for constraint in ObjectConstraintsData.data["constraints"]:
            if constraint["type"] == "IfcObjective":
                icon = "LIGHT"
            else:
                continue  # Metric not implemented
            row = self.layout.row(align=True)
            row.label(text=constraint["name"])
            row.operator("bim.unassign_constraint", text="", icon="X").constraint = constraint["id"]

    def draw_add_ui(self):
        if self.props.is_adding:
            row = self.layout.row(align=True)
            icon = "LIGHT" if self.props.is_adding == "IfcObjective" else "FILE_HIDDEN"
            row.label(text="Adding {}".format(self.props.is_adding), icon=icon)
            row.operator("bim.disable_assigning_constraint", text="", icon="CANCEL")
            self.layout.template_list(
                "BIM_UL_object_constraints",
                "",
                self.sprops,
                "constraints",
                self.sprops,
                "active_constraint_index",
            )
        else:
            row = self.layout.row(align=True)
            row.prop(self.props, "available_constraint_types", text="")
            row.operator("bim.enable_assigning_constraint", text="", icon="ADD")


class BIM_UL_constraints(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
            if context.scene.BIMConstraintProperties.active_constraint_id == item.ifc_definition_id:
                if context.scene.BIMConstraintProperties.is_editing == "IfcObjective":
                    row.operator("bim.edit_objective", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_constraint", text="", icon="CANCEL")
            elif context.scene.BIMConstraintProperties.active_constraint_id:
                row.operator("bim.remove_constraint", text="", icon="X").constraint = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_constraint", text="", icon="GREASEPENCIL")
                op.constraint = item.ifc_definition_id
                row.operator("bim.remove_constraint", text="", icon="X").constraint = item.ifc_definition_id


class BIM_UL_object_constraints(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
            row.operator("bim.assign_constraint", text="", icon="ADD").constraint = item.ifc_definition_id
