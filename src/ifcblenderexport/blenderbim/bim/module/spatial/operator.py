import bpy
import blenderbim.bim.module.spatial.assign_container as assign_container
import blenderbim.bim.module.spatial.remove_container as remove_container
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.spatial.data import Data


class AssignContainer(bpy.types.Operator):
    bl_idname = "bim.assign_container"
    bl_label = "Assign Container"
    relating_structure: bpy.props.StringProperty()
    related_element: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_element = (
            bpy.data.objects.get(self.related_element) if self.related_element else bpy.context.active_object
        )
        props = related_element.BIMObjectProperties
        relating_structure = (
            bpy.data.objects.get(self.relating_structure) if self.relating_structure else props.relating_structure
        )
        if not relating_structure or not relating_structure.BIMObjectProperties.ifc_definition_id:
            return {"FINISHED"}
        assign_container.Usecase(
            self.file,
            {
                "product": self.file.by_id(props.ifc_definition_id),
                "relating_structure": self.file.by_id(relating_structure.BIMObjectProperties.ifc_definition_id),
            },
        ).execute()
        bpy.ops.bim.edit_object_placement(obj=related_element.name)
        Data.load(props.ifc_definition_id)
        bpy.ops.bim.disable_editing_container(obj=related_element.name)

        aggregate_collection = bpy.data.collections.get(related_element.name)
        relating_collection = bpy.data.collections.get(relating_structure.name)
        if aggregate_collection:
            self.remove_collection(bpy.context.scene.collection, aggregate_collection)
            for collection in bpy.data.collections:
                self.remove_collection(collection, aggregate_collection)
            relating_collection.children.link(aggregate_collection)
        else:
            for collection in related_element.users_collection:
                collection.objects.unlink(related_element)
            relating_collection.objects.link(related_element)
        return {"FINISHED"}

    def remove_collection(self, parent, child):
        try:
            parent.children.unlink(child)
        except:
            pass


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


class RemoveContainer(bpy.types.Operator):
    bl_idname = "bim.remove_container"
    bl_label = "Remvoe Container"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        props = obj.BIMObjectProperties
        self.file = IfcStore.get_file()
        remove_container.Usecase(self.file, {"product": self.file.by_id(props.ifc_definition_id)}).execute()
        Data.load(props.ifc_definition_id)

        aggregate_collection = bpy.data.collections.get(obj.name)
        if aggregate_collection:
            self.remove_collection(bpy.context.scene.collection, aggregate_collection)
            for collection in bpy.data.collections:
                self.remove_collection(collection, spatial_collection)
            bpy.context.scene.collection.children.link(aggregate_collection)
        else:
            for collection in obj.users_collection:
                collection.objects.unlink(obj)
            bpy.context.scene.collection.objects.link(obj)
        return {"FINISHED"}

    def remove_collection(self, parent, child):
        try:
            parent.children.unlink(child)
        except:
            pass
