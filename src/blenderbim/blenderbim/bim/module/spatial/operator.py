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
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.spatial.data import SpatialData


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class AssignContainer(bpy.types.Operator, Operator):
    bl_idname = "bim.assign_container"
    bl_label = "Assign Container"
    bl_options = {"REGISTER", "UNDO"}
    structure: bpy.props.IntProperty()

    def _execute(self, context):
        structure_obj = tool.Ifc.get_object(tool.Ifc.get().by_id(self.structure))
        for element_obj in context.selected_objects:
            core.assign_container(
                tool.Ifc,
                tool.Collector,
                tool.Container,
                structure_obj=structure_obj,
                element_obj=element_obj,
            )


class EnableEditingContainer(bpy.types.Operator, Operator):
    bl_idname = "bim.enable_editing_container"
    bl_label = "Enable Editing Container"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.enable_editing_container(tool.Container, obj=context.active_object)


class ChangeSpatialLevel(bpy.types.Operator, Operator):
    bl_idname = "bim.change_spatial_level"
    bl_label = "Change Spatial Level"
    bl_options = {"REGISTER", "UNDO"}
    parent: bpy.props.IntProperty()

    def _execute(self, context):
        core.change_spatial_level(tool.Container, parent=tool.Ifc.get().by_id(self.parent))


class DisableEditingContainer(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_container"
    bl_label = "Disable Editing Container"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_container(tool.Container, obj=context.active_object)


class RemoveContainer(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_container"
    bl_label = "Remove Container"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        for obj in context.selected_objects:
            core.remove_container(tool.Ifc, tool.Collector, obj=obj)


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
            container = ifcopenshell.util.element.get_container(
                self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            )
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
