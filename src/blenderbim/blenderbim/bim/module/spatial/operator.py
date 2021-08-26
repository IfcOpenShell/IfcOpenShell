
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

import bpy
import ifcopenshell.api
import ifcopenshell.util.element
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.spatial.data import Data
from blenderbim.bim.module.spatial.prop import getSpatialContainers


class AssignContainer(bpy.types.Operator):
    bl_idname = "bim.assign_container"
    bl_label = "Assign Container"
    bl_options = {"REGISTER", "UNDO"}
    relating_structure: bpy.props.IntProperty()
    related_element: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        # The active object pointer is lost when the object is unlinked from all collections in the view layer
        # We need to store it first, then restore it at the end
        active_object = context.active_object
        self.file = IfcStore.get_file()
        related_elements = (
            [bpy.data.objects.get(self.related_element)] if self.related_element else context.selected_objects
        )
        sprops = context.scene.BIMSpatialProperties
        relating_structure = (
            self.relating_structure or sprops.spatial_elements[sprops.active_spatial_element_index].ifc_definition_id
        )
        for related_element in related_elements:
            oprops = related_element.BIMObjectProperties            
            if not oprops.ifc_definition_id:
                continue
            props = related_element.BIMObjectSpatialProperties

            ifcopenshell.api.run(
                "spatial.assign_container",
                self.file,
                **{
                    "product": self.file.by_id(oprops.ifc_definition_id),
                    "relating_structure": self.file.by_id(relating_structure),
                },
            )
            bpy.ops.bim.edit_object_placement(obj=related_element.name)
            Data.load(IfcStore.get_file(), oprops.ifc_definition_id)
            bpy.ops.bim.disable_editing_container(obj=related_element.name)

            aggregate_collection = bpy.data.collections.get(related_element.name)

            relating_structure_obj = IfcStore.get_element(relating_structure)
            relating_collection = None
            if relating_structure_obj:
                relating_collection = bpy.data.collections.get(relating_structure_obj.name)

            if aggregate_collection:
                self.remove_collection(context.scene.collection, aggregate_collection)
                for collection in bpy.data.collections:
                    self.remove_collection(collection, aggregate_collection)
                relating_collection.children.link(aggregate_collection)
            elif relating_collection:
                for collection in related_element.users_collection:
                    collection.objects.unlink(related_element)
                relating_collection.objects.link(related_element)
        # Restore the active object :
        context.view_layer.objects.active = active_object
        return {"FINISHED"}

    def remove_collection(self, parent, child):
        try:
            parent.children.unlink(child)
        except:
            pass


class EnableEditingContainer(bpy.types.Operator):
    bl_idname = "bim.enable_editing_container"
    bl_label = "Enable Editing Container"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.active_object.BIMObjectSpatialProperties.is_editing = True
        getSpatialContainers(self, context)
        return {"FINISHED"}


class ChangeSpatialLevel(bpy.types.Operator):
    bl_idname = "bim.change_spatial_level"
    bl_label = "Change Spatial Level"
    bl_options = {"REGISTER", "UNDO"}
    parent_id: bpy.props.IntProperty()

    def execute(self, context):
        getSpatialContainers(self, context, parent_id=self.parent_id)
        return {"FINISHED"}


class DisableEditingContainer(bpy.types.Operator):
    bl_idname = "bim.disable_editing_container"
    bl_label = "Disable Editing Container"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        obj.BIMObjectSpatialProperties.is_editing = False
        return {"FINISHED"}


class RemoveContainer(bpy.types.Operator):
    bl_idname = "bim.remove_container"
    bl_label = "Remove Container"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        active_object = context.active_object
        self.file = IfcStore.get_file()
        objs = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        for obj in objs:
            obj_id = obj.BIMObjectProperties.ifc_definition_id
            if not obj_id:
                continue
            ifcopenshell.api.run(
                "spatial.remove_container", 
                self.file, 
                **{
                    "product": self.file.by_id(obj_id)
                }
            )
            Data.load(self.file, obj_id)

            aggregate_collection = bpy.data.collections.get(obj.name)
            if aggregate_collection:
                self.remove_collection(context.scene.collection, aggregate_collection)
                for collection in bpy.data.collections:
                    self.remove_collection(collection, spatial_collection)
                context.scene.collection.children.link(aggregate_collection)
            else:
                for collection in obj.users_collection:
                    collection.objects.unlink(obj)
                context.scene.collection.objects.link(obj)
        context.view_layer.objects.active = active_object
        return {"FINISHED"}

    def remove_collection(self, parent, child):
        try:
            parent.children.unlink(child)
        except:
            pass


class CopyToContainer(bpy.types.Operator):
    """
    Copies selected objects to selected containers
    Check the mark next to a container in the container list to select it
    Several containers can be selected at a time
    """
    bl_idname = "bim.copy_to_container"
    bl_label = "Copy To Container"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        objects = list(bpy.data.objects.get(self.obj, context.selected_objects))
        sprops = context.scene.BIMSpatialProperties
        container_ids = [c.ifc_definition_id for c in sprops.spatial_elements if c.is_selected]
        for obj in objects:
            container = ifcopenshell.util.element.get_container(self.file.by_id(obj.BIMObjectProperties.ifc_definition_id))
            if container:
                container_obj = IfcStore.get_element(container.id())
                local_position = container_obj.matrix_world.inverted() @ obj.matrix_world
            else:
                local_position = obj.matrix_world

            for container_id in container_ids:
                container_obj = IfcStore.get_element(container_id)
                if not container_obj:
                    continue
                new_obj = obj.copy()
                new_obj.data = obj.data.copy()
                new_obj.matrix_world = container_obj.matrix_world @ local_position
                bpy.ops.bim.copy_class(obj=new_obj.name)
                bpy.ops.bim.assign_container(relating_structure=container_id, related_element=new_obj.name)
        obj.BIMObjectSpatialProperties.is_editing = False
        return {"FINISHED"}
