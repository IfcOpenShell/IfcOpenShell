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
import ifcopenshell.util.element

import blenderbim.core.tool
import blenderbim.core.spatial
import blenderbim.core.aggregate
import blenderbim.tool as tool
from typing import Union


class Collector(blenderbim.core.tool.Collector):
    @classmethod
    def assign(cls, obj: bpy.types.Object) -> None:
        """link object and it's owned collection to the proper collection
        and unlink them from any other"""
        element = tool.Ifc.get_entity(obj)

        object_collection = None
        collection_collection = None

        object_collection = cls._get_own_collection(element, obj)
        if object_collection:
            collection_collection = cls._get_collection(element, obj)
        else:
            object_collection = cls._get_collection(element, obj)

        # NOTE: calling `obj.users_collection` is expensive in large projects
        # since it's iterating over all collections under the hood

        # ensure object is linked only to object_collection
        if obj.users_collection != (object_collection,):
            for collection in obj.users_collection:
                collection.objects.unlink(obj)
            if object_collection is not None:
                object_collection.objects.link(obj)

        # ensure object_collection is linked only to collection_collection
        if collection_collection and collection_collection.children.find(object_collection.name) == -1:
            if bpy.context.scene.collection.children.find(object_collection.name) != -1:
                bpy.context.scene.collection.children.unlink(object_collection)
            for collection in bpy.data.collections:
                if collection.children.find(object_collection.name) != -1:
                    collection.children.unlink(object_collection)
            collection_collection.children.link(object_collection)

        # If an aggregate or nested host loses all its children, it no longer needs its own collection
        if obj.BIMObjectProperties.collection and obj.BIMObjectProperties.collection != object_collection:
            bpy.data.collections.remove(obj.BIMObjectProperties.collection)

    @classmethod
    def _get_own_collection(
        cls, element: ifcopenshell.entity_instance, obj: bpy.types.Object
    ) -> Union[bpy.types.Collection, None]:
        """get or create own collection for the element if it's neccessary for it's type"""
        if element.is_a("IfcProject"):
            return cls._create_own_collection(obj)

        if tool.Ifc.get_schema() == "IFC2X3":
            if element.is_a("IfcSpatialStructureElement"):
                return cls._create_own_collection(obj)
        else:
            if element.is_a("IfcSpatialStructureElement") or element.is_a("IfcExternalSpatialStructureElement"):
                return cls._create_own_collection(obj)

        if element.is_a("IfcGrid"):
            return cls._create_own_collection(obj)

        if element.is_a("IfcGridAxis"):
            if element.PartOfU:
                grid = element.PartOfU[0]
                axes = "UAxes"
            elif element.PartOfV:
                grid = element.PartOfV[0]
                axes = "VAxes"
            elif element.PartOfW:
                grid = element.PartOfW[0]
                axes = "WAxes"
            grid_obj = tool.Ifc.get_object(grid)
            if grid_obj:
                grid_col = cls._get_own_collection(grid, grid_obj)
                axes_col = next((c for c in grid_col.children if axes in c.name), None)
                return axes_col or bpy.data.collections.new(axes)

        if element.is_a("IfcAnnotation") and element.ObjectType == "DRAWING":
            return cls._create_own_collection(obj)

        if element.is_a("IfcStructuralMember"):
            return bpy.data.collections.get("Members") or bpy.data.collections.new("Members")

        if element.is_a("IfcStructuralConnection"):
            return bpy.data.collections.get("Connections") or bpy.data.collections.new("Connections")

        if getattr(element, "IsDecomposedBy", None):
            return cls._create_own_collection(obj)

        if getattr(element, "IsNestedBy", None):
            if any(e for e in element.IsNestedBy[0].RelatedObjects if not e.is_a("IfcPort")):
                return cls._create_own_collection(obj)

        if getattr(element, "HasSurfaceFeatures", None):
            return cls._create_own_collection(obj)

    @classmethod
    def _get_collection(cls, element: ifcopenshell.entity_instance, obj: bpy.types.Object) -> bpy.types.Collection:
        """get or create collection for the element based on it's type"""
        if element.is_a("IfcTypeObject"):
            return cls._create_project_child_collection("Types")

        if element.is_a("IfcOpeningElement"):
            return cls._create_project_child_collection("IfcOpeningElements")

        if element.is_a("IfcGridAxis"):
            if element.PartOfU:
                grid = element.PartOfU[0]
                axes = "UAxes"
            elif element.PartOfV:
                grid = element.PartOfV[0]
                axes = "VAxes"
            elif element.PartOfW:
                grid = element.PartOfW[0]
                axes = "WAxes"
            grid_obj = tool.Ifc.get_object(grid)
            if grid_obj:
                return grid_obj.BIMObjectProperties.collection

        if element.is_a("IfcAnnotation"):
            if element.ObjectType == "DRAWING":
                return cls._create_project_child_collection("Views")
            for rel in element.HasAssignments or []:
                if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.ObjectType == "DRAWING":
                    for related_object in rel.RelatedObjects:
                        if related_object.is_a("IfcAnnotation") and related_object.ObjectType == "DRAWING":
                            drawing_obj = tool.Ifc.get_object(related_object)
                            if drawing_obj:
                                return drawing_obj.BIMObjectProperties.collection

        if element.is_a("IfcStructuralItem"):
            return cls._create_project_child_collection("StructuralItems")

        aggregate = ifcopenshell.util.element.get_aggregate(element)
        if aggregate:
            aggregate_obj = tool.Ifc.get_object(aggregate)
            if aggregate_obj:
                collection = aggregate_obj.BIMObjectProperties.collection
                if collection:
                    return collection

        nest = ifcopenshell.util.element.get_nest(element)
        if nest:
            nest_obj = tool.Ifc.get_object(nest)
            if nest_obj:
                collection = nest_obj.BIMObjectProperties.collection
                if collection:
                    return collection

        container = ifcopenshell.util.element.get_container(element)
        if container:
            container_obj = tool.Ifc.get_object(container)
            collection = container_obj.BIMObjectProperties.collection
            if collection:
                return collection

        if element.is_a("IfcSurfaceFeature") and element.file.schema == "IFC4X3":
            adherend = element.AdheresToElement[0].RelatingElement
            adherend_obj = tool.Ifc.get_object(adherend)
            collection = adherend_obj.BIMObjectProperties.collection
            if collection:
                return collection

        if element.is_a("IfcProject"):
            return bpy.context.scene.collection

        project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
        if project_obj:
            return project_obj.BIMObjectProperties.collection

    @classmethod
    def _create_project_child_collection(cls, name: str) -> bpy.types.Collection:
        """get or create new collection inside project"""
        collection = bpy.data.collections.get(name)
        if not collection:
            collection = bpy.data.collections.new(name)
            project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
            project_obj.BIMObjectProperties.collection.children.link(collection)
            collection.hide_viewport = True
        return collection

    @classmethod
    def _create_own_collection(cls, obj: bpy.types.Object) -> bpy.types.Collection:
        """get or create own collection for the element"""
        if obj.BIMObjectProperties.collection:
            return obj.BIMObjectProperties.collection
        collection = bpy.data.collections.new(obj.name)
        obj.BIMObjectProperties.collection = collection
        collection.BIMCollectionProperties.obj = obj
        return collection
