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
import blenderbim.tool as tool


class Collector(blenderbim.core.tool.Collector):
    @classmethod
    def sync(cls, obj):
        # This is the reverse of assign. It reads the Blender collection and figures out its IFC hierarchy
        element = tool.Ifc.get_entity(obj)

        if element.is_a("IfcProject") or element.is_a("IfcGridAxis") or element.is_a("IfcOpeningElement"):
            return

        if not obj.users_collection:
            return

        object_collection = None
        collection_collection = None

        object_collection = cls._get_own_collection(element, obj)
        if object_collection:
            collection_collection = cls._get_collection(element, obj)
        else:
            object_collection = cls._get_collection(element, obj)

        parent_collection = None

        if obj.users_collection != (object_collection,) and obj.users_collection[0].name != obj.name:
            parent_collection = obj.users_collection[0]
        elif collection_collection and collection_collection.children.find(object_collection.name) == -1:
            for collection in bpy.data.collections:
                if collection.children.find(obj.users_collection[0].name) != -1:
                    parent_collection = collection
                    break

        if parent_collection:
            parent_obj = bpy.data.objects.get(parent_collection.name)
            parent = tool.Ifc.get_entity(parent_obj)
            if parent:
                # This is lazy, but works. One of these will succeed, the other will fail silently.
                blenderbim.core.spatial.assign_container(
                    tool.Ifc, tool.Collector, tool.Spatial, structure_obj=parent_obj, element_obj=obj
                )
                blenderbim.core.aggregate.assign_object(
                    tool.Ifc, tool.Aggregate, tool.Collector, relating_obj=parent_obj, related_obj=obj
                )

    @classmethod
    def assign(cls, obj):
        element = tool.Ifc.get_entity(obj)

        object_collection = None
        collection_collection = None

        object_collection = cls._get_own_collection(element, obj)
        if object_collection:
            collection_collection = cls._get_collection(element, obj)
        else:
            object_collection = cls._get_collection(element, obj)

        if obj.users_collection != (object_collection,):
            for collection in obj.users_collection:
                collection.objects.unlink(obj)
            if object_collection is not None:
                object_collection.objects.link(obj)

        if collection_collection and collection_collection.children.find(object_collection.name) == -1:
            if bpy.context.scene.collection.children.find(object_collection.name) != -1:
                bpy.context.scene.collection.children.unlink(object_collection)
            for collection in bpy.data.collections:
                if collection.children.find(object_collection.name) != -1:
                    collection.children.unlink(object_collection)
            collection_collection.children.link(object_collection)

    @classmethod
    def _get_own_collection(cls, element, obj):
        if element.is_a("IfcProject"):
            return bpy.data.collections.get(obj.name, bpy.data.collections.new(obj.name))

        if tool.Ifc.get_schema() == "IFC2X3":
            if element.is_a("IfcSpatialStructureElement"):
                return bpy.data.collections.get(obj.name, bpy.data.collections.new(obj.name))
        else:
            if element.is_a("IfcSpatialStructureElement") or element.is_a("IfcExternalSpatialStructureElement"):
                return bpy.data.collections.get(obj.name, bpy.data.collections.new(obj.name))

        if element.is_a("IfcGrid"):
            return bpy.data.collections.get(obj.name, bpy.data.collections.new(obj.name))

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
                grid_col = bpy.data.collections.get(grid_obj.name)
                axes_col = [c for c in grid_col.children if axes in c.name]
                if axes_col:
                    return axes_col[0]
                return bpy.data.collections.new(axes)

        if element.is_a("IfcAnnotation"):
            for rel in element.HasAssignments or []:
                if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.ObjectType == "DRAWING":
                    name = "IfcGroup/" + rel.RelatingGroup.Name
                    return bpy.data.collections.get(name, bpy.data.collections.new(name))

        if element.is_a("IfcStructuralMember"):
            return bpy.data.collections.get("Members", bpy.data.collections.new("Members"))

        if element.is_a("IfcStructuralConnection"):
            return bpy.data.collections.get("Connections", bpy.data.collections.new("Connections"))

        if getattr(element, "IsDecomposedBy", None):
            return bpy.data.collections.get(obj.name, bpy.data.collections.new(obj.name))

    @classmethod
    def _get_collection(cls, element, obj):
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
                return bpy.data.collections.get(grid_obj.name)

        if element.is_a("IfcAnnotation"):
            for rel in element.HasAssignments or []:
                if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.ObjectType == "DRAWING":
                    return cls._create_project_child_collection("Views")

        if element.is_a("IfcStructuralItem"):
            return cls._create_project_child_collection("StructuralItems")

        aggregate = ifcopenshell.util.element.get_aggregate(element)
        if aggregate:
            aggregate_obj = tool.Ifc.get_object(aggregate)
            if aggregate_obj:
                collection = bpy.data.collections.get(aggregate_obj.name)
                if collection:
                    return collection

        container = ifcopenshell.util.element.get_container(element)
        if container:
            container_obj = tool.Ifc.get_object(container)
            collection = bpy.data.collections.get(container_obj.name)
            if collection:
                return collection

        if element.is_a("IfcProject"):
            return bpy.context.scene.collection

        project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
        if project_obj:
            collection = bpy.data.collections.get(project_obj.name)
            if collection:
                return collection

    @classmethod
    def _create_project_child_collection(cls, name):
        collection = bpy.data.collections.get(name)
        if not collection:
            collection = bpy.data.collections.new(name)
            project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
            project_obj.users_collection[0].children.link(collection)
        return collection
