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

import bpy
import bonsai.core.tool
import bonsai.tool as tool
import ifcopenshell.util.element
from typing import Union


class Collector(bonsai.core.tool.Collector):
    @classmethod
    def assign(cls, obj: bpy.types.Object, should_clean_users_collection=True) -> None:
        """Links an object to an appropriate Blender collection."""
        if should_clean_users_collection:
            for users_collection in obj.users_collection:
                if obj.BIMObjectProperties.collection == users_collection:
                    continue
                # Users are free to user extra collections for their own
                # purposes except for the reserved keyword "Ifc" and
                # "Collection" (which is the default collection that comes with
                # a Blender session)
                if "Ifc" in users_collection.name or users_collection.name == "Collection":
                    users_collection.objects.unlink(obj)

        element = tool.Ifc.get_entity(obj)
        assert element

        # Note that tool.Geometry.is_locked is only checked within the if
        # statements for efficiency as it is a slow check.

        if element.is_a("IfcGridAxis"):
            if tool.Geometry.is_locked(element):
                tool.Geometry.lock_object(obj)
            element = (element.PartOfU or element.PartOfV or element.PartOfW)[0]
        elif element.is_a("IfcGrid"):
            if tool.Geometry.is_locked(element):
                tool.Geometry.lock_object(obj)

        if element.is_a("IfcProject"):
            if tool.Geometry.is_locked(element):
                tool.Geometry.lock_object(obj)
            if collection := cls._create_own_collection(obj):
                cls.link_collection_object_safe(collection, obj)
                cls.link_collection_child_safe(bpy.context.scene.collection, collection)
        elif element.is_a("IfcTypeProduct"):
            collection = cls._create_project_child_collection("IfcTypeProduct")
            cls.link_collection_object_safe(collection, obj)
        elif element.is_a("IfcOpeningElement"):
            collection = cls._create_project_child_collection("IfcOpeningElement")
            cls.link_collection_object_safe(collection, obj)
        elif element.is_a("IfcSpace"):
            collection = cls._create_project_child_collection("IfcSpace")
            cls.link_collection_object_safe(collection, obj)
        elif element.is_a("IfcStructuralItem"):
            collection = cls._create_project_child_collection("IfcStructuralItem")
            cls.link_collection_object_safe(collection, obj)
        elif element.is_a("IfcLinearPositioningElement"):
            if tool.Geometry.is_locked(element):
                tool.Geometry.lock_object(obj)
            collection = cls._create_project_child_collection("IfcLinearPositioningElement")
            cls.link_collection_object_safe(collection, obj)
        elif element.is_a("IfcReferent"):
            if tool.Geometry.is_locked(element):
                tool.Geometry.lock_object(obj)
            collection = cls._create_project_child_collection("IfcReferent")
            cls.link_collection_object_safe(collection, obj)
        elif tool.Ifc.get_schema() == "IFC2X3" and element.is_a("IfcSpatialStructureElement"):
            if tool.Geometry.is_locked(element):
                tool.Geometry.lock_object(obj)
            if collection := cls._create_own_collection(obj):
                cls.link_collection_object_safe(collection, obj)
                project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
                cls.link_collection_child_safe(project_obj.BIMObjectProperties.collection, collection)
        elif (
            tool.Ifc.get_schema() != "IFC2X3"
            and element.is_a("IfcSpatialElement")
            and not element.is_a("IfcSpatialZone")
        ):
            if tool.Geometry.is_locked(element):
                tool.Geometry.lock_object(obj)
            if collection := cls._create_own_collection(obj):
                cls.link_collection_object_safe(collection, obj)
                project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
                cls.link_collection_child_safe(project_obj.BIMObjectProperties.collection, collection)
        elif element.is_a("IfcAnnotation") and element.ObjectType == "DRAWING":
            if collection := cls._create_own_collection(obj):
                cls.link_collection_object_safe(collection, obj)
                project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
                cls.link_collection_child_safe(project_obj.BIMObjectProperties.collection, collection)
        elif element.is_a("IfcAnnotation") and (drawing_obj := cls.get_annotation_drawing_obj(element)):
            cls.link_collection_object_safe(drawing_obj.BIMObjectProperties.collection, obj)
        elif container := ifcopenshell.util.element.get_container(element):
            while container.is_a("IfcSpace"):
                container = ifcopenshell.util.element.get_aggregate(container)
            container_obj = tool.Ifc.get_object(container)
            if not (collection := container_obj.BIMObjectProperties.collection):
                cls.assign(container_obj)
                collection = container_obj.BIMObjectProperties.collection
            cls.link_collection_object_safe(collection, obj)
        else:
            collection = cls._create_project_child_collection("Unsorted")
            cls.link_collection_object_safe(collection, obj)

    @classmethod
    def _create_project_child_collection(cls, name: str) -> bpy.types.Collection:
        """get or create new collection inside project"""
        if collection := bpy.data.collections.get(name):
            return collection
        collection = bpy.data.collections.new(name)
        project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
        project_obj.BIMObjectProperties.collection.children.link(collection)
        if layer_collection := tool.Blender.get_layer_collection(collection):
            cls.set_layer_collection_visibility(layer_collection)
        return collection

    @classmethod
    def _create_own_collection(cls, obj: bpy.types.Object) -> bpy.types.Collection:
        """get or create own collection for the element"""
        if obj.BIMObjectProperties.collection:
            obj.BIMObjectProperties.collection.name = obj.name
            return
        collection = bpy.data.collections.new(obj.name)
        obj.BIMObjectProperties.collection = collection
        collection.BIMCollectionProperties.obj = obj
        return collection

    @classmethod
    def get_annotation_drawing_obj(cls, element: ifcopenshell.entity_instance) -> bpy.types.Object | None:
        for rel in element.HasAssignments or []:
            if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.ObjectType == "DRAWING":
                for related_object in rel.RelatedObjects:
                    if related_object.is_a("IfcAnnotation") and related_object.ObjectType == "DRAWING":
                        return tool.Ifc.get_object(related_object)

    @classmethod
    def link_collection_object_safe(cls, collection: bpy.types.Collection, obj: bpy.types.Object) -> None:
        # Catching an exception is 10x faster than doing collection.objects.find
        try:
            collection.objects.link(obj)
        except:
            pass

    @classmethod
    def link_collection_child_safe(cls, collection: bpy.types.Collection, child: bpy.types.Collection) -> None:
        try:
            collection.children.link(child)
        except:
            pass

    @classmethod
    def set_layer_collection_visibility(cls, layer_collection):
        name = layer_collection.collection.name
        if name in (
            "IfcTypeProduct",
            "IfcStructuralItem",
            "Unsorted",
        ):
            layer_collection.hide_viewport = True
        elif name.startswith("IfcAnnotation"):
            layer_collection.hide_viewport = True
        else:
            layer_collection.hide_viewport = False

    @classmethod
    def reset_default_visibility(cls):
        project = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
        project_collection = project.BIMObjectProperties.collection
        for layer_collection in bpy.context.view_layer.layer_collection.children:
            if layer_collection.collection == project_collection:
                for layer_collection2 in layer_collection.children:
                    cls.set_layer_collection_visibility(layer_collection2)
