# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations
import bpy
import bmesh
import shapely
import shapely.ops
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.classification
import ifcopenshell.util.shape_builder
import ifcopenshell.util.type
import ifcopenshell.util.unit
import bonsai.core.type
import bonsai.core.tool
import bonsai.core.root
import bonsai.core.spatial
import bonsai.core.geometry
import bonsai.core.unit
import bonsai.tool as tool
import json
import numpy as np
from math import pi
from mathutils import Vector, Matrix
from shapely import Polygon
from typing import Generator, Optional, Union, Literal, List, Any, Iterable, TYPE_CHECKING
from collections import defaultdict
from natsort import natsorted

if TYPE_CHECKING:
    from bonsai.bim.module.spatial.prop import (
        BIMGridProperties,
        BIMSpatialDecompositionProperties,
        BIMObjectSpatialProperties,
    )


class Spatial(bonsai.core.tool.Spatial):
    @classmethod
    def get_spatial_props(cls) -> BIMSpatialDecompositionProperties:
        return bpy.context.scene.BIMSpatialDecompositionProperties

    @classmethod
    def get_object_spatial_props(cls, obj: bpy.types.Object) -> BIMObjectSpatialProperties:
        return obj.BIMObjectSpatialProperties

    @classmethod
    def get_grid_props(cls) -> BIMGridProperties:
        return bpy.context.scene.BIMGridProperties

    @classmethod
    def can_contain(cls, container: ifcopenshell.entity_instance, element_obj: Union[bpy.types.Object, None]) -> bool:
        if not (element := tool.Ifc.get_entity(element_obj)):
            return False
        if tool.Ifc.get_schema() == "IFC2X3":
            if not container.is_a("IfcSpatialStructureElement"):
                return False
        else:
            if not container.is_a("IfcSpatialStructureElement") and not container.is_a(
                "IfcExternalSpatialStructureElement"
            ):
                return False
        if not hasattr(element, "ContainedInStructure"):
            return False
        return True

    @classmethod
    def can_reference(
        cls, structure: Union[ifcopenshell.entity_instance, None], element: Union[ifcopenshell.entity_instance, None]
    ) -> bool:
        if not structure or not element:
            return False
        if tool.Ifc.get_schema() == "IFC2X3":
            if not structure.is_a("IfcSpatialStructureElement"):
                return False
        else:
            if not structure.is_a("IfcSpatialElement"):
                return False
        if not hasattr(element, "ReferencedInStructures"):
            return False
        return True

    @classmethod
    def disable_editing(cls, obj: bpy.types.Object) -> None:
        props = cls.get_object_spatial_props(obj)
        props.is_editing = False

    @classmethod
    def duplicate_object_and_data(cls, obj: bpy.types.Object) -> bpy.types.Object:
        new_obj = obj.copy()
        if obj.data:
            new_obj.data = obj.data.copy()
        return new_obj

    @classmethod
    def enable_editing(cls, obj: bpy.types.Object) -> None:
        props = cls.get_object_spatial_props(obj)
        props.is_editing = True
        props.relating_container_object = None

    @classmethod
    def get_container(cls, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        return ifcopenshell.util.element.get_container(element)

    @classmethod
    def get_decomposed_elements(cls, container: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.element.get_decomposition(container)

    @classmethod
    def get_object_matrix(cls, obj: bpy.types.Object) -> Matrix:
        return obj.matrix_world

    @classmethod
    def get_relative_object_matrix(cls, target_obj: bpy.types.Object, relative_to_obj: bpy.types.Object) -> Matrix:
        return relative_to_obj.matrix_world.inverted() @ target_obj.matrix_world

    @classmethod
    def run_root_copy_class(cls, obj: bpy.types.Object) -> ifcopenshell.entity_instance:
        return bonsai.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=obj)

    @classmethod
    def run_spatial_assign_container(
        cls, container: ifcopenshell.entity_instance, element_obj: bpy.types.Object
    ) -> Union[ifcopenshell.entity_instance, None]:
        return bonsai.core.spatial.assign_container(
            tool.Ifc, tool.Collector, tool.Spatial, container=container, element_obj=element_obj
        )

    @classmethod
    def run_spatial_import_spatial_decomposition(cls) -> None:
        return bonsai.core.spatial.import_spatial_decomposition(tool.Spatial)

    @classmethod
    def select_object(cls, obj: bpy.types.Object) -> None:
        tool.Blender.select_object(obj)

    @classmethod
    def set_active_object(cls, obj: bpy.types.Object, selection_mode: str = "ADD") -> None:
        if selection_mode == "ADD":
            tool.Blender.set_active_object(obj)
        elif selection_mode == "REMOVE":
            tool.Blender.deselect_object(obj)
        else:
            tool.Blender.select_and_activate_single_object(bpy.context, obj)

    @classmethod
    def set_relative_object_matrix(
        cls, target_obj: bpy.types.Object, relative_to_obj: bpy.types.Object, matrix: Matrix
    ) -> None:
        target_obj.matrix_world = relative_to_obj.matrix_world @ matrix

    @classmethod
    def select_products(cls, products: Iterable[ifcopenshell.entity_instance], unhide: bool = False) -> None:
        bpy.ops.object.select_all(action="DESELECT")
        for product in products:
            obj = tool.Ifc.get_object(product)
            if obj and bpy.context.view_layer.objects.get(obj.name):
                if unhide:
                    obj.hide_set(False)
                obj.select_set(True)

    @classmethod
    def filter_products(
        cls, products: list[ifcopenshell.entity_instance], action: Literal["select", "isolate", "unhide", "hide"]
    ) -> None:
        objects = [obj for product in products if (obj := tool.Ifc.get_object(product))]
        if action == "select":
            [obj.select_set(True) for obj in objects]
        elif action == "isolate":
            [obj.hide_set(False) for obj in objects if bpy.context.view_layer.objects.get(obj.name)]
            [
                obj.hide_set(True)
                for obj in bpy.context.visible_objects
                if not obj in objects and bpy.context.view_layer.objects.get(obj.name)
            ]  # this is slow
        elif action == "unhide":
            [obj.hide_set(False) for obj in objects if bpy.context.view_layer.objects.get(obj.name)]
        elif action == "hide":
            [obj.hide_set(True) for obj in objects if bpy.context.view_layer.objects.get(obj.name)]

    @classmethod
    def deselect_objects(cls) -> None:
        [obj.select_set(False) for obj in bpy.context.selected_objects]

    @classmethod
    def show_scene_objects(cls) -> None:
        [
            obj.hide_set(False)
            for obj in bpy.data.scenes["Scene"].objects
            if bpy.context.view_layer.objects.get(obj.name)
        ]

    @classmethod
    def get_selected_products(cls) -> Generator[ifcopenshell.entity_instance, None, None]:
        for obj in bpy.context.selected_objects:
            entity = tool.Ifc.get_entity(obj)
            if entity and entity.is_a("IfcProduct"):
                yield entity

    @classmethod
    def get_selected_product_types(cls) -> Generator[ifcopenshell.entity_instance, None, None]:
        for obj in tool.Blender.get_selected_objects():
            entity = tool.Ifc.get_entity(obj)
            if entity and entity.is_a("IfcTypeProduct"):
                yield entity

    @classmethod
    def copy_xy(cls, src_obj: bpy.types.Object, destination_obj: bpy.types.Object) -> None:
        src_obj.location.xy = destination_obj.location.xy

    @classmethod
    def get_container_elements_grouped_by_classification(cls, container: ifcopenshell.entity_instance) -> dict:
        props = cls.get_spatial_props()
        results = {}
        if props.should_include_children:
            elements = ifcopenshell.util.element.get_decomposition(container, is_recursive=True)
        else:
            elements = set(ifcopenshell.util.element.get_contained(container))
            for e in elements:
                elements.update(ifcopenshell.util.element.get_decomposition(e))
        flat_results: dict[str, Any] = {}
        reference_names: dict[str, str] = {}
        for element in elements:
            if element.is_a("IfcOpeningElement") or tool.Root.is_spatial_element(element):
                continue
            references = ifcopenshell.util.classification.get_references(element)
            if not references:
                flat_results.setdefault("Unclassified", []).append(element)
            else:
                for reference in references:
                    identification = reference[1] or ""
                    reference_names[identification] = reference[2]
                    flat_results.setdefault(identification, []).append(element)

        for flat_key in sorted(flat_results.keys()):
            current_results = results

            while True:
                has_parent = None
                for key in current_results:
                    if flat_key.startswith(key):
                        has_parent = True
                        new_current_results = current_results[key]["children"]
                        break
                if has_parent:
                    current_results = new_current_results
                else:
                    break

            current_results[flat_key] = {
                "Name": "Unclassified" if flat_key == "Unclassified" else reference_names[flat_key],
                "elements": flat_results[flat_key],
                "children": {},
            }

        return results

    @classmethod
    def get_container_elements_grouped_by_type(cls, container: ifcopenshell.entity_instance) -> dict:
        props = cls.get_spatial_props()
        results: defaultdict[str, dict[int, Any]] = defaultdict(dict)
        if props.should_include_children:
            elements = ifcopenshell.util.element.get_decomposition(container, is_recursive=True)
        else:
            queue = list(set(ifcopenshell.util.element.get_contained(container)))
            elements = set()
            while queue:
                item = queue.pop()
                elements.add(item)
                queue.extend(ifcopenshell.util.element.get_decomposition(item))
        for element in elements:
            if element.is_a("IfcOpeningElement") or tool.Root.is_spatial_element(element):
                continue
            element_type = ifcopenshell.util.element.get_type(element)
            ifc_class = element.is_a()
            ifc_definition_id = element_type.id() if element_type else 0
            type_name = (
                element_type.is_a() + "/" + (element_type.Name or "Unnamed")
                if element_type
                else f"Untyped {element.is_a()}"
            )
            class_data = results.setdefault(ifc_class, {})
            type_data = class_data.setdefault(ifc_definition_id, {"type_name": type_name, "elements": []})
            type_data["elements"].append(element)
        return results

    @classmethod
    def load_contained_elements(cls) -> None:
        props = cls.get_spatial_props()
        props.elements.clear()
        if not (container := props.active_container):
            return

        container = tool.Ifc.get().by_id(container.ifc_definition_id)
        if props.element_mode == "TYPE":
            cls.load_contained_elements_by_type(container)
        elif props.element_mode == "DECOMPOSITION":
            cls.load_contained_elements_by_decomposition(container)
        elif props.element_mode == "CLASSIFICATION":
            cls.load_contained_elements_by_classification(container)

    @classmethod
    def load_contained_elements_by_type(cls, container: ifcopenshell.entity_instance) -> None:
        props = cls.get_spatial_props()
        results = cls.get_container_elements_grouped_by_type(container)

        expanded_elements = json.loads(props.expanded_elements)
        expanded_classes = expanded_elements.get("CLASS", [])
        expanded_ifc_ids = expanded_elements.get("IFC_ID", [])
        expanded_untyped = expanded_elements.get("UNTYPED_CLASSES", [])
        expanded_classes_r = expanded_elements.get("CLASS_R", [])

        total_elements = 0
        for ifc_class in sorted(results.keys()):
            new = props.elements.add()
            new.name = ifc_class
            new.type = "CLASS"
            new.has_children = True
            class_is_expanded = ifc_class in expanded_classes
            class_is_expanded_r = ifc_class in expanded_classes_r
            new.is_expanded = class_is_expanded or class_is_expanded_r
            total = 0
            for ifc_definition_id in sorted(
                results[ifc_class].keys(), key=lambda x: results[ifc_class][x]["type_name"]
            ):
                type_data = results[ifc_class][ifc_definition_id]
                total2 = len(type_data["elements"])
                if new.is_expanded:
                    new2 = props.elements.add()
                    new2.type = "TYPE"
                    new2.has_children = True
                    new2.level = 1
                    new2.name = type_data["type_name"]
                    new2.ifc_class = ifc_class
                    new2.total = total2
                    new2.ifc_definition_id = ifc_definition_id
                    if ifc_definition_id == 0:
                        type_is_expanded = ifc_class in expanded_untyped
                    else:
                        type_is_expanded = ifc_definition_id in expanded_ifc_ids
                    new2.is_expanded = type_is_expanded or class_is_expanded_r

                    if new2.is_expanded:
                        for element in type_data["elements"]:
                            occurrence = props.elements.add()
                            occurrence.name = element.Name or "Unnamed"
                            occurrence.level = 2
                            occurrence.ifc_definition_id = element.id()
                            occurrence.type = "OCCURRENCE"

                total += total2
            new.total = total
            total_elements += total

        props.total_elements = total_elements

    @classmethod
    def load_contained_elements_by_decomposition(cls, container: ifcopenshell.entity_instance) -> None:
        props = cls.get_spatial_props()
        expanded_elements = json.loads(props.expanded_elements)
        expanded_ifc_ids = expanded_elements.get("IFC_ID", [])

        def add_elements(elements, level=0):
            for element in sorted(elements, key=lambda x: f"{x.is_a()}/{x.Name or 'Unnamed'}"):
                if not props.should_include_children and tool.Root.is_spatial_element(element):
                    continue
                ifc_definition_id = element.id()
                new = props.elements.add()
                new.name = f"{element.is_a()}/{element.Name or 'Unnamed'}"
                new.level = level
                new.ifc_definition_id = ifc_definition_id
                new.type = "OCCURRENCE"
                children = [
                    e
                    for e in ifcopenshell.util.element.get_decomposition(element, is_recursive=False)
                    if not e.is_a("IfcFeatureElement")
                ]
                if children:
                    new.has_children = True
                    new.total = len(children)
                    if ifc_definition_id in expanded_ifc_ids:
                        new.is_expanded = True
                        add_elements(children, level=level + 1)

        elements = ifcopenshell.util.element.get_decomposition(container, is_recursive=False)
        add_elements(elements)

    @classmethod
    def load_contained_elements_by_classification(cls, container: ifcopenshell.entity_instance) -> None:
        props = cls.get_spatial_props()
        expanded_elements = json.loads(props.expanded_elements)
        expanded_classifications = expanded_elements.get("CLASSIFICATION", [])
        expanded_classifications_r = expanded_elements.get("CLASSIFICATION_R", [])

        def add_elements(results, level=0):
            for identification in sorted(results.keys()):
                data = results[identification]
                new = props.elements.add()
                new.name = f"{identification}:{data['Name']}"
                new.type = "CLASSIFICATION"
                new.identification = identification
                new.has_children = True
                new.level = level

                is_expanded = identification in expanded_classifications
                is_expanded_r = any([c for c in expanded_classifications_r if identification.startswith(c)])

                if is_expanded or is_expanded_r:
                    new.is_expanded = True
                    add_elements(data["children"], level=level + 1)

                    for element in sorted(data["elements"], key=lambda x: f"{x.is_a()}/{x.Name or 'Unnamed'}"):
                        new2 = props.elements.add()
                        new2.name = f"{element.is_a()}/{element.Name or 'Unnamed'}"
                        new2.type = "OCCURRENCE"
                        new2.level = level + 1
                        new2.ifc_definition_id = element.id()

        results = cls.get_container_elements_grouped_by_classification(container)
        add_elements(results)

    @classmethod
    def filter_elements(
        cls,
        elements: Iterable[ifcopenshell.entity_instance],
        ifc_class: str | None,
        relating_type: ifcopenshell.entity_instance | None,
        is_untyped: bool,
        keyword: str | None,
    ) -> filter[ifcopenshell.entity_instance]:
        keyword = keyword.lower() if keyword else keyword

        def filter_element(element: ifcopenshell.entity_instance) -> bool:
            if ifc_class:
                if not element.is_a(ifc_class):
                    return False
            element_type = ifcopenshell.util.element.get_type(element)
            if relating_type:
                if relating_type != element_type:
                    return False
            if is_untyped:
                if element_type is not None:
                    return False
            if keyword:
                type_name = getattr(element_type, "Name", "") or ""
                if keyword not in f"{element.is_a()} {type_name}".lower():
                    return False
            return True

        return filter(filter_element, elements)

    @classmethod
    def import_spatial_decomposition(cls) -> None:
        props = cls.get_spatial_props()
        previous_container_index = props.active_container_index
        props.containers.clear()
        cls.contracted_containers = json.loads(props.contracted_containers)
        cls.import_spatial_element(tool.Ifc.get().by_type("IfcProject")[0], 0)
        props.active_container_index = min(previous_container_index, len(props.containers) - 1)

    @classmethod
    def import_spatial_element(cls, element: ifcopenshell.entity_instance, level_index: int) -> None:
        if not element.is_a("IfcProject") and not tool.Root.is_spatial_element(element):
            return
        props = cls.get_spatial_props()
        new = props.containers.add()
        new.ifc_class = element.is_a()
        new["name"] = element.Name or "Unnamed"
        new.description = element.Description or ""
        new.long_name = element.LongName or ""
        if not element.is_a("IfcProject"):
            elevation = ifcopenshell.util.placement.get_storey_elevation(element)
            new["elevation"] = tool.Unit.format_value(elevation)
        new.is_expanded = element.id() not in cls.contracted_containers
        new.level_index = level_index
        children = ifcopenshell.util.element.get_parts(element)
        if children:
            children = natsorted(
                children,
                key=lambda element: (ifcopenshell.util.placement.get_storey_elevation(element), element.Name),
            )
        new.has_children = bool(children)
        new.ifc_definition_id = element.id()
        if new.is_expanded:
            for child in children or []:
                cls.import_spatial_element(child, level_index + 1)

    @classmethod
    def create_orientation_slot(cls, container: ifcopenshell.entity_instance) -> None:
        active_slot = bpy.context.scene.transform_orientation_slots[0]
        placement = container.ObjectPlacement
        combined_matrix = ifcopenshell.util.placement.get_local_placement(placement)[:3, :3]

        if np.allclose(combined_matrix, np.eye(3), atol=1e-6):
            # this spatial element has global orientation
            active_slot.type = "GLOBAL"
            return
        elif (
            hasattr(container, "Decomposes")
            and container.Decomposes
            and hasattr(container.Decomposes[0].RelatingObject, "ObjectPlacement")
        ):
            # this spatial element is part of a decomposition
            parent_placement = container.Decomposes[0].RelatingObject.ObjectPlacement
            parent_matrix = ifcopenshell.util.placement.get_local_placement(parent_placement)[:3, :3]
            if np.allclose(combined_matrix, parent_matrix, atol=1e-6):
                # this spatial element has the same orientation as its parent
                cls.create_orientation_slot(container=container.Decomposes[0].RelatingObject)
                return

        # this spatial element has a unique orientation
        orientation_name = container.is_a() + "/" + container.Name

        # stash selected objects
        active_object = bpy.context.view_layer.objects.active
        selected_objects = list(bpy.context.view_layer.objects.selected)

        # bpy.ops.transform.create_orientation() requires a dummy object
        bpy.ops.object.empty_add(type="PLAIN_AXES")
        bpy.ops.transform.create_orientation(name=orientation_name, overwrite=True)
        active_slot.type = orientation_name
        active_slot.custom_orientation.matrix = np.linalg.inv(combined_matrix)

        # delete dummy object
        bpy.ops.object.delete()

        # reinstate selected objects
        for obj in selected_objects:
            obj.select_set(True)
        if active_object:
            bpy.context.view_layer.objects.active = active_object

    @classmethod
    def edit_container_name(cls, container: ifcopenshell.entity_instance, name: str) -> None:
        tool.Ifc.run("attribute.edit_attributes", product=container, attributes={"Name": name})

    @classmethod
    def get_active_container(cls) -> Union[ifcopenshell.entity_instance, None]:
        props = cls.get_spatial_props()
        if props.active_container_index < len(props.containers):
            container = tool.Ifc.get().by_id(props.containers[props.active_container_index].ifc_definition_id)
            return container

    @classmethod
    def contract_container(cls, container: ifcopenshell.entity_instance, is_recursive: bool) -> None:
        props = cls.get_spatial_props()
        contracted_containers = set(json.loads(props.contracted_containers))
        queue = [container]
        while queue:
            item = queue.pop()
            if is_recursive and (children := ifcopenshell.util.element.get_parts(item)):
                queue.extend(children)
            contracted_containers.add(item.id())
        props.contracted_containers = json.dumps(list(contracted_containers))

    @classmethod
    def expand_container(cls, container: ifcopenshell.entity_instance, is_recursive: bool) -> None:
        props = cls.get_spatial_props()
        contracted_containers = set(json.loads(props.contracted_containers))
        queue = [container]
        while queue:
            item = queue.pop()
            if is_recursive and (children := ifcopenshell.util.element.get_parts(item)):
                queue.extend(children)
            contracted_containers.discard(item.id())
        props.contracted_containers = json.dumps(list(contracted_containers))

    @classmethod
    def toggle_container_element(cls, element_index: int, is_recursive: bool) -> None:
        props = cls.get_spatial_props()
        if props.element_mode == "TYPE":
            cls.toggle_container_element_by_type(element_index, is_recursive)
        elif props.element_mode == "DECOMPOSITION":
            cls.toggle_container_element_by_decomposition(element_index, is_recursive)
        elif props.element_mode == "CLASSIFICATION":
            cls.toggle_container_element_by_classification(element_index, is_recursive)

    @classmethod
    def toggle_container_element_by_type(cls, element_index: int, is_recursive: bool) -> None:
        props = cls.get_spatial_props()
        expanded_elements: dict[str, list[Union[str, int]]] = json.loads(props.expanded_elements)

        element = props.elements[element_index]
        if element.type == "CLASS":
            element_type = "CLASS"
            filtered_item = element.name
        elif element.type == "TYPE":
            if element.ifc_definition_id == 0:
                element_type = "UNTYPED_CLASSES"
                filtered_item = element.ifc_class
            else:
                element_type = "IFC_ID"
                filtered_item = element.ifc_definition_id
        else:
            return

        expanded_elements_list: list[Union[str, int]] = expanded_elements.setdefault(element_type, [])
        if filtered_item in expanded_elements_list:
            expanded_elements_list.remove(filtered_item)
            should_expand = False
        else:
            expanded_elements_list.append(filtered_item)
            should_expand = True

        if is_recursive and element.type == "CLASS":
            container = tool.Ifc.get().by_id(props.active_container.ifc_definition_id)
            results = cls.get_container_elements_grouped_by_type(container)
            for ifc_class in results.keys():
                if ifc_class != element.name:
                    continue
                for ifc_definition_id in results[ifc_class].keys():
                    if ifc_definition_id == 0:
                        element_type = "UNTYPED_CLASSES"
                        filtered_item = ifc_class
                    else:
                        element_type = "IFC_ID"
                        filtered_item = ifc_definition_id

                    expanded_elements_list = expanded_elements.setdefault(element_type, [])
                    if should_expand is False and filtered_item in expanded_elements_list:
                        expanded_elements_list.remove(filtered_item)
                    elif should_expand is True and filtered_item not in expanded_elements_list:
                        expanded_elements_list.append(filtered_item)

        props.expanded_elements = json.dumps(expanded_elements)

    @classmethod
    def toggle_container_element_by_decomposition(cls, element_index: int, is_recursive: bool) -> None:
        props = cls.get_spatial_props()
        element = props.elements[element_index]
        expanded_elements: dict[str, list[Union[str, int]]] = json.loads(props.expanded_elements)
        expanded_elements_list: list[Union[str, int]] = expanded_elements.setdefault("IFC_ID", [])
        ifc_definition_id = element.ifc_definition_id
        if ifc_definition_id in expanded_elements_list:
            expanded_elements_list.remove(ifc_definition_id)
            should_expand = False
        else:
            expanded_elements_list.append(ifc_definition_id)
            should_expand = True

        if is_recursive:
            queue = [tool.Ifc.get().by_id(ifc_definition_id)]
            while queue:
                element = queue.pop()
                children = [
                    e
                    for e in ifcopenshell.util.element.get_decomposition(element, is_recursive=False)
                    if not e.is_a("IfcFeatureElement")
                ]
                ifc_definition_id = element.id()
                if children:
                    if should_expand is False and ifc_definition_id in expanded_elements_list:
                        expanded_elements_list.remove(ifc_definition_id)
                    elif should_expand is True and ifc_definition_id not in expanded_elements_list:
                        expanded_elements_list.append(ifc_definition_id)
                    queue.extend(children)

        props.expanded_elements = json.dumps(expanded_elements)

    @classmethod
    def toggle_container_element_by_classification(cls, element_index: int, is_recursive: bool) -> None:
        props = cls.get_spatial_props()
        expanded_elements: dict[str, list[str]] = json.loads(props.expanded_elements)
        expanded_elements_list: list[str] = expanded_elements.setdefault("CLASSIFICATION", [])

        element = props.elements[element_index]
        identification = element.identification

        if identification in expanded_elements_list:
            expanded_elements_list.remove(identification)
            should_expand = False
        else:
            expanded_elements_list.append(identification)
            should_expand = True

        if is_recursive:
            expanded_elements_list = expanded_elements.setdefault("CLASSIFICATION_R", [])
            if should_expand is False and identification in expanded_elements_list:
                expanded_elements_list.remove(identification)
            elif should_expand is True and identification not in expanded_elements_list:
                expanded_elements_list.append(identification)

        props.expanded_elements = json.dumps(expanded_elements)

    # HERE STARTS SPATIAL TOOL

    @classmethod
    def is_bounding_class(cls, visible_element: ifcopenshell.entity_instance) -> bool:
        for ifc_class in ["IfcWall", "IfcColumn", "IfcMember", "IfcVirtualElement", "IfcPlate"]:
            if visible_element.is_a(ifc_class):
                return True
        return False

    @classmethod
    def get_space_polygon_from_context_visible_objects(
        cls, x: float, y: float
    ) -> Union[shapely.Polygon, Literal["NO POLYGONS FOUND", "NO POLYGON FOR POINT"]]:
        boundary_lines = cls.get_boundary_lines_from_context_visible_objects()
        unioned_boundaries = shapely.union_all(shapely.GeometryCollection(boundary_lines))
        closed_polygons = shapely.polygonize(unioned_boundaries.geoms)
        if not closed_polygons:
            return "NO POLYGONS FOUND"
        space_polygon = None
        for polygon in closed_polygons.geoms:
            if shapely.contains_xy(polygon, x, y):
                space_polygon = shapely.force_3d(polygon)
        if space_polygon is None:
            return "NO POLYGON FOR POINT"
        return space_polygon

    @classmethod
    def debug_shape(cls, foo: shapely.Polygon) -> None:
        coords = [(p[0], p[1], 0) for p in foo.exterior.coords]
        mesh = bpy.data.meshes.new(name="NewMesh")
        bm = bmesh.new()
        for coord in coords:
            bm.verts.new(coord)
        bm.verts.ensure_lookup_table()
        bm.faces.new(bm.verts)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new("NewObject", mesh)
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.update()

    @classmethod
    def debug_line(cls, start: Vector, end: Vector) -> None:
        coords = [start, end]
        mesh = bpy.data.meshes.new(name="NewMesh")
        bm = bmesh.new()
        for coord in coords:
            bm.verts.new(coord)
        bm.verts.ensure_lookup_table()
        bm.edges.new(bm.verts)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new("NewLine", mesh)
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.update()

    @classmethod
    def get_boundary_lines_from_context_visible_objects(cls) -> list[shapely.LineString]:
        props = tool.Model.get_model_props()
        calculation_rl = props.rl3
        container = tool.Root.get_default_container()
        container_obj = tool.Ifc.get_object(container)
        cut_point = container_obj.matrix_world.translation.copy() + Vector((0, 0, calculation_rl))
        cut_normal = Vector((0, 0, 1))
        boundary_lines = []

        for obj in bpy.context.visible_objects:
            visible_element = tool.Ifc.get_entity(obj)

            old_mesh = obj.data
            if (
                not visible_element
                or not isinstance(old_mesh, bpy.types.Mesh)
                or not cls.is_bounding_class(visible_element)
                or not tool.Drawing.is_intersecting_plane(obj, cut_point, cut_normal)
            ):
                continue

            old_mesh = obj.data
            assert isinstance(old_mesh, bpy.types.Mesh)
            if visible_element.HasOpenings:
                new_mesh = cls.get_gross_mesh_from_element(visible_element)
            else:
                new_mesh = old_mesh.copy()
            obj.data = new_mesh

            # Boundary objects are likely triangulated. If a triangulated quad
            # is bisected by our plane, we end up with two lines instead of
            # one. This makes shapely's job much harder (since shapely is very
            # exact with its coordinates). As a result, let's limited dissolve
            # prior to bisecting.
            bm = bmesh.new()
            bm.from_mesh(new_mesh)
            bmesh.ops.dissolve_limit(bm, angle_limit=0.02, verts=bm.verts, edges=bm.edges)
            bm.to_mesh(new_mesh)
            new_mesh.update()
            bm.free()

            local_cut_point = obj.matrix_world.inverted() @ cut_point
            local_cut_normal = obj.matrix_world.inverted().to_quaternion() @ cut_normal
            verts, edges = tool.Drawing.bisect_mesh_with_plane(obj, local_cut_point, local_cut_normal)

            # Restore the original mesh
            obj.data = old_mesh
            bpy.data.meshes.remove(new_mesh)

            for edge in edges or []:
                # Rounding is necessary to ensure coincident points are coincident
                start = [round(x, 3) for x in verts[edge[0]]]
                end = [round(x, 3) for x in verts[edge[1]]]
                if start == end:
                    continue
                # Extension by 50mm is necessary to ensure lines overlap with other diagonal lines
                # This also closes small but likely irrelevant gaps for space generation.
                start, end = tool.Drawing.extend_line(start, end, 0.05)
                boundary_lines.append(shapely.LineString([start, end]))

        return boundary_lines

    @classmethod
    def get_gross_mesh_from_element(cls, visible_element: ifcopenshell.entity_instance) -> bpy.types.Mesh:
        gross_settings = ifcopenshell.geom.settings()
        gross_settings.set("disable-opening-subtractions", True)
        new_mesh = cls.create_mesh_from_shape(ifcopenshell.geom.create_shape(gross_settings, visible_element))
        return new_mesh

    @classmethod
    def create_mesh_from_shape(cls, shape: ifcopenshell.geom.ShapeElementType) -> bpy.types.Mesh:
        geometry = shape.geometry
        return tool.Loader.create_mesh_from_shape(geometry)

    @classmethod
    def get_x_y_z_h_mat_from_obj(cls, obj: bpy.types.Object) -> tuple[float, float, float, float, Matrix]:
        """
        `x`, `y` - object's center XY in world space;\n
        `z` - object's local Z- in world space;\n
        `h` - object's Z dimension;\n
        `mat` - object's matrix
        """
        mat = obj.matrix_world
        local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
        global_bbox_center = mat @ local_bbox_center
        x = global_bbox_center.x
        y = global_bbox_center.y
        z = (mat @ Vector(obj.bound_box[0])).z

        h = obj.dimensions.z
        return x, y, z, h, mat

    @classmethod
    def get_x_y_z_h_mat_from_cursor(cls) -> tuple[float, float, float, float, Matrix]:
        """
        `x`, `y` - from cursor;\n
        `z` - from default container Z location (if set);\n
        `h` - default value of 3;\n
        `mat` - identity matrix
        """
        x, y, z = bpy.context.scene.cursor.location.xyz
        if tool.Root.get_default_container():
            z = tool.Root.get_default_container_elevation()
        mat = Matrix()
        h = 3
        return x, y, z, h, mat

    @classmethod
    def get_union_shape_from_selected_objects(cls) -> Polygon:
        selected_objects = bpy.context.selected_objects
        boundary_elements = cls.get_boundary_elements(selected_objects)
        polys = cls.get_polygons(boundary_elements)
        converted_tolerance = cls.get_converted_tolerance(tolerance_si=0.03)
        union = shapely.ops.unary_union(polys).buffer(
            converted_tolerance,
            cap_style=shapely.constructive.BufferCapStyle.flat,
            join_style=shapely.constructive.BufferJoinStyle.mitre,
        )
        union = cls.get_purged_inner_holes_poly(
            union_geom=union, min_area=cls.get_converted_tolerance(tolerance_si=0.1)
        )
        return union

    @classmethod
    def get_boundary_elements(cls, selected_objects: list[bpy.types.Object]) -> list[ifcopenshell.entity_instance]:
        boundary_elements = []
        for obj in selected_objects:
            subelement = tool.Ifc.get_entity(obj)
            if subelement.is_a("IfcWall") or subelement.is_a("IfcColumn"):
                boundary_elements.append(subelement)
        return boundary_elements

    @classmethod
    def get_polygons(cls, boundary_elements: list[ifcopenshell.entity_instance]) -> list[Polygon]:
        polys = []
        for boundary_element in boundary_elements:
            obj = tool.Ifc.get_object(boundary_element)
            if not obj:
                continue
            points = []
            base = cls.get_obj_base_points(obj)
            for index in ["low_left", "low_right", "high_right", "high_left"]:
                point = base[index]
                points.append(point)

            polys.append(Polygon(points))
        return polys

    @classmethod
    def get_obj_base_points(cls, obj: bpy.types.Object) -> dict[str, tuple[float, float]]:
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        bbox_ws = [obj.matrix_world @ Vector(v) / si_conversion for v in obj.bound_box]
        return {
            "low_left": (bbox_ws[0].x, bbox_ws[0].y),
            "high_left": (bbox_ws[3].x, bbox_ws[3].y),
            "low_right": (bbox_ws[4].x, bbox_ws[4].y),
            "high_right": (bbox_ws[7].x, bbox_ws[7].y),
        }

    @classmethod
    def get_converted_tolerance(cls, tolerance_si: float) -> float:
        model = tool.Ifc.get()
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(model)
        return tolerance_si / si_conversion

    @classmethod
    def get_purged_inner_holes_poly(cls, union_geom: Polygon, min_area: float) -> Polygon:
        interiors_list = []

        if union_geom.geom_type == "MultiPolygon":
            for poly in union_geom.geoms:
                interiors_list = cls.get_poly_valid_interior_list(
                    poly=poly, min_area=min_area, interiors_list=interiors_list
                )

            new_poly = Polygon(poly.exterior.coords, holes=interiors_list)

        if union_geom.geom_type == "Polygon":
            interiors_list = cls.get_poly_valid_interior_list(
                poly=union_geom, min_area=min_area, interiors_list=interiors_list
            )
            new_poly = Polygon(union_geom.exterior.coords, holes=interiors_list)

        return new_poly

    @classmethod
    def get_poly_valid_interior_list(cls, poly: Polygon, min_area: float, interiors_list: list[shapely.LinearRing]):
        for interior in poly.interiors:
            p = Polygon(interior)
            if p.area >= min_area:
                interiors_list.append(interior)
        return interiors_list

    @classmethod
    def get_buffered_poly_from_linear_ring(cls, linear_ring: shapely.LinearRing) -> Polygon:
        poly = Polygon(linear_ring)
        converted_tolerance = cls.get_converted_tolerance(tolerance_si=0.03)
        poly = poly.buffer(
            converted_tolerance,
            #            single_sided=True,
            cap_style=shapely.BufferCapStyle.flat,
            join_style=shapely.BufferJoinStyle.mitre,
        )
        return poly

    @classmethod
    def get_bmesh_from_polygon(cls, poly: Polygon, h: float, polygon_is_si: bool = False) -> bmesh.types.BMesh:
        """
        :param h: Height, in meters.
        :param polygon_is_si: Should be True if `poly` is defined in meters.
        """
        mat = Matrix()
        bm = bmesh.new()
        bm.verts.index_update()
        bm.edges.index_update()

        mat_invert = mat.inverted()
        si_conversion = 1.0 if polygon_is_si else ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        new_verts = [
            # bm.verts.new(mat_invert @ (Vector([v[0], v[1], 0]) * si_conversion)) for v in poly.exterior.coords[0:-1]
            bm.verts.new(mat_invert @ (Vector([v[0], v[1], 0]) * si_conversion))
            for v in shapely.get_exterior_ring(poly).coords[0:-1]
        ]
        [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(new_verts) - 1)]
        bm.edges.new((new_verts[len(new_verts) - 1], new_verts[0]))

        bm.verts.index_update()
        bm.edges.index_update()

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.triangle_fill(bm, edges=bm.edges)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 5, verts=bm.verts, edges=bm.edges)

        if h != 0:
            extrusion = bmesh.ops.extrude_face_region(bm, geom=bm.faces)
            extruded_verts = [g for g in extrusion["geom"] if isinstance(g, bmesh.types.BMVert)]
            bmesh.ops.translate(bm, vec=[0.0, 0.0, h], verts=extruded_verts)

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

        return bm

    @classmethod
    def get_named_obj_from_bmesh(cls, name: str, bmesh: bmesh.types.BMesh) -> bpy.types.Object:
        mesh = cls.get_named_mesh_from_bmesh(name, bmesh)
        obj = cls.get_named_obj_from_mesh(name, mesh)
        return obj

    @classmethod
    def get_named_obj_from_mesh(cls, name: str, mesh: bpy.types.Mesh) -> bpy.types.Object:
        obj = bpy.data.objects.new(name, mesh)
        return obj

    @classmethod
    def get_named_mesh_from_bmesh(cls, name: str, bmesh: bmesh.types.BMesh) -> bpy.types.Mesh:
        mesh = bpy.data.meshes.new(name=name)
        bmesh.to_mesh(mesh)
        bmesh.free()
        return mesh

    @classmethod
    def get_transformed_mesh_from_local_to_global(cls, mesh: bpy.types.Mesh) -> bpy.types.Mesh:
        active_obj = cls.get_active_obj()
        mat = active_obj.matrix_world
        mesh.transform(mat.inverted())
        mesh.update()
        return mesh

    @classmethod
    def edit_active_space_obj_from_mesh(cls, mesh: bpy.types.Mesh) -> None:
        active_obj = bpy.context.active_object
        old_mesh = active_obj.data
        old_mesh_name = old_mesh.name
        assert active_obj and isinstance(old_mesh, bpy.types.Mesh)
        tool.Geometry.get_mesh_props(mesh).ifc_definition_id = tool.Geometry.get_mesh_props(old_mesh).ifc_definition_id
        tool.Geometry.change_object_data(active_obj, mesh, is_global=True)
        tool.Ifc.edit(active_obj)
        tool.Blender.remove_data_block(old_mesh)
        # Rename after old mesh is removed to avoid .001 suffix.
        mesh.name = old_mesh_name

    @classmethod
    def set_obj_origin_to_bboxcenter(cls, obj: bpy.types.Object) -> None:
        mat = obj.matrix_world
        inverted = mat.inverted()
        local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
        global_bbox_center = mat @ local_bbox_center

        oldLoc = obj.location
        newLoc = global_bbox_center
        diff = newLoc - oldLoc
        for vert in obj.data.vertices:
            aux_vector = mat @ vert.co
            aux_vector = aux_vector - diff
            vert.co = inverted @ aux_vector
        obj.location = newLoc

    @classmethod
    def set_obj_origin_to_bboxcenter_and_zero_elevation(cls, obj: bpy.types.Object) -> None:
        mat = obj.matrix_world
        inverted = mat.inverted()
        local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
        global_bbox_center = mat @ local_bbox_center
        global_obj_origin = global_bbox_center
        global_obj_origin.z = 0

        oldLoc = obj.location
        newLoc = global_obj_origin
        diff = newLoc - oldLoc
        for vert in obj.data.vertices:
            aux_vector = mat @ vert.co
            aux_vector = aux_vector - diff
            vert.co = inverted @ aux_vector
        obj.location = newLoc

    @classmethod
    def set_obj_origin_to_cursor_position_and_zero_elevation(cls, obj: bpy.types.Object) -> None:
        mat = obj.matrix_world
        inverted = mat.inverted()

        x, y = bpy.context.scene.cursor.location.xy
        z = 0

        oldLoc = obj.location
        newLoc = Vector((x, y, z))
        diff = newLoc - oldLoc
        for vert in obj.data.vertices:
            aux_vector = mat @ vert.co
            aux_vector = aux_vector - diff
            vert.co = inverted @ aux_vector
        obj.location = newLoc

    @classmethod
    def get_selected_objects(cls) -> list[bpy.types.Object]:
        return bpy.context.selected_objects

    @classmethod
    def get_active_obj(cls) -> Union[bpy.types.Object, None]:
        return bpy.context.active_object

    @classmethod
    def get_active_obj_z(cls) -> float:
        return bpy.context.active_object.matrix_world.translation.z

    @classmethod
    def get_active_obj_height(cls) -> float:
        height = bpy.context.active_object.dimensions.z
        return height

    @classmethod
    def get_relating_type_id(cls) -> int:
        props = tool.Model.get_model_props()
        relating_type_id = props.relating_type_id
        return relating_type_id

    @classmethod
    def translate_obj_to_z_location(cls, obj: bpy.types.Object, z: float) -> None:
        if z != 0:
            obj.location = obj.location + Vector((0, 0, z))

    @classmethod
    def get_2d_vertices_from_obj(cls, obj: bpy.types.Object) -> list[tuple]:
        points = []
        vectors = [v.co for v in obj.data.vertices.values()]
        for vector in vectors:
            points.append(vector.xy)

        points.append(vectors[0].xy)
        return points

    @classmethod
    def get_scaled_2d_vertices(cls, points: list[Vector]) -> list[tuple[float, float]]:
        model = tool.Ifc.get()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(model)
        _points = []
        for p in points:
            _p = list(p)
            _p[0] /= unit_scale
            _p[1] /= unit_scale
            _points.append(_p)
        return _points

    @classmethod
    def assign_swept_area_outer_curve_from_2d_vertices(cls, obj: bpy.types.Object, vertices: list[Vector]) -> None:
        body = cls.get_body_representation(obj)
        model = tool.Ifc.get()
        extrusion = tool.Model.get_extrusion(body)
        area = extrusion.SweptArea
        old_area = area.OuterCurve

        builder = ifcopenshell.util.shape_builder.ShapeBuilder(model)
        outer_curve = builder.polyline(vertices, closed=True)

        area.OuterCurve = outer_curve
        ifcopenshell.util.element.remove_deep2(tool.Ifc.get(), old_area)

    @classmethod
    def get_body_representation(cls, obj: bpy.types.Object) -> Union[ifcopenshell.entity_instance, None]:
        element = tool.Ifc.get_entity(obj)
        return ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")

    @classmethod
    def assign_ifcspace_class_to_obj(cls, obj: bpy.types.Object) -> None:
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcSpace")

    @classmethod
    def assign_type_to_obj(cls, obj: bpy.types.Object) -> None:
        props = tool.Model.get_model_props()
        relating_type_id = props.relating_type_id
        relating_type = tool.Ifc.get().by_id(int(relating_type_id))
        ifc_class = relating_type.is_a()
        instance_class = ifcopenshell.util.type.get_applicable_entities(ifc_class, tool.Ifc.get().schema)[0]
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class=instance_class)
        element = tool.Ifc.get_entity(obj)
        tool.Ifc.run("type.assign_type", related_objects=[element], relating_type=relating_type)

    @classmethod
    def assign_relating_type_to_element(
        cls,
        ifc: tool.Ifc,
        type: tool.Type,
        element: ifcopenshell.entity_instance,
        relating_type: ifcopenshell.entity_instance,
    ) -> None:
        bonsai.core.type.assign_type(ifc, type, element=element, type=relating_type)

    @classmethod
    def regen_obj_representation(cls, obj: bpy.types.Object, body: ifcopenshell.entity_instance) -> None:
        bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=body,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
        )

    @classmethod
    def toggle_spaces_visibility_wired_and_textured(cls, spaces: list[ifcopenshell.entity_instance]) -> None:
        first_obj = tool.Ifc.get_object(spaces[0])
        assert isinstance(first_obj, bpy.types.Object)
        obj: bpy.types.Object
        if first_obj.display_type == "TEXTURED":
            for space in spaces:
                obj = tool.Ifc.get_object(space)
                obj.show_wire = True
                obj.display_type = "WIRE"
            return

        elif first_obj.display_type == "WIRE":
            for space in spaces:
                obj = tool.Ifc.get_object(space)
                obj.show_wire = False
                obj.display_type = "TEXTURED"
            return

    @classmethod
    def toggle_hide_spaces(cls, spaces: list[ifcopenshell.entity_instance]) -> None:
        first_obj = tool.Ifc.get_object(spaces[0])
        assert isinstance(first_obj, bpy.types.Object)
        obj: bpy.types.Object
        if first_obj.hide_get() == False:
            for space in spaces:
                obj = tool.Ifc.get_object(space)
                obj.hide_set(True)
            return

        elif first_obj.hide_get() == True:
            for space in spaces:
                obj = tool.Ifc.get_object(space)
                obj.hide_set(False)

    @classmethod
    def set_default_container(cls, container: ifcopenshell.entity_instance) -> None:
        from bonsai.bim.module.spatial.data import SpatialDecompositionData

        props = cls.get_spatial_props()
        props.default_container = container.id()
        SpatialDecompositionData.data["default_container"] = SpatialDecompositionData.default_container()

        project = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
        project_collection = tool.Blender.get_object_bim_props(project).collection
        obj = tool.Ifc.get_object(container)
        if obj and (collection := tool.Blender.get_object_bim_props(obj).collection):
            for layer_collection in bpy.context.view_layer.layer_collection.children:
                if layer_collection.collection == project_collection:
                    for layer_collection2 in layer_collection.children:
                        if layer_collection2.collection == collection:
                            bpy.context.view_layer.active_layer_collection = layer_collection2
                            break

    @classmethod
    def guess_default_container(cls) -> Optional[ifcopenshell.entity_instance]:
        project = tool.Ifc.get().by_type("IfcProject")[0]
        subelement = None
        # We try to priorise the first Site > Building > Storey as a convention for vertical projects
        for subelement in ifcopenshell.util.element.get_parts(project):
            if subelement.is_a("IfcSite"):
                for subelement2 in ifcopenshell.util.element.get_parts(subelement):
                    if subelement2.is_a("IfcBuilding"):
                        for subelement3 in ifcopenshell.util.element.get_parts(subelement2):
                            if subelement3.is_a("IfcBuildingStorey"):
                                return subelement3
        if subelement:
            return subelement
        return None

    @classmethod
    def get_selected_containers(cls) -> List[ifcopenshell.entity_instance]:
        results = []
        for obj in tool.Blender.get_selected_objects():
            if (element := tool.Ifc.get_entity(obj)) and tool.Root.is_spatial_element(element):
                results.append(element)
        return results

    @classmethod
    def get_selected_objects_without_containers(cls) -> list[bpy.types.Object]:
        """Get selected objects skipping spatial elements.

        Useful for operators that are using selected objects to identify selected containers.
        Note that those operators are typically have a limitation since they can't tell
        objects to operate on from containers that should be used in the operation.

        E.g. we cannot bim.copy_to_container containers to other containers."""
        results: list[bpy.types.Object] = []
        for obj in tool.Blender.get_selected_objects():
            if (element := tool.Ifc.get_entity(obj)) and not tool.Root.is_spatial_element(element):
                results.append(obj)
        return results

    @classmethod
    def set_target_container_as_default(cls) -> None:
        if (
            (container := tool.Root.get_default_container())
            and (container_obj := tool.Ifc.get_object(container))
            and (obj := bpy.context.active_object)
        ):
            props = cls.get_object_spatial_props(obj)
            props.container_obj = container_obj

    @classmethod
    def get_filtered_elements(cls, should_filter: bool = True) -> Iterable[ifcopenshell.entity_instance]:
        ifc_file = tool.Ifc.get()
        props = cls.get_spatial_props()
        container = ifc_file.by_id(props.active_container.ifc_definition_id)
        element_filter = props.element_filter
        active_element = props.active_element

        if not should_filter:
            if props.should_include_children:
                elements = ifcopenshell.util.element.get_decomposition(container, is_recursive=True)
            else:
                queue = list(set(ifcopenshell.util.element.get_contained(container)))
                elements = set()
                while queue:
                    item = queue.pop()
                    elements.add(item)
                    queue.extend(ifcopenshell.util.element.get_decomposition(item))
            if not element_filter:
                return elements

            keyword = element_filter.lower()
            if props.element_mode == "TYPE":
                filtered_occurrences = set()
                filtered_classes = set()
                filtered_types = set()
                for item in props.elements:
                    if item.type == "CLASS" and not item.is_expanded and keyword in item.name.lower():
                        filtered_classes.add(item.name)
                    elif item.type == "TYPE" and not item.is_expanded and keyword in item.name.lower():
                        if item.ifc_definition_id:
                            filtered_types.add(ifc_file.by_id(item.ifc_definition_id))
                        else:
                            filtered_types.add(item.name.split(" ")[1])
                    elif item.type == "OCCURRENCE" and keyword in item.name.lower():
                        filtered_occurrences.add(ifc_file.by_id(item.ifc_definition_id))
                return {
                    e
                    for e in elements
                    if e.is_a() in filtered_classes
                    or ((e_type := ifcopenshell.util.element.get_type(e)) and e_type in filtered_types)
                    or (not e_type and e.is_a() in filtered_types)
                } | filtered_occurrences
            elif props.element_mode == "DECOMPOSITION":
                return [ifc_file.by_id(i.ifc_definition_id) for i in props.elements if keyword in i.name.lower()]
            elif props.element_mode == "CLASSIFICATION":
                filtered_classifications = set()
                filtered_occurrences = set()
                for item in props.elements:
                    if item.type == "CLASSIFICATION" and not item.is_expanded and keyword in item.name.lower():
                        filtered_classifications.add(item.identification)
                    elif item.type == "OCCURRENCE" and keyword in item.name.lower():
                        filtered_occurrences.add(ifc_file.by_id(item.ifc_definition_id))
                for element in elements:
                    if refs := ifcopenshell.util.classification.get_references(element):
                        for ref in refs:
                            for filtered_classification in filtered_classifications:
                                if ref[1].startswith(filtered_classification):
                                    filtered_occurrences.add(element)
                    elif "Unclassified" in filtered_classifications:
                        filtered_occurrences.add(element)
                return filtered_occurrences
            return elements

        if not active_element:
            return []

        if props.element_mode == "TYPE":
            if active_element.type == "OCCURRENCE":
                return {ifc_file.by_id(active_element.ifc_definition_id)}

            ifc_class = relating_type = None
            is_untyped = False

            if active_element.type == "CLASS":
                ifc_class = active_element.name
            elif active_element.type == "TYPE":
                ifc_class = active_element.ifc_class
                if ifc_id := active_element.ifc_definition_id:
                    relating_type = ifc_file.by_id(ifc_id)

            if props.should_include_children:
                elements = ifcopenshell.util.element.get_decomposition(container, is_recursive=True)
            else:
                elements = set(ifcopenshell.util.element.get_contained(container))
                for e in elements:
                    elements.update(ifcopenshell.util.element.get_decomposition(e))
            return cls.filter_elements(elements, ifc_class, relating_type, is_untyped, element_filter)
        elif props.element_mode == "DECOMPOSITION":
            occurrence = ifc_file.by_id(active_element.ifc_definition_id)
            elements = ifcopenshell.util.element.get_decomposition(occurrence, is_recursive=True)
            elements.add(occurrence)
            return elements
        elif props.element_mode == "CLASSIFICATION":
            if active_element.type == "OCCURRENCE":
                return {ifc_file.by_id(active_element.ifc_definition_id)}

            if active_element.type == "CLASSIFICATION":
                identification = active_element.identification
                if props.should_include_children:
                    elements = ifcopenshell.util.element.get_decomposition(container, is_recursive=True)
                else:
                    elements = set(ifcopenshell.util.element.get_contained(container))
                    for e in elements:
                        elements.update(ifcopenshell.util.element.get_decomposition(e))

                def filter_element(element: ifcopenshell.entity_instance) -> bool:
                    references = ifcopenshell.util.classification.get_references(element)
                    if identification == "Unclassified":
                        if not references:
                            return True
                    elif any([r for r in references if r[1].startswith(identification)]):
                        return True
                    return False

                return filter(filter_element, elements)
