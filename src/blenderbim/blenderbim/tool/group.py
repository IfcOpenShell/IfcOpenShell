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
    def load_group(cls, group_entity: entity_instance, props, expanded_groups, tree_depth=0):
        new_group = props.groups.add()
        new_group.ifc_definition_id = group_entity.id()
        new_group.name = group_entity.Name or "Unnamed"
        new_group.selection_query = ""
        new_group.tree_depth = tree_depth
        new_group.has_children = False
        new_group.is_expanded = group_entity.id() in expanded_groups

        for sub_group in cls.get_sub_groups(group_entity):
            new_group.has_children = True
            if not new_group.is_expanded:
                return
            cls.load_group(sub_group, props, expanded_groups, tree_depth=tree_depth + 1)

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

    @classmethod
    def remove_group(cls, ifc, group_entity) -> None:
        """
        removes Group from Ifc and UI
        Doesn't Delete Subgroups -> Subgroups move to first Layer in View (IfcProject)
        """
        group_object = ifc.get_object(group_entity)
        sub_groups = cls.get_sub_groups(group_entity)
        ifcopenshell.api.run("group.remove_group", ifc.get(), **{"group": group_entity})
        group_collection = group_object.BIMObjectProperties.collection
        bpy.data.objects.remove(group_object, do_unlink=True)
        bpy.data.collections.remove(group_collection, do_unlink=True)

        project_entity = ifc.get().by_type("IfcProject")[0]
        project_collection = ifc.get_object(project_entity).BIMObjectProperties.collection

        # check if subgroup is also assigned elsewhere. if not -> Move to Project
        for sub_group in sub_groups:
            if [ass for ass in sub_group.HasAssignments if ass.is_a("IfcRelAssignsToGroup")]:
                continue
            collection = ifc.get_object(sub_group).BIMObjectProperties.collection
            project_collection.children.link(collection)

    @classmethod
    def get_sub_groups(self, group_entity) -> list[entity_instance]:
        """
        return all IfcGroup entities hat have IfcRelAssignsToGroup assignment to group_entity
        """
        sub_groups = list()
        [sub_groups.extend([o for o in rel.RelatedObjects if o.is_a("IfcGroup")]) for rel in group_entity.IsGroupedBy]
        return sub_groups
