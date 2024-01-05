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

# ############################################################################ #


import bpy


def select_group_object_by_id(context, ifc, group, group_id: int):
    bpy.ops.object.select_all(action='DESELECT')
    entity = ifc.get_entity_by_id(group_id)
    collection = ifc.get_object(entity).BIMObjectProperties.collection
    obj = group.get_object_from_collection(collection)
    obj.select_set(True)
    context.view_layer.objects.active = obj


def add_group(parent_id: int, ifc, group, loader):
    new_group_entity = group.create_group(ifc.get())
    parent_group = ifc.get_entity_by_id(parent_id)
    if parent_group is not None:
        group.add_entities_to_group(ifc.get(), parent_group, [new_group_entity])

    # handle collections
    name = loader.get_name(new_group_entity)
    group_object = group.create_group_object(new_group_entity, name, ifc)
    project_entity = ifc.get().by_type("IfcProject")[0]
    project_collection = ifc.get_object(project_entity).BIMObjectProperties.collection
    group.create_collection_by_group(new_group_entity, group_object, name, project_collection, ifc)
    bpy.ops.bim.load_groups()


def remove_group(group_id, ifc, group):
    group_entity = ifc.get_entity_by_id(group_id)
    group.remove_group(ifc, group_entity)
    bpy.ops.bim.load_groups()
