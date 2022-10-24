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
import blenderbim.tool as tool
import blenderbim.core.spatial as core
import blenderbim.core.root
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.spatial.data import SpatialData


class ReferenceStructure(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.reference_structure"
    bl_label = "Reference Structure"
    bl_options = {"REGISTER", "UNDO"}
    structure: bpy.props.IntProperty()

    def _execute(self, context):
        sprops = context.scene.BIMSpatialProperties
        containers = [tool.Ifc.get().by_id(c.ifc_definition_id) for c in sprops.containers if c.is_selected]
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            for container in containers:
                core.reference_structure(tool.Ifc, tool.Spatial, structure=container, element=element)


class DereferenceStructure(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.dereference_structure"
    bl_label = "Dereference Structure"
    bl_options = {"REGISTER", "UNDO"}
    structure: bpy.props.IntProperty()

    def _execute(self, context):
        sprops = context.scene.BIMSpatialProperties
        containers = [tool.Ifc.get().by_id(c.ifc_definition_id) for c in sprops.containers if c.is_selected]
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            for container in containers:
                core.dereference_structure(tool.Ifc, tool.Spatial, structure=container, element=element)


class AssignContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_container"
    bl_label = "Assign Container"
    bl_options = {"REGISTER", "UNDO"}
    structure: bpy.props.IntProperty()

    def _execute(self, context):
        structure_obj = tool.Ifc.get_object(tool.Ifc.get().by_id(self.structure))
        for element_obj in context.selected_objects:
            core.assign_container(
                tool.Ifc, tool.Collector, tool.Spatial, structure_obj=structure_obj, element_obj=element_obj
            )


class EnableEditingContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_container"
    bl_label = "Enable Editing Container"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.enable_editing_container(tool.Spatial, obj=context.active_object)


class ChangeSpatialLevel(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_spatial_level"
    bl_label = "Change Spatial Level"
    bl_options = {"REGISTER", "UNDO"}
    parent: bpy.props.IntProperty()

    def _execute(self, context):
        core.change_spatial_level(tool.Spatial, parent=tool.Ifc.get().by_id(self.parent))


class DisableEditingContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_container"
    bl_label = "Disable Editing Container"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_container(tool.Spatial, obj=context.active_object)


class RemoveContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_container"
    bl_label = "Remove Container"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        for obj in context.selected_objects:
            core.remove_container(tool.Ifc, tool.Collector, obj=obj)


class CopyToContainer(bpy.types.Operator, tool.Ifc.Operator):
    """
    Copies selected 3D elements in the viewport to checkmarked spatial containers

    Example: bulk copy a wall to multiple storeys

    1. Select one or more 3D elements in the viewport
    2. Enable the checkmark next to one or more containers in the container list below to select it
    3. Press this button
    4. The copied elements will have a new position relative to the destination containers
    """

    bl_idname = "bim.copy_to_container"
    bl_label = "Copy To Container"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        sprops = context.scene.BIMSpatialProperties
        # Track decompositions so they can be recreated after the operation
        relationships = tool.Root.get_decomposition_relationships(context.selected_objects)
        old_to_new = {}
        containers = [tool.Ifc.get().by_id(c.ifc_definition_id) for c in sprops.containers if c.is_selected]
        for obj in context.selected_objects:
            result_objs = core.copy_to_container(tool.Ifc, tool.Spatial, obj=obj, containers=containers)
            if result_objs:
                old_to_new[tool.Ifc.get_entity(obj)] = result_objs
        # Recreate decompositions
        tool.Root.recreate_decompositions(relationships, old_to_new)
        blenderbim.bim.handler.purge_module_data()


class SelectContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_container"
    bl_label = "Select Container"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.select_container(tool.Ifc, tool.Spatial, obj=context.active_object)


class SelectSimilarContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_similar_container"
    bl_label = "Select Similar Container"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.select_similar_container(tool.Ifc, tool.Spatial, obj=context.active_object)
