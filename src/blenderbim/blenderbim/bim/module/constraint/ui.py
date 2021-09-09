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

from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.helper import draw_attributes
from ifcopenshell.api.constraint.data import Data


class BIM_PT_constraints(Panel):
    bl_label = "IFC Constraints"
    bl_idname = "BIM_PT_constraints"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())

        self.props = context.scene.BIMConstraintProperties

        if not self.props.is_editing or self.props.is_editing == "IfcObjective":
            row = self.layout.row(align=True)
            row.label(text="{} Objectives Found".format(len(Data.objectives)), icon="LIGHT")
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
    bl_label = "IFC Constraints"
    bl_idname = "BIM_PT_object_constraints"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if not IfcStore.get_element(context.active_object.BIMObjectProperties.ifc_definition_id):
            return False
        return bool(context.active_object.BIMObjectProperties.ifc_definition_id)

    def draw(self, context):
        obj = context.active_object
        self.oprops = obj.BIMObjectProperties
        self.sprops = context.scene.BIMConstraintProperties
        self.props = obj.BIMObjectConstraintProperties
        self.file = IfcStore.get_file()
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        if self.oprops.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), self.oprops.ifc_definition_id)

        self.draw_add_ui()

        constraint_ids = Data.products[self.oprops.ifc_definition_id]

        if not constraint_ids:
            row = self.layout.row(align=True)
            row.label(text="No Constraints", icon="LIGHT")

        for constraint_id in constraint_ids:
            try:
                constraint = Data.objectives[constraint_id]
                icon = "LIGHT"
            except:
                pass  # Metric not implemented
            row = self.layout.row(align=True)
            row.label(text=constraint.get("Name") or "Unnamed")
            row.operator("bim.unassign_constraint", text="", icon="X").constraint = constraint_id

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
