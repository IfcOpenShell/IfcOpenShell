import bpy
import json
import ifcopenshell.api
import ifcopenshell.util.attribute
import blenderbim.bim.helper
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.constraint.data import Data


class LoadObjectives(bpy.types.Operator):
    bl_idname = "bim.load_objectives"
    bl_label = "Load Objectives"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMConstraintProperties
        while len(props.constraints) > 0:
            props.constraints.remove(0)
        for constraint_id, constraint in Data.objectives.items():
            new = props.constraints.add()
            new.name = constraint["Name"] or "Unnamed"
            new.ifc_definition_id = constraint_id
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
        while len(props.constraint_attributes) > 0:
            props.constraint_attributes.remove(0)

        if props.is_editing == "IfcObjective":
            data = Data.objectives[self.constraint]

        blenderbim.bim.helper.import_attributes(props.is_editing, props.constraint_attributes, data)
        props.active_constraint_id = self.constraint
        return {"FINISHED"}


class DisableEditingConstraint(bpy.types.Operator):
    bl_idname = "bim.disable_editing_constraint"
    bl_label = "Disable Editing Constraint"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMConstraintProperties.active_constraint_id = 0
        return {"FINISHED"}


class AddObjective(bpy.types.Operator):
    bl_idname = "bim.add_objective"
    bl_label = "Add Objective"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        result = ifcopenshell.api.run("constraint.add_objective", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_objectives()
        bpy.ops.bim.enable_editing_constraint(constraint=result.id())
        return {"FINISHED"}


class EditObjective(bpy.types.Operator):
    bl_idname = "bim.edit_objective"
    bl_label = "Edit Objective"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

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
            **{"objective": self.file.by_id(props.active_constraint_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_objectives()
        return {"FINISHED"}


class RemoveConstraint(bpy.types.Operator):
    bl_idname = "bim.remove_constraint"
    bl_label = "Remove Constraint"
    bl_options = {"REGISTER", "UNDO"}
    constraint: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMConstraintProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "constraint.remove_constraint", self.file, **{"constraint": self.file.by_id(self.constraint)}
        )
        Data.load(IfcStore.get_file())
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


class AssignConstraint(bpy.types.Operator):
    bl_idname = "bim.assign_constraint"
    bl_label = "Assign Constraint"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    constraint: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "constraint.assign_constraint",
            self.file,
            **{
                "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
                "constraint": self.file.by_id(self.constraint),
            }
        )
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class UnassignConstraint(bpy.types.Operator):
    bl_idname = "bim.unassign_constraint"
    bl_label = "Unassign Constraint"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    constraint: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "constraint.unassign_constraint",
            self.file,
            **{
                "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
                "constraint": self.file.by_id(self.constraint),
            }
        )
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}
