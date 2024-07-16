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
import ifcopenshell.util.element
import blenderbim.tool as tool
import blenderbim.core.spatial as core
import blenderbim.core.geometry
import blenderbim.core.aggregate
import blenderbim.core.root
import blenderbim.bim.handler


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
            result_objs = core.copy_to_container(tool.Ifc, tool.Collector, tool.Spatial, obj=obj, containers=containers)
            if result_objs:
                old_to_new[tool.Ifc.get_entity(obj)] = result_objs
        # Recreate decompositions
        tool.Root.recreate_decompositions(relationships, old_to_new)
        blenderbim.bim.handler.refresh_ui_data()


class SelectContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_container"
    bl_label = "Select Container"
    bl_options = {"REGISTER", "UNDO"}
    container: bpy.props.IntProperty()

    def _execute(self, context):
        if self.container:
            container = tool.Ifc.get().by_id(self.container)
        elif element := tool.Ifc.get_entity(context.active_object):
            container = ifcopenshell.util.element.get_container(element)
        else:
            return
        if container:
            core.select_container(tool.Ifc, tool.Spatial, container=container)


class SelectSimilarContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_similar_container"
    bl_label = "Select Similar Container"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.select_similar_container(tool.Ifc, tool.Spatial, obj=context.active_object)


class SelectProduct(bpy.types.Operator):
    bl_idname = "bim.select_product"
    bl_label = "Select Product"
    bl_options = {"REGISTER", "UNDO"}
    product: bpy.props.IntProperty()

    def execute(self, context):
        core.select_product(tool.Spatial, product=tool.Ifc.get().by_id(self.product))
        return {"FINISHED"}


class ImportSpatialDecomposition(bpy.types.Operator):
    bl_idname = "bim.import_spatial_decomposition"
    bl_label = "Load Container Manager"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.import_spatial_decomposition(tool.Spatial)
        return {"FINISHED"}


class EditContainerAttributes(bpy.types.Operator):
    bl_idname = "bim.edit_container_attributes"
    bl_label = "Edit container attributes"
    bl_options = {"REGISTER", "UNDO"}
    container: bpy.props.IntProperty()

    def execute(self, context):
        core.edit_container_attributes(tool.Spatial, entity=tool.Ifc.get().by_id(self.container))
        return {"FINISHED"}


class ContractContainer(bpy.types.Operator):
    bl_idname = "bim.contract_container"
    bl_label = "Contract Container"
    bl_options = {"REGISTER", "UNDO"}
    container: bpy.props.IntProperty()

    def execute(self, context):
        core.contract_container(tool.Spatial, container=tool.Ifc.get().by_id(self.container))
        return {"FINISHED"}


class ExpandContainer(bpy.types.Operator):
    bl_idname = "bim.expand_container"
    bl_label = "Expand Container"
    bl_options = {"REGISTER", "UNDO"}
    container: bpy.props.IntProperty()

    def execute(self, context):
        core.expand_container(tool.Spatial, container=tool.Ifc.get().by_id(self.container))
        return {"FINISHED"}


class DeleteContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.delete_container"
    bl_label = "Delete Container"
    bl_options = {"REGISTER", "UNDO"}
    container: bpy.props.IntProperty()

    def _execute(self, context):
        core.delete_container(tool.Ifc, tool.Spatial, tool.Geometry, container=tool.Ifc.get().by_id(self.container))


class SelectDecomposedElements(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_decomposed_elements"
    bl_label = "Select Children"
    bl_options = {"REGISTER", "UNDO"}
    container: bpy.props.IntProperty()
    ifc_class: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, operator):
        return f"Select all elements contained in this {operator.ifc_class}"

    def _execute(self, context):
        core.select_decomposed_elements(tool.Spatial, container=tool.Ifc.get().by_id(self.container))


class SetDefaultContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.set_default_container"
    bl_label = "Set Default Container"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Set this as the default container that all new elements will be contained in"
    container: bpy.props.IntProperty()

    def _execute(self, context):
        core.set_default_container(tool.Spatial, container=tool.Ifc.get().by_id(self.container))


class SetContainerVisibility(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.set_container_visibility"
    bl_label = "Set Container Visibility"
    bl_options = {"REGISTER", "UNDO"}
    container: bpy.props.IntProperty()
    should_include_children: bpy.props.BoolProperty(name="Should Include Children", default=True, options={"SKIP_SAVE"})
    mode: bpy.props.StringProperty(name="Mode")

    @classmethod
    def description(cls, context, operator):
        if operator.mode == "HIDE":
            return "Hides the selected container and all children.\n" + "ALT+CLICK to ignore children"
        elif operator.mode == "SHOW":
            return "Shows the selected container and all children.\n" + "ALT+CLICK to ignore children"
        return "Isolate the selected container and all children.\n" + "ALT+CLICK to ignore children"

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.alt:
            self.should_include_children = False
        return self.execute(context)

    def _execute(self, context):
        if self.mode == "ISOLATE":
            if tool.Ifc.get_schema() == "IFC2X3":
                containers = tool.Ifc.get().by_type("IfcSpatialStructureElement")
            elif tool.Ifc.get_schema() != "IFC2X3":
                containers = set(tool.Ifc.get().by_type("IfcSpatialElement"))
                containers -= set(tool.Ifc.get().by_type("IfcSpatialZone"))
            for container in containers:
                if obj := tool.Ifc.get_object(container):
                    if collection := obj.BIMObjectProperties.collection:
                        collection.hide_viewport = True
            should_hide = False
        else:
            should_hide = self.mode == "HIDE"

        container = tool.Ifc.get().by_id(self.container)
        queue = [container]
        while queue:
            container = queue.pop()
            if obj := tool.Ifc.get_object(container):
                if collection := obj.BIMObjectProperties.collection:
                    collection.hide_viewport = should_hide
            if self.should_include_children:
                queue.extend(ifcopenshell.util.element.get_parts(container))
