# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell.util.element
import bonsai.tool as tool
import bonsai.core.spatial as core
import bonsai.bim.handler


class ReferenceStructure(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.reference_structure"
    bl_label = "Reference Structure"
    bl_description = (
        "Reference selected objects from all selected structures.\n\n"
        "Currently we do not support referencing structures in other structures "
        "though it is allowed in IFC4X3"
    )
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        objs = tool.Spatial.get_selected_objects_without_containers()
        if not objs:
            self.report({"INFO"}, "No non-spatial objects are selected.")
            return

        containers = tool.Spatial.get_selected_containers()
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            for container in containers:
                core.reference_structure(tool.Ifc, tool.Spatial, structure=container, element=element)


class DereferenceStructure(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.dereference_structure"
    bl_label = "Dereference Structure"
    bl_description = (
        "Dereference selected objects from all selected structures.\n\n"
        "Currently we do not support referencing structures in other structures "
        "though it is allowed in IFC4X3"
    )
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        objs = tool.Spatial.get_selected_objects_without_containers()
        if not objs:
            self.report({"INFO"}, "No non-spatial objects are selected.")
            return

        containers = tool.Spatial.get_selected_containers()
        for obj in objs:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            for container in containers:
                core.dereference_structure(tool.Ifc, tool.Spatial, structure=container, element=element)


class AssignContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_container"
    bl_label = "Assign Container"
    bl_description = "Assign the selected objects to the selected container"
    bl_options = {"REGISTER", "UNDO"}
    container: bpy.props.IntProperty(options={"SKIP_SAVE"})

    def _execute(self, context):
        props = context.active_object.BIMObjectSpatialProperties
        if self.container:
            container = tool.Ifc.get().by_id(self.container)
        elif (container_obj := props.container_obj) and (container := tool.Ifc.get_entity(container_obj)):
            pass
        for element_obj in context.selected_objects:
            core.assign_container(tool.Ifc, tool.Collector, tool.Spatial, container=container, element_obj=element_obj)


class EnableEditingContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_container"
    bl_label = "Enable Editing Container"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.enable_editing_container(tool.Spatial, obj=context.active_object)


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
    Copies selected 3D elements in the viewport to the selected spatial containers

    Example: bulk copy a wall to multiple storeys

    1. Select one or more 3D elements in the viewport
    2. Select one or more spatial containers in the viewport
    3. Press this button
    4. The copied elements will have a new position relative to the destination containers

    Copying containers to other containers currently is not supported."""

    bl_idname = "bim.copy_to_container"
    bl_label = "Copy To Container"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        objs = tool.Spatial.get_selected_objects_without_containers()
        if not objs:
            self.report({"INFO"}, "No non-spatial objects are selected.")
            return

        containers = tool.Spatial.get_selected_containers()
        # Track decompositions so they can be recreated after the operation
        relationships = tool.Root.get_decomposition_relationships(objs)
        old_to_new = {}
        for obj in objs:
            result_objs = core.copy_to_container(tool.Ifc, tool.Collector, tool.Spatial, obj=obj, containers=containers)
            if result_objs:
                old_to_new[tool.Ifc.get_entity(obj)] = result_objs

        # Recreate decompositions
        tool.Root.recreate_decompositions(relationships, old_to_new)
        bonsai.bim.handler.refresh_ui_data()


class SelectContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_container"
    bl_label = "Select Container"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "SHIFT + Click to add container to selection\nALT + Click to remove container from selection"
    container: bpy.props.IntProperty()
    selection_mode: bpy.props.EnumProperty(items=[("ADD",) * 3, ("REMOVE",) * 3, ("SINGLE",) * 3])

    def invoke(self, context, event):
        if event.shift:
            self.selection_mode = "ADD"
        elif event.alt:
            self.selection_mode = "REMOVE"
        else:
            self.selection_mode = "SINGLE"
        return self.execute(context)

    def _execute(self, context):
        if self.container:
            container = tool.Ifc.get().by_id(self.container)
        elif element := tool.Ifc.get_entity(context.active_object):
            container = ifcopenshell.util.element.get_container(element)
        else:
            return
        if container:
            core.select_container(
                tool.Ifc,
                tool.Spatial,
                container=container,
                selection_mode=self.selection_mode,
            )


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


class ToggleContainerElement(bpy.types.Operator):
    bl_idname = "bim.toggle_container_element"
    bl_label = "Toggle Container Element"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Toggle children\nALT+CLICK to recursively toggle children"
    element_index: bpy.props.IntProperty()
    is_recursive: bpy.props.BoolProperty(name="Is Recursive", default=False, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.alt:
            self.is_recursive = True
        return self.execute(context)

    def execute(self, context):
        core.toggle_container_element(tool.Spatial, element_index=self.element_index, is_recursive=self.is_recursive)
        return {"FINISHED"}


class SelectDecomposedElement(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_decomposed_element"
    bl_label = "Select Decomposed Element"
    bl_options = {"REGISTER", "UNDO"}
    element: bpy.props.IntProperty()

    def _execute(self, context):
        if self.element:
            core.select_decomposed_element(tool.Ifc, tool.Spatial, element=tool.Ifc.get().by_id(self.element))


class SelectDecomposedElements(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_decomposed_elements"
    bl_label = "Select Children"
    bl_options = {"REGISTER", "UNDO"}
    should_filter: bpy.props.BoolProperty(name="Should Filter", default=True, options={"SKIP_SAVE"})
    container: bpy.props.IntProperty()

    @classmethod
    def description(cls, context, operator):
        return "Select all contained elements filtered by this type" + "\nALT+CLICK to select all contained elements"

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.alt:
            self.should_filter = False
        return self.execute(context)

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        container = ifc_file.by_id(self.container)
        props = context.scene.BIMSpatialDecompositionProperties
        element_filter = props.element_filter
        active_element = props.active_element

        if not self.should_filter and not element_filter:
            tool.Spatial.select_products(tool.Spatial.get_decomposed_elements(container))
            return

        if props.element_mode == "TYPE":
            if active_element.type == "OCCURRENCE":
                if obj := tool.Ifc.get_object(ifc_file.by_id(active_element.ifc_definition_id)):
                    tool.Blender.set_active_object(obj)
                return

            ifc_class = relating_type = None
            is_untyped = False

            if self.should_filter:
                if active_element.type == "CLASS":
                    ifc_class = active_element.name
                elif active_element.type == "TYPE":
                    ifc_class = active_element.ifc_class
                    if ifc_id := active_element.ifc_definition_id:
                        relating_type = ifc_file.by_id(ifc_id)

            elements = tool.Spatial.get_decomposed_elements(container)
            elements = tool.Spatial.filter_elements(elements, ifc_class, relating_type, is_untyped, element_filter)
            tool.Spatial.select_products(elements)
        elif props.element_mode == "DECOMPOSITION":
            occurrence = ifc_file.by_id(active_element.ifc_definition_id)
            elements = ifcopenshell.util.element.get_decomposition(occurrence)
            elements.add(occurrence)
            tool.Spatial.select_products(elements)
        elif props.element_mode == "CLASSIFICATION":
            if active_element.type == "OCCURRENCE":
                if obj := tool.Ifc.get_object(ifc_file.by_id(active_element.ifc_definition_id)):
                    tool.Blender.set_active_object(obj)
                return

            if active_element.type == "CLASSIFICATION":
                identification = active_element.identification
                elements = tool.Spatial.get_decomposed_elements(container)

                def filter_element(element: ifcopenshell.entity_instance) -> bool:
                    references = ifcopenshell.util.classification.get_references(element)
                    if identification == "Unclassified":
                        if not references:
                            return True
                    elif any([r for r in references if r[1].startswith(identification)]):
                        return True
                    return False

                tool.Spatial.select_products(filter(filter_element, elements))


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


class ToggleGrids(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.toggle_grids"
    bl_label = "Toggle Grids"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Show or hide grids and grid axes"
    is_visible: bpy.props.BoolProperty(name="Is Visible", default=False, options={"SKIP_SAVE"})

    def _execute(self, context):
        for element in tool.Ifc.get().by_type("IfcGrid") + tool.Ifc.get().by_type("IfcGridAxis"):
            if obj := tool.Ifc.get_object(element):
                obj.hide_set(not self.is_visible)


class ToggleSpatialElements(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.toggle_spatial_elements"
    bl_label = "Toggle Spatial Elements"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Show or hide spatial elements, such as buildings, sites, etc"
    is_visible: bpy.props.BoolProperty(name="Is Visible", default=False, options={"SKIP_SAVE"})

    def _execute(self, context):
        if tool.Ifc.get().schema == "IFC2X3":
            elements = tool.Ifc.get().by_type("IfcSpatialStructureElement")
        else:
            elements = tool.Ifc.get().by_type("IfcSpatialElement")
        for element in elements:
            if obj := tool.Ifc.get_object(element):
                obj.hide_set(not self.is_visible)
