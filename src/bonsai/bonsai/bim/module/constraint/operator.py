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
import json
import ifcopenshell.api
import ifcopenshell.util.attribute
import bonsai.bim.helper
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore


class LoadObjectives(bpy.types.Operator):
    bl_idname = "bim.load_objectives"
    bl_label = "Load Objectives"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMConstraintProperties
        props.constraints.clear()
        for constraint in tool.Ifc.get().by_type("IfcObjective"):
            new = props.constraints.add()
            new.name = constraint.Name or "Unnamed"
            new.ifc_definition_id = constraint.id()
        props.is_editing = "IfcObjective"
        bpy.ops.bim.disable_editing_constraint()
        return {"FINISHED"}


class DisableConstraintEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_constraint_editing_ui"
    bl_label = "Disable Constraint Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMConstraintProperties.is_editing = ""
        bpy.ops.bim.disable_editing_constraint()
        return {"FINISHED"}


class EnableEditingConstraint(bpy.types.Operator):
    bl_idname = "bim.enable_editing_constraint"
    bl_label = "Enable Editing Constraint"
    bl_options = {"REGISTER", "UNDO"}
    constraint: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMConstraintProperties
        props.constraint_attributes.clear()
        bonsai.bim.helper.import_attributes2(tool.Ifc.get().by_id(self.constraint), props.constraint_attributes)
        props.active_constraint_id = self.constraint
        return {"FINISHED"}


class DisableEditingConstraint(bpy.types.Operator):
    bl_idname = "bim.disable_editing_constraint"
    bl_label = "Disable Editing Constraint"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMConstraintProperties.active_constraint_id = 0
        return {"FINISHED"}


class AddObjective(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_objective"
    bl_label = "Add Objective"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        result = ifcopenshell.api.run("constraint.add_objective", IfcStore.get_file())
        bpy.ops.bim.load_objectives()
        bpy.ops.bim.enable_editing_constraint(constraint=result.id())
        return {"FINISHED"}


class EditObjective(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_objective"
    bl_label = "Edit Objective"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMConstraintProperties
        attributes = {}
        for attribute in props.constraint_attributes:
            if attribute.is_null:
                attributes[attribute.name] = None
            elif attribute.enum_items:
                attributes[attribute.name] = attribute.enum_value
            else:
                attributes[attribute.name] = attribute.string_value
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "constraint.edit_objective",
            self.file,
            **{"objective": self.file.by_id(props.active_constraint_id), "attributes": attributes},
        )
        bpy.ops.bim.load_objectives()
        return {"FINISHED"}


class RemoveConstraint(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_constraint"
    bl_label = "Remove Constraint"
    bl_options = {"REGISTER", "UNDO"}
    constraint: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMConstraintProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "constraint.remove_constraint", self.file, **{"constraint": self.file.by_id(self.constraint)}
        )
        if props.is_editing == "IfcObjective":
            bpy.ops.bim.load_objectives()
        return {"FINISHED"}


class EnableAssigningConstraint(bpy.types.Operator):
    bl_idname = "bim.enable_assigning_constraint"
    bl_label = "Enable Assigning Constraint"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMObjectConstraintProperties
        if props.available_constraint_types == "IfcObjective":
            bpy.ops.bim.load_objectives()
        props.is_adding = props.available_constraint_types
        return {"FINISHED"}


class DisableAssigningConstraint(bpy.types.Operator):
    bl_idname = "bim.disable_assigning_constraint"
    bl_label = "Disable Assigning Constraint"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMObjectConstraintProperties
        props.is_adding = ""
        return {"FINISHED"}


class AssignConstraint(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_constraint"
    bl_label = "Assign Constraint"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    constraint: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        objs = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        products = [self.file.by_id(obj_id) for obj in objs if (obj_id := obj.BIMObjectProperties.ifc_definition_id)]
        if products:
            ifcopenshell.api.run(
                "constraint.assign_constraint",
                self.file,
                **{
                    "products": products,
                    "constraint": self.file.by_id(self.constraint),
                },
            )
        return {"FINISHED"}


class UnassignConstraint(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_constraint"
    bl_label = "Unassign Constraint"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    constraint: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        objs = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        products = [self.file.by_id(obj_id) for obj in objs if (obj_id := obj.BIMObjectProperties.ifc_definition_id)]
        if products:
            ifcopenshell.api.run(
                "constraint.unassign_constraint",
                self.file,
                **{
                    "products": products,
                    "constraint": self.file.by_id(self.constraint),
                },
            )
        return {"FINISHED"}
