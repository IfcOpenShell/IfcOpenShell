import bpy
import blenderbim.bim.module.spatial.assign_container as assign_container
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.spatial.data import Data


class AssignContainer(bpy.types.Operator):
    bl_idname = "bim.assign_container"
    bl_label = "Assign Container"
    relating_structure: bpy.props.StringProperty()
    related_element: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_element = bpy.data.objects.get(self.related_element) if self.related_element else bpy.context.active_object
        props = related_element.BIMObjectProperties
        relating_structure = bpy.data.objects.get(self.relating_structure) if self.relating_structure else props.relating_structure
        if not relating_structure or not relating_structure.BIMObjectProperties.ifc_definition_id:
            return {"FINISHED"}
        assign_container.Usecase(
            self.file,
            {
                "product": self.file.by_id(props.ifc_definition_id),
                "relating_structure": self.file.by_id(relating_structure.BIMObjectProperties.ifc_definition_id),
            },
        ).execute()
        Data.load(props.ifc_definition_id)
        bpy.ops.bim.disable_editing_container(obj=related_element.name)

        for collection in related_element.users_collection:
            collection.objects.unlink(related_element)
        collection = bpy.data.collections.get(relating_structure.name)
        collection.objects.link(related_element)
        return {"FINISHED"}


class EnableEditingContainer(bpy.types.Operator):
    bl_idname = "bim.enable_editing_container"
    bl_label = "Enable Editing Container"

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.relating_structure = None
        bpy.context.active_object.BIMObjectProperties.is_editing_container = True
        return {"FINISHED"}


class DisableEditingContainer(bpy.types.Operator):
    bl_idname = "bim.disable_editing_container"
    bl_label = "Disable Editing Container"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        obj.BIMObjectProperties.is_editing_container = False
        return {"FINISHED"}
