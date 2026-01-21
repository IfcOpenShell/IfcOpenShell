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
from typing import TYPE_CHECKING


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


class ReferenceFromProvidedStructure(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.reference_from_provided_structure"
    bl_label = "Reference from Provided Structure"
    bl_description = "Reference selected objects from the provided structure.\n\n" "ALT + Click to dereference instead."
    bl_options = {"REGISTER", "UNDO"}

    structure: bpy.props.IntProperty(options={"SKIP_SAVE"})
    dereference: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        if not tool.Blender.get_selected_objects():
            cls.poll_message_set("No objects selected.")
            return False
        return True

    def invoke(self, context, event):
        self.dereference = event.alt
        return self.execute(context)

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        structure = ifc_file.by_id(self.structure)

        objs = tool.Spatial.get_selected_objects_without_containers()
        if not objs:
            self.report({"INFO"}, "No non-spatial objects are selected.")
            return

        elements = [e for o in objs if (e := tool.Ifc.get_entity(o))]
        for element in elements:
            if self.dereference:
                core.dereference_structure(tool.Ifc, tool.Spatial, structure=structure, element=element)
            else:
                core.reference_structure(tool.Ifc, tool.Spatial, structure=structure, element=element)

        msg = "dereferenced" if self.dereference else "referenced"
        self.report({"INFO"}, f"{len(elements)} elements {msg} from the structure.")


class DereferenceFromProvidedStructure(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.dereference_from_provided_structure"
    bl_label = "Dereference from Provided Structure"
    bl_description = "Dereference selected objects from the provided structure."
    bl_options = {"REGISTER", "UNDO"}

    structure: bpy.props.IntProperty(options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        if not tool.Blender.get_selected_objects():
            cls.poll_message_set("No objects selected.")
            return False
        return True

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        structure = ifc_file.by_id(self.structure)
        objs = tool.Spatial.get_selected_objects_without_containers()
        if not objs:
            self.report({"INFO"}, "No non-spatial objects are selected.")
            return

        elements = [e for o in objs if (e := tool.Ifc.get_entity(o))]
        for element in elements:
            core.dereference_structure(tool.Ifc, tool.Spatial, structure=structure, element=element)

        self.report({"INFO"}, f"{len(elements)} elements dereferenced from the structure.")


class AssignContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_container"
    bl_label = "Assign Container"
    bl_description = (
        "Assign the selected objects to the container selected in Spatial Manager.\n\n"
        "All elements-parts of an aggregate will be skipped.\n"
        "To assign a container, they should be unassigned from an aggregate first.\n\n"
        "This will also move objects to the container collection in the outliner.\n"
        "ALT + Click to ensure objects are only linked in the container collection"
    )
    bl_options = {"REGISTER", "UNDO"}
    container: bpy.props.IntProperty(options={"SKIP_SAVE"})
    remove_from_other_containers: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        self.remove_from_other_containers = event.alt
        return self.execute(context)

    def _execute(self, context):
        if self.container:
            container = tool.Ifc.get().by_id(self.container)
        elif (
            (obj := tool.Blender.get_active_object())
            and (props := tool.Spatial.get_object_spatial_props(obj))
            and (container_obj := props.container_obj)
            and (container := tool.Ifc.get_entity(container_obj))
        ):
            pass
        else:
            return

        def get_root_aggregate(element):
            """Traverse up the aggregate hierarchy to find the top-most aggregate"""
            current = element
            root = None
            while aggregate := ifcopenshell.util.element.get_aggregate(current):
                root = aggregate
                current = aggregate
            return root

        def get_all_parts_recursive(element):
            """Recursively get all parts of an aggregate"""
            parts = []
            for part in ifcopenshell.util.element.get_parts(element):
                parts.append(part)
                # Recursively get nested parts
                parts.extend(get_all_parts_recursive(part))
            return parts

        objs: list[bpy.types.Object] = []
        processed_elements = set()  # Track elements we've already handled (by IFC ID)
        promoted_parts = 0  # Count how many parts were promoted to their root aggregate

        for obj in tool.Blender.get_selected_objects():
            if not (element := tool.Ifc.get_entity(obj)):
                continue

            # Check if element is part of an aggregate (at any level)
            if root_aggregate := get_root_aggregate(element):
                # Skip if we've already processed this root aggregate
                if root_aggregate.id() in processed_elements:
                    continue

                # Get the root aggregate object and add it instead
                if root_aggregate_obj := tool.Ifc.get_object(root_aggregate):
                    objs.append(root_aggregate_obj)
                    processed_elements.add(root_aggregate.id())
                    if root_aggregate != element:  # Only count as promoted if different from selected
                        promoted_parts += 1
            else:
                # Element is not part of any aggregate
                if element.id() not in processed_elements:
                    objs.append(obj)
                    processed_elements.add(element.id())

        # Get the container's collection
        container_obj = tool.Ifc.get_object(container)
        container_collection = container_obj.BIMObjectProperties.collection if container_obj else None

        for element_obj in objs:
            element = tool.Ifc.get_entity(element_obj)

            # Only assign container to the ROOT aggregate (this updates IFC relationships)
            if self.remove_from_other_containers:
                for col in element_obj.users_collection[:]:
                    col.objects.unlink(element_obj)
            core.assign_container(tool.Ifc, tool.Collector, tool.Spatial, container=container, element_obj=element_obj)

            # For parts, only move them in Blender collections (don't change IFC relationships)
            if container_collection:
                all_parts = get_all_parts_recursive(element)
                for part in all_parts:
                    if part_obj := tool.Ifc.get_object(part):
                        # Always remove from ALL previous collections when moving to new container
                        for col in part_obj.users_collection[:]:
                            col.objects.unlink(part_obj)

                        # Link to new container collection (Blender-only, no IFC change)
                        if part_obj.name not in container_collection.objects:
                            container_collection.objects.link(part_obj)

        # Disable editing mode for all selected objects
        for obj in tool.Blender.get_selected_objects():
            core.disable_editing_container(tool.Spatial, obj=obj)

        promoted_msg = ""
        if promoted_parts:
            promoted_msg = f" {promoted_parts} nested parts promoted to their root aggregates."
        self.report({"INFO"}, f"{len(objs)} elements assigned.{promoted_msg}")


class EnableEditingContainer(bpy.types.Operator):
    bl_idname = "bim.enable_editing_container"
    bl_label = "Enable Editing Container"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.enable_editing_container(tool.Spatial, obj=context.active_object)
        return {"FINISHED"}


class DisableEditingContainer(bpy.types.Operator):
    bl_idname = "bim.disable_editing_container"
    bl_label = "Disable Editing Container"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_container(tool.Spatial, obj=context.active_object)
        return {"FINISHED"}


class RemoveContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_container"
    bl_label = "Remove Container"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        for obj in context.selected_objects:
            core.remove_container(tool.Ifc, tool.Collector, obj=obj)


class CopyToContainer(bpy.types.Operator, tool.Ifc.Operator):
    """
    Copies selected 3D elements in the viewport to the container selected in Spatial Manager.

    Example: bulk copy a wall to multiple storeys

    The copied elements will have a new position relative to the destination containers

    Copying containers to other containers currently is not supported."""

    bl_idname = "bim.copy_to_container"
    bl_label = "Copy to Container"
    bl_options = {"REGISTER", "UNDO"}

    container: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        container: int

    def _execute(self, context):
        objs = tool.Spatial.get_selected_objects_without_containers()
        if not objs:
            self.report({"INFO"}, "No non-spatial objects are selected.")
            return

        # TODO: make a multi-select in the spatial decomposition panel to support multiple containers
        # containers = tool.Spatial.get_selected_containers()
        containers = [tool.Ifc.get().by_id(self.container)]
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


class SelectContainer(bpy.types.Operator):
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

    def execute(self, context):
        if self.container:
            container = tool.Ifc.get().by_id(self.container)
        elif element := tool.Ifc.get_entity(context.active_object):
            container = ifcopenshell.util.element.get_container(element)
        else:
            return {"CANCELLED"}
        if container:
            core.select_container(
                tool.Ifc,
                tool.Spatial,
                container=container,
                selection_mode=self.selection_mode,
            )
        return {"FINISHED"}


class SelectSimilarContainer(bpy.types.Operator):
    bl_idname = "bim.select_similar_container"
    bl_label = "Select Similar Container"
    bl_description = "Recurvisevly selects all objects in the container.\n\nCtrl+click to select only one level deep"
    bl_options = {"REGISTER", "UNDO"}

    is_recursive: bpy.props.BoolProperty(default=True)

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.ctrl:
            self.is_recursive = False
        return self.execute(context)

    def execute(self, context):
        core.select_similar_container(
            tool.Ifc,
            tool.Spatial,
            obj=context.active_object,
            is_recursive=self.is_recursive,
        )
        self.is_recursive = True  # <-- forcibly reset
        return {"FINISHED"}


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


class ContractContainer(bpy.types.Operator):
    bl_idname = "bim.contract_container"
    bl_label = "Contract Container"
    bl_description = "Contract the hierarchy\nALT+CLICK to recursively contract"
    bl_options = {"REGISTER", "UNDO"}
    container: bpy.props.IntProperty()
    is_recursive: bpy.props.BoolProperty(name="Is Recursive", default=False, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.alt:
            self.is_recursive = True
        return self.execute(context)

    def execute(self, context):
        core.contract_container(
            tool.Spatial, container=tool.Ifc.get().by_id(self.container), is_recursive=self.is_recursive
        )
        return {"FINISHED"}


class ExpandContainer(bpy.types.Operator):
    bl_idname = "bim.expand_container"
    bl_label = "Expand Container"
    bl_description = "Expand the hierarchy\nALT+CLICK to recursively contract"
    bl_options = {"REGISTER", "UNDO"}
    container: bpy.props.IntProperty()
    is_recursive: bpy.props.BoolProperty(name="Is Recursive", default=False, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.alt:
            self.is_recursive = True
        return self.execute(context)

    def execute(self, context):
        core.expand_container(
            tool.Spatial, container=tool.Ifc.get().by_id(self.container), is_recursive=self.is_recursive
        )
        return {"FINISHED"}


class DeleteContainer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.delete_container"
    bl_label = "Delete Container"
    bl_options = {"REGISTER", "UNDO"}
    container: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        props = tool.Spatial.get_spatial_props()
        active_container = props.active_container
        if not active_container:
            cls.poll_message_set("No active container.")
            return False
        if active_container.ifc_class == "IfcProject":
            cls.poll_message_set("Cannot delete IfcProject.")
            return False
        return True

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


class SelectDecomposedElement(bpy.types.Operator):
    bl_idname = "bim.select_decomposed_element"
    bl_label = "Select Decomposed Element"
    bl_options = {"REGISTER", "UNDO"}
    element: bpy.props.IntProperty()

    def execute(self, context):
        if self.element:
            core.select_decomposed_element(tool.Ifc, tool.Spatial, element=tool.Ifc.get().by_id(self.element))
        return {"FINISHED"}


class SelectDecomposedElements(bpy.types.Operator):
    bl_idname = "bim.select_decomposed_elements"
    bl_label = "Select Elements"
    bl_options = {"REGISTER", "UNDO"}
    should_filter: bpy.props.BoolProperty(name="Should Filter", default=True, options={"SKIP_SAVE"})
    container: bpy.props.IntProperty()
    is_recursive: bpy.props.BoolProperty(default=True, options={"SKIP_SAVE"})

    @classmethod
    def description(cls, context, operator):
        return (
            "Select the active item"
            + "\nALT+CLICK to select all listed elements.\nCTRL + CLICK to select only one level deep"
        )

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE":
            if event.alt:
                self.should_filter = False
            if event.ctrl:
                self.is_recursive = False
        return self.execute(context)

    def execute(self, context):
        tool.Spatial.select_products(tool.Spatial.get_filtered_elements(self.should_filter, self.is_recursive))

        # Make selected active element in list, the active object
        props = tool.Spatial.get_spatial_props()
        active_element = props.active_element
        if active_element and active_element.type == "OCCURRENCE":
            ifc_file = tool.Ifc.get()
            ifc_entity = ifc_file.by_id(active_element.ifc_definition_id)
            obj = tool.Ifc.get_object(ifc_entity)
            if obj:
                context.view_layer.objects.active = obj
                obj.select_set(True)
        return {"FINISHED"}


class SetDefaultContainer(bpy.types.Operator):
    bl_idname = "bim.set_default_container"
    bl_label = "Set Default Container"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Set this as the default container that all new elements will be contained in"
    container: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        props = tool.Spatial.get_spatial_props()
        active_container = props.active_container
        if not active_container:
            cls.poll_message_set("No active container.")
            return False
        if active_container.ifc_class == "IfcProject":
            cls.poll_message_set("Cannot set default IfcProject as default container.")
            return False
        return True

    def execute(self, context):
        core.set_default_container(tool.Spatial, container=tool.Ifc.get().by_id(self.container))
        core.set_orientation_slot(tool.Spatial, container=tool.Ifc.get().by_id(self.container))
        return {"FINISHED"}


class SetContainerVisibility(bpy.types.Operator):
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

    def execute(self, context):
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
        return {"FINISHED"}


class SetElementVisibility(bpy.types.Operator):
    bl_idname = "bim.set_element_visibility"
    bl_label = "Set Element Visibility"
    bl_options = {"REGISTER", "UNDO"}
    container: bpy.props.IntProperty()
    should_filter: bpy.props.BoolProperty(name="Should Filter", default=True, options={"SKIP_SAVE"})
    mode: bpy.props.StringProperty(name="Mode")

    @classmethod
    def description(cls, context, operator):
        if operator.mode == "HIDE":
            return "Hides the active item\n" + "ALT+CLICK to hide all listed items"
        elif operator.mode == "SHOW":
            return "Shows the active item\n" + "ALT+CLICK to show all listed items"
        return "Isolate the active item\n" + "ALT+CLICK to isolate all listed items"

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.alt:
            self.should_filter = False
        return self.execute(context)

    def execute(self, context):
        if self.mode == "ISOLATE":
            context_override = tool.Blender.get_viewport_context()
            with context.temp_override(**context_override):
                bpy.ops.object.hide_view_set(unselected=True)
                bpy.ops.object.hide_view_set(unselected=False)
            should_hide = False
        else:
            should_hide = self.mode == "HIDE"

        for element in tool.Spatial.get_filtered_elements(self.should_filter):
            if obj := tool.Ifc.get_object(element):
                obj.hide_set(should_hide)
                for collection in obj.users_collection:
                    collection.hide_viewport = False
        return {"FINISHED"}


class ToggleGrids(bpy.types.Operator):
    bl_idname = "bim.toggle_grids"
    bl_label = "Toggle Grids"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Show or hide grids and grid axes"
    is_visible: bpy.props.BoolProperty(name="Is Visible", default=False, options={"SKIP_SAVE"})

    def execute(self, context):
        tool.Spatial.set_grid_visibility(self.is_visible)
        return {"FINISHED"}


class ToggleSpatialElements(bpy.types.Operator):
    bl_idname = "bim.toggle_spatial_elements"
    bl_label = "Toggle Spatial Elements"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Show or hide spatial elements, such as buildings, sites, etc"
    is_visible: bpy.props.BoolProperty(name="Is Visible", default=False, options={"SKIP_SAVE"})

    def execute(self, context):
        tool.Spatial.set_space_visibility(self.is_visible)
        return {"FINISHED"}
