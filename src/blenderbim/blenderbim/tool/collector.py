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
            collection = bpy.data.collections.get(obj.name)
            if not collection:
                collection = bpy.data.collections.new(obj.name)
            return collection

        if tool.Ifc.get_schema() == "IFC2X3":
            if element.is_a("IfcSpatialStructureElement"):
                collection = bpy.data.collections.get(obj.name)
                if not collection:
                    collection = bpy.data.collections.new(obj.name)
                return collection
        else:
            if element.is_a("IfcSpatialElement"):
                collection = bpy.data.collections.get(obj.name)
                if not collection:
                    collection = bpy.data.collections.new(obj.name)
                return collection

        if element.IsDecomposedBy:
            collection = bpy.data.collections.get(obj.name)
            if not collection:
                collection = bpy.data.collections.new(obj.name)
            return collection

    @classmethod
    def _get_collection(cls, element, obj):
        aggregate = ifcopenshell.util.element.get_aggregate(element)
        if aggregate:
            aggregate_obj = tool.Ifc.get_object(aggregate)
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
