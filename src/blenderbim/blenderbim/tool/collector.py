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
import blenderbim.core.tool
import blenderbim.tool as tool
import ifcopenshell.util.element


class Collector(blenderbim.core.tool.Collector):
    @classmethod
    def assign(cls, obj: bpy.types.Object) -> None:
        """Links an object to an appropriate Blender collection."""
        element = tool.Ifc.get_entity(obj)

        if element.is_a("IfcGridAxis"):
            element = (element.PartOfU or element.PartOfV or element.PartOfW)[0]

        if element.is_a("IfcProject"):
            if collection := cls._create_own_collection(obj):
                collection.objects.link(obj)
                bpy.context.scene.collection.children.link(collection)
        elif element.is_a("IfcTypeProduct"):
            collection = cls._create_project_child_collection("IfcTypeProduct")
            collection.objects.link(obj)
        elif element.is_a("IfcOpeningElement"):
            collection = cls._create_project_child_collection("IfcOpeningElement")
            collection.objects.link(obj)
        elif element.is_a("IfcStructuralItem"):
            collection = cls._create_project_child_collection("IfcStructuralItem")
            collection.objects.link(obj)
        elif tool.Ifc.get_schema() == "IFC2X3" and element.is_a("IfcSpatialStructureElement"):
            if collection := cls._create_own_collection(obj):
                collection.objects.link(obj)
                project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
                project_obj.BIMObjectProperties.collection.children.link(collection)
        elif tool.Ifc.get_schema() != "IFC2X3" and element.is_a("IfcSpatialElement"):
            if collection := cls._create_own_collection(obj):
                collection.objects.link(obj)
                project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
                project_obj.BIMObjectProperties.collection.children.link(collection)
        elif container := ifcopenshell.util.element.get_container(element):
            container_obj = tool.Ifc.get_object(container)
            if not (collection := container_obj.BIMObjectProperties.collection):
                cls.assign(container_obj)
                collection = container_obj.BIMObjectProperties.collection
            collection.objects.link(obj)
        elif element.is_a("IfcAnnotation"):
            if element.ObjectType == "DRAWING":
                if collection := cls._create_own_collection(obj):
                    collection.objects.link(obj)
                    project_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
                    project_obj.BIMObjectProperties.collection.children.link(collection)
            else:
                for rel in element.HasAssignments or []:
                    if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.ObjectType == "DRAWING":
                        for related_object in rel.RelatedObjects:
                            if related_object.is_a("IfcAnnotation") and related_object.ObjectType == "DRAWING":
                                drawing_obj = tool.Ifc.get_object(related_object)
                                if drawing_obj:
                                    drawing_obj.BIMObjectProperties.collection.objects.link(obj)
        else:
            collection = cls._create_project_child_collection("Unsorted")
            collection.objects.link(obj)

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
            return
        collection = bpy.data.collections.new(obj.name)
        obj.BIMObjectProperties.collection = collection
        collection.BIMCollectionProperties.obj = obj
        return collection
