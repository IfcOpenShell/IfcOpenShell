import bpy
import blenderbim.bim.module.aggregate.assign_object as assign_object
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.aggregate.data import Data


class AssignObject(bpy.types.Operator):
    bl_idname = "bim.assign_object"
    bl_label = "Assign Object"

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.context.active_object
        props = obj.BIMObjectProperties
        relating_object = props.relating_object
        if not relating_object or not relating_object.BIMObjectProperties.ifc_definition_id:
            return {"FINISHED"}
        usecase = assign_object.Usecase(
            self.file,
            {
                "product": self.file.by_id(props.ifc_definition_id),
                "relating_object": self.file.by_id(relating_object.BIMObjectProperties.ifc_definition_id),
            },
        )
        usecase.execute()
        Data.load(props.ifc_definition_id)
        bpy.ops.bim.disable_editing_aggregate()
        return {"FINISHED"}


class EnableEditingAggregate(bpy.types.Operator):
    bl_idname = "bim.enable_editing_aggregate"
    bl_label = "Enable Editing Aggregate"

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.relating_object = None
        bpy.context.active_object.BIMObjectProperties.is_editing_aggregate = True
        return {"FINISHED"}


class DisableEditingAggregate(bpy.types.Operator):
    bl_idname = "bim.disable_editing_aggregate"
    bl_label = "Disable Editing Aggregate"

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.is_editing_aggregate = False
        return {"FINISHED"}
