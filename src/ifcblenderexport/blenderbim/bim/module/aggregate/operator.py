import bpy
import blenderbim.bim.module.aggregate.assign_object as assign_object
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.aggregate.data import Data


class AssignObject(bpy.types.Operator):
    bl_idname = "bim.assign_object"
    bl_label = "Assign Object"
    relating_object: bpy.props.StringProperty()
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.data.objects.get(self.related_object) if self.related_object else bpy.context.active_object
        props = obj.BIMObjectProperties
        relating_object = bpy.data.objects.get(self.relating_object) if self.relating_object else props.relating_object
        if not relating_object or not relating_object.BIMObjectProperties.ifc_definition_id:
            return {"FINISHED"}
        assign_object.Usecase(
            self.file,
            {
                "product": self.file.by_id(props.ifc_definition_id),
                "relating_object": self.file.by_id(relating_object.BIMObjectProperties.ifc_definition_id),
            },
        ).execute()
        Data.load(props.ifc_definition_id)
        bpy.ops.bim.disable_editing_aggregate(obj=self.related_object)
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
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        obj.BIMObjectProperties.is_editing_aggregate = False
        return {"FINISHED"}
