import bpy
import blenderbim.bim.module.spatial.assign_container as assign_container
import blenderbim.bim.module.spatial.remove_container as remove_container
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.spatial.data import Data
from blenderbim.bim.module.spatial.prop import getSpatialContainers


class AssignContainer(bpy.types.Operator):
    bl_idname = "bim.assign_container"
    bl_label = "Assign Container"
    relating_structure: bpy.props.IntProperty()
    related_element: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_element = (
            bpy.data.objects.get(self.related_element) if self.related_element else bpy.context.active_object
        )
        oprops = related_element.BIMObjectProperties
        sprops = context.scene.BIMSpatialProperties
        props = related_element.BIMObjectSpatialProperties
        relating_structure = (
            self.relating_structure or sprops.spatial_elements[sprops.active_spatial_element_index].ifc_definition_id
        )

        assign_container.Usecase(
            self.file,
            {
                "product": self.file.by_id(oprops.ifc_definition_id),
                "relating_structure": self.file.by_id(relating_structure),
            },
        ).execute()
        bpy.ops.bim.edit_object_placement(obj=related_element.name)
        Data.load(oprops.ifc_definition_id)
        bpy.ops.bim.disable_editing_container(obj=related_element.name)

        aggregate_collection = bpy.data.collections.get(related_element.name)

        relating_structure_obj = IfcStore.id_map.get(relating_structure)
        relating_collection = None
        if relating_structure_obj:
            relating_collection = bpy.data.collections.get(relating_structure_obj.name)

        if aggregate_collection:
            self.remove_collection(bpy.context.scene.collection, aggregate_collection)
            for collection in bpy.data.collections:
                self.remove_collection(collection, aggregate_collection)
            relating_collection.children.link(aggregate_collection)
        elif relating_collection:
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
        bpy.context.active_object.BIMObjectSpatialProperties.is_editing = True
        getSpatialContainers(self, context)
        return {"FINISHED"}


class ChangeSpatialLevel(bpy.types.Operator):
    bl_idname = "bim.change_spatial_level"
    bl_label = "Change Spatial Level"
    parent_id: bpy.props.IntProperty()

    def execute(self, context):
        getSpatialContainers(self, context, parent_id=self.parent_id)
        return {"FINISHED"}


class DisableEditingContainer(bpy.types.Operator):
    bl_idname = "bim.disable_editing_container"
    bl_label = "Disable Editing Container"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        obj.BIMObjectSpatialProperties.is_editing = False
        return {"FINISHED"}


class RemoveContainer(bpy.types.Operator):
    bl_idname = "bim.remove_container"
    bl_label = "Remvoe Container"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        oprops = obj.BIMObjectProperties
        self.file = IfcStore.get_file()
        remove_container.Usecase(self.file, {"product": self.file.by_id(oprops.ifc_definition_id)}).execute()
        Data.load(oprops.ifc_definition_id)

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
