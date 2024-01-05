# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
# Typing
from ifcopenshell import entity_instance


class Group(blenderbim.core.tool.Group):
    @classmethod
    def get_collection_from_entity(cls, entity: ifcopenshell.entity_instance,
                                   groups_data) -> entity_instance | None:
        """Select Object in Collection by entity id"""
        collection_dict = groups_data.data["collections_dict"]
        return collection_dict.get(entity)

    @classmethod
    def get_object_from_collection(cls, collection: bpy.types.Collection):

        prop = collection.BIMCollectionProperties
        if prop is None:
            return
        return prop.obj

    @classmethod
    def create_group(cls, ifc_file) -> entity_instance:
        group = ifcopenshell.api.run("group.add_group", ifc_file)
        return group

    @classmethod
    def create_group_object(csl, group_entity: entity_instance, name: str, ifc):
        group_object = bpy.data.objects.new(name, None)
        ifc.link(group_entity, group_object)
        return group_object

    @classmethod
    def add_entities_to_group(cls, ifc_file, parent_group: entity_instance, entities: list[entity_instance]) -> None:
        ifcopenshell.api.run("group.assign_group", ifc_file, products=entities, group=parent_group)

    @classmethod
    def create_collection_by_group(cls, group: entity_instance, obj, name: str, collection_project, ifc) -> None:

        if not group.HasAssignments:
            collection = bpy.data.collections.new(name)
            collection_project.children.link(collection)
            collection.objects.link(obj)
            collection.BIMCollectionProperties.obj = obj
            obj.BIMObjectProperties.collection = collection

        for assignemnt in group.HasAssignments:
            collection = bpy.data.collections.new(name)
            collection.objects.link(obj)
            collection.BIMCollectionProperties.obj = obj
            obj.BIMObjectProperties.collection = collection
            # technical it is possible that a group is assigned to multiple groups
            # this edgecase is (so far) not perfectly handled

            if not assignemnt.is_a("IfcRelAssignsToGroup"):
                continue
            parent_group_entity = assignemnt.RelatingGroup
            parent_collection = ifc.get_object(parent_group_entity).BIMObjectProperties.collection
            if parent_collection is None:
                continue
            parent_collection.children.link(collection)
