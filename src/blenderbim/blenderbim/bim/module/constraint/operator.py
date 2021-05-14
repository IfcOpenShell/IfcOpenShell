import bpy
import json
import ifcopenshell.api
import ifcopenshell.util.attribute
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.constraint.data import Data


class LoadObjectives(bpy.types.Operator):
    bl_idname = "bim.load_objectives"
    bl_label = "Load Objectives"

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

    def execute(self, context):
        context.scene.BIMConstraintProperties.is_editing = ""
        bpy.ops.bim.disable_editing_constraint()
        return {"FINISHED"}


class EnableEditingConstraint(bpy.types.Operator):
    bl_idname = "bim.enable_editing_constraint"
    bl_label = "Enable Editing Constraint"
    constraint: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMConstraintProperties
        while len(props.constraint_attributes) > 0:
            props.constraint_attributes.remove(0)

        if props.is_editing == "IfcObjective":
            data = Data.objectives[self.constraint]

        for attribute in IfcStore.get_schema().declaration_by_name(props.is_editing).all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if data_type == "entity":
                continue
            new = props.constraint_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            new.data_type = data_type
            if data_type == "string":
                new.string_value = "" if new.is_null else data[attribute.name()]
            elif data_type == "enum":
                new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]
        props.active_constraint_id = self.constraint
        return {"FINISHED"}


class DisableEditingConstraint(bpy.types.Operator):
    bl_idname = "bim.disable_editing_constraint"
    bl_label = "Disable Editing Constraint"

    def execute(self, context):
        context.scene.BIMConstraintProperties.active_constraint_id = 0
        return {"FINISHED"}


class AddObjective(bpy.types.Operator):
    bl_idname = "bim.add_objective"
    bl_label = "Add Objective"

    def execute(self, context):
        result = ifcopenshell.api.run("constraint.add_objective", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_objectives()
        bpy.ops.bim.enable_editing_constraint(constraint=result.id())
        return {"FINISHED"}


class EditObjective(bpy.types.Operator):
    bl_idname = "bim.edit_objective"
    bl_label = "Edit Objective"

    def execute(self, context):
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
    constraint: bpy.props.IntProperty()

    def execute(self, context):
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
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMObjectConstraintProperties
        props.is_adding = ""
        return {"FINISHED"}


class AssignConstraint(bpy.types.Operator):
    bl_idname = "bim.assign_constraint"
    bl_label = "Assign Constraint"
    obj: bpy.props.StringProperty()
    constraint: bpy.props.IntProperty()

    def execute(self, context):
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
    obj: bpy.props.StringProperty()
    constraint: bpy.props.IntProperty()

    def execute(self, context):
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
