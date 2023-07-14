# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import blenderbim.core.tool
import blenderbim.core.root
import blenderbim.core.spatial
import blenderbim.tool as tool
import json


class Spatial(blenderbim.core.tool.Spatial):
    @classmethod
    def can_contain(cls, structure_obj, element_obj):
        structure = tool.Ifc.get_entity(structure_obj)
        element = tool.Ifc.get_entity(element_obj)
        if not structure or not element:
            return False
        if tool.Ifc.get_schema() == "IFC2X3":
            if not structure.is_a("IfcSpatialStructureElement"):
                return False
        else:
            if not structure.is_a("IfcSpatialStructureElement") and not structure.is_a(
                "IfcExternalSpatialStructureElement"
            ):
                return False
        if not hasattr(element, "ContainedInStructure"):
            return False
        return True

    @classmethod
    def can_reference(cls, structure, element):
        if not structure or not element:
            return False
        if tool.Ifc.get_schema() == "IFC2X3":
            if not structure.is_a("IfcSpatialStructureElement"):
                return False
        else:
            if not structure.is_a() in ("IfcSpatialElement", "IfcSpatialStructureElement"):
                return False
        if not hasattr(element, "ReferencedInStructures"):
            return False
        return True

    @classmethod
    def disable_editing(cls, obj):
        obj.BIMObjectSpatialProperties.is_editing = False

    @classmethod
    def duplicate_object_and_data(cls, obj):
        new_obj = obj.copy()
        if obj.data:
            new_obj.data = obj.data.copy()
        return new_obj

    @classmethod
    def enable_editing(cls, obj):
        obj.BIMObjectSpatialProperties.is_editing = True

    @classmethod
    def get_container(cls, element):
        return ifcopenshell.util.element.get_container(element)

    @classmethod
    def get_decomposed_elements(cls, container):
        return ifcopenshell.util.element.get_decomposition(container)

    @classmethod
    def get_object_matrix(cls, obj):
        return obj.matrix_world

    @classmethod
    def get_relative_object_matrix(cls, target_obj, relative_to_obj):
        return relative_to_obj.matrix_world.inverted() @ target_obj.matrix_world

    @classmethod
    def import_containers(cls, parent=None):
        props = bpy.context.scene.BIMSpatialProperties
        props.containers.clear()

        if not parent:
            parent = tool.Ifc.get().by_type("IfcProject")[0]

        props.active_container_id = parent.id()

        for rel in parent.IsDecomposedBy or []:
            related_objects = []
            for element in rel.RelatedObjects:
                related_objects.append((element, ifcopenshell.util.placement.get_storey_elevation(element)))
            related_objects = sorted(related_objects, key=lambda e: e[1])
            for element in related_objects:
                element = element[0]
                new = props.containers.add()
                new.name = element.Name or "Unnamed"
                new.long_name = element.LongName or ""
                new.has_decomposition = bool(element.IsDecomposedBy)
                new.ifc_definition_id = element.id()
                new.elevation = element[1]

    @classmethod
    def run_root_copy_class(cls, obj=None):
        return blenderbim.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=obj)

    @classmethod
    def run_spatial_assign_container(cls, structure_obj=None, element_obj=None):
        return blenderbim.core.spatial.assign_container(
            tool.Ifc, tool.Collector, tool.Spatial, structure_obj=structure_obj, element_obj=element_obj
        )

    @classmethod
    def select_object(cls, obj):
        obj.select_set(True)

    @classmethod
    def set_active_object(cls, obj):
        bpy.context.view_layer.objects.active = obj
        cls.select_object(obj)

    @classmethod
    def set_relative_object_matrix(cls, target_obj, relative_to_obj, matrix):
        target_obj.matrix_world = relative_to_obj.matrix_world @ matrix

    @classmethod
    def select_products(cls, products, unhide=False):
        bpy.ops.object.select_all(action="DESELECT")
        for product in products:
            obj = tool.Ifc.get_object(product)
            if obj and bpy.context.view_layer.objects.get(obj.name):
                obj.select_set(True)
                if unhide:
                    obj.hide_set(False)

    @classmethod
    def filter_products(cls, products, action):
        objects = [tool.Ifc.get_object(product) for product in products if tool.Ifc.get_object(product)]
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
    def deselect_objects(cls):
        [obj.select_set(False) for obj in bpy.context.selected_objects]
        # bpy.ops.object.select_all(action='DESELECT')

    @classmethod
    def show_scene_objects(cls):
        [
            obj.hide_set(False)
            for obj in bpy.data.scenes["Scene"].objects
            if bpy.context.view_layer.objects.get(obj.name)
        ]

    @classmethod
    def get_selected_products(cls):
        for obj in bpy.context.selected_objects:
            entity = tool.Ifc.get_entity(obj)
            if entity and entity.is_a("IfcProduct"):
                yield entity

    @classmethod
    def get_selected_product_types(cls):
        for obj in bpy.context.selected_objects:
            entity = tool.Ifc.get_entity(obj)
            if entity and entity.is_a("IfcTypeProduct"):
                yield entity

    @classmethod
    def copy_xy(cls, src_obj, destination_obj):
        z = src_obj.location[2]
        src_obj.location = (destination_obj.location[0], destination_obj.location[1], z)

    @classmethod
    def load_container_manager(cls):
        cls.props = bpy.context.scene.BIMSpatialManagerProperties
        cls.props.containers.clear()
        cls.contracted_containers = json.loads(cls.props.contracted_containers)
        cls.props.is_container_update_enabled = False
        parent = tool.Ifc.get().by_type("IfcProject")[0]

        for object in ifcopenshell.util.element.get_parts(parent) or []:
            if object.is_a() in ("IfcSpatialElement", "IfcSpatialStructureElement"):
                cls.create_new_storey_li(object, 0)
        cls.props.is_container_update_enabled = True

    @classmethod
    def create_new_storey_li(cls, element, level_index):
        new = cls.props.containers.add()
        new.name = element.Name or "Unnamed"
        new.long_name = element.LongName or ""
        new.has_decomposition = bool(element.IsDecomposedBy)
        new.ifc_definition_id = element.id()
        new.elevation = ifcopenshell.util.placement.get_storey_elevation(element)

        new.is_expanded = element.id() not in cls.contracted_containers
        new.level_index = level_index
        if new.has_decomposition:
            new.has_children = True
            if new.is_expanded:
                for related_object in ifcopenshell.util.element.get_parts(element) or []:
                    if related_object.is_a() in ("IfcSpatialElement", "IfcSpatialStructureElement"):
                        cls.create_new_storey_li(related_object, level_index + 1)

    @classmethod
    def edit_container_attributes(cls, entity):
        obj = tool.Ifc.get_object(entity)
        blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        name = bpy.context.scene.BIMSpatialManagerProperties.container_name
        if name != entity.Name:
            cls.edit_container_name(entity, name)

    @classmethod
    def edit_container_name(cls, container, name):
        tool.Ifc.run("attribute.edit_attributes", product=container, attributes={"Name": name})

    @classmethod
    def get_active_container(cls):
        props = bpy.context.scene.BIMSpatialManagerProperties
        if props.active_container_index < len(props.containers):
            container = tool.Ifc.get().by_id(props.containers[props.active_container_index].ifc_definition_id)
            return container

    @classmethod
    def contract_container(cls, container):
        props = bpy.context.scene.BIMSpatialManagerProperties
        contracted_containers = json.loads(props.contracted_containers)
        contracted_containers.append(container.id())
        props.contracted_containers = json.dumps(contracted_containers)

    @classmethod
    def expand_container(cls, container):
        props = bpy.context.scene.BIMSpatialManagerProperties
        contracted_containers = json.loads(props.contracted_containers)
        contracted_containers.remove(container.id())
        props.contracted_containers = json.dumps(contracted_containers)
