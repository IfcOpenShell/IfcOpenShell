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

        if element.is_a("IfcGridAxis"):
            element = (element.PartOfU or element.PartOfV or element.PartOfW)[0]

        if element.is_a("IfcProject"):
            if collection := cls._create_own_collection(obj):
                cls.link_to_collection_safe(obj, collection)
                cls.link_to_collection_safe(collection, bpy.context.scene.collection)
        elif element.is_a("IfcTypeProduct"):
            collection = cls._create_project_child_collection("IfcTypeProduct")
            cls.link_to_collection_safe(obj, collection)
        elif element.is_a("IfcOpeningElement"):
            collection = cls._create_project_child_collection("IfcOpeningElement")
            cls.link_to_collection_safe(obj, collection)
        elif element.is_a("IfcStructuralItem"):
            collection = cls._create_project_child_collection("IfcStructuralItem")
            cls.link_to_collection_safe(obj, collection)
        elif element.is_a("IfcLinearPositioningElement"):
            collection = cls._create_project_child_collection("IfcLinearPositioningElement")
            cls.link_to_collection_safe(obj, collection)
        elif element.is_a("IfcReferent"):
            collection = cls._create_project_child_collection("IfcReferent")
            cls.link_to_collection_safe(obj, collection)
        elif tool.Ifc.get_schema() == "IFC2X3" and element.is_a("IfcSpatialStructureElement"):
            if collection := cls._create_own_collection(obj):
                cls.link_to_collection_safe(obj, collection)
                project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
                cls.link_to_collection_safe(collection, project_obj.BIMObjectProperties.collection)
        elif (
            tool.Ifc.get_schema() != "IFC2X3"
            and element.is_a("IfcSpatialElement")
            and not element.is_a("IfcSpatialZone")
        ):
            if collection := cls._create_own_collection(obj):
                cls.link_to_collection_safe(obj, collection)
                project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
                cls.link_to_collection_safe(collection, project_obj.BIMObjectProperties.collection)
        elif element.is_a("IfcAnnotation") and element.ObjectType == "DRAWING":
            if collection := cls._create_own_collection(obj):
                cls.link_to_collection_safe(obj, collection)
                project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
                cls.link_to_collection_safe(collection, project_obj.BIMObjectProperties.collection)
        elif element.is_a("IfcAnnotation") and (drawing_obj := cls.get_annotation_drawing_obj(element)):
            cls.link_to_collection_safe(obj, drawing_obj.BIMObjectProperties.collection)
        elif container := ifcopenshell.util.element.get_container(element):
            container_obj = tool.Ifc.get_object(container)
            if not (collection := container_obj.BIMObjectProperties.collection):
                cls.assign(container_obj)
                collection = container_obj.BIMObjectProperties.collection
            cls.link_to_collection_safe(obj, collection)
        else:
            collection = cls._create_project_child_collection("Unsorted")
            cls.link_to_collection_safe(obj, collection)

    @classmethod
    def _create_project_child_collection(cls, name: str) -> bpy.types.Collection:
        """get or create new collection inside project"""
        collection = bpy.data.collections.get(name)
        if not collection:
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
    def link_to_collection_safe(
        cls, obj_or_col: Union[bpy.types.Object, bpy.types.Collection], collection: bpy.types.Collection
    ) -> None:
        """Link `obj_or_col` (an object or a collection) to the `collection`
        if `obj_or_col` is not part of that collection already.

        Method is needed to avoid RuntimeErrors like below that occur if you link object/collection
        to the collection directly and they are already part of that collection.
        RuntimeError: Error: Object 'xxx' already in collection 'xxx'.
        """
        # TODO: Maybe just catching RuntimeError is faster?
        if isinstance(obj_or_col, bpy.types.Object):
            if collection.objects.find(obj_or_col.name) != -1:
                return
            collection.objects.link(obj_or_col)
            return

        if collection.children.find(obj_or_col.name) != -1:
            return
        collection.children.link(obj_or_col)

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
