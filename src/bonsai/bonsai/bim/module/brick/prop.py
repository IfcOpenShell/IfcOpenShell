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
from bonsai.bim.module.brick.data import BrickschemaData, BrickschemaReferencesData
from bonsai.bim.prop import StrProperty, Attribute
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)
import bonsai.core.brick as core
import bonsai.tool.brick as tool
from bonsai.tool.brick import BrickStore


def update_active_brick_index(self, context):
    BrickschemaData.is_loaded = False


def get_libraries(self, context):
    if not BrickschemaReferencesData.is_loaded:
        BrickschemaReferencesData.load()
    return BrickschemaReferencesData.data["libraries"]


def get_namespaces(self, context):
    global NAMESPACES_ENUM_ITEMS
    NAMESPACES_ENUM_ITEMS = [(uri, f"{alias}: {uri}", "") for alias, uri in BrickStore.namespaces]
    return NAMESPACES_ENUM_ITEMS


def get_brick_entity_classes(self, context):
    global ENTITY_CLASSES_ENUM_ITEMS
    entity = self.brick_entity_create_type
    ENTITY_CLASSES_ENUM_ITEMS = [(uri, uri.split("#")[-1], "") for uri in BrickStore.entity_classes[entity]]
    return ENTITY_CLASSES_ENUM_ITEMS


def get_brick_roots(self, context):
    global BRICK_ROOTS_ENUM_ITEMS
    BRICK_ROOTS_ENUM_ITEMS = [(root, root, "") for root in BrickStore.root_classes]
    return BRICK_ROOTS_ENUM_ITEMS


def get_brick_relations(self, context):
    global BRICK_RELATIONS_ENUM_ITEMS
    BRICK_RELATIONS_ENUM_ITEMS = [(uri, uri.split("#")[-1], "") for uri in BrickStore.relationships]
    for relation in BrickschemaData.data["active_relations"]:
        if relation["predicate_name"] == "label":
            return BRICK_RELATIONS_ENUM_ITEMS
    BRICK_RELATIONS_ENUM_ITEMS.append(("http://www.w3.org/2000/01/rdf-schema#label", "label", ""))
    return BRICK_RELATIONS_ENUM_ITEMS


def update_view(self, context):
    root = context.scene.BIMBrickProperties.brick_list_root
    core.set_brick_list_root(tool.Brick, brick_root=root, split_screen=False)


def split_screen_update_view(self, context):
    root = context.scene.BIMBrickProperties.split_screen_brick_list_root
    core.set_brick_list_root(tool.Brick, brick_root=root, split_screen=True)


class Brick(PropertyGroup):
    name: StringProperty(name="Name")
    label: StringProperty(name="Label")
    uri: StringProperty(name="URI")
    total_items: IntProperty(name="Total Items")


class BIMBrickProperties(PropertyGroup):
    active_brick_class: StringProperty(name="Active Brick Class")
    brick_breadcrumbs: CollectionProperty(name="Brick Breadcrumbs", type=StrProperty)
    bricks: CollectionProperty(name="Bricks", type=Brick)
    active_brick_index: IntProperty(name="Active Brick Index", update=update_active_brick_index)
    libraries: EnumProperty(name="Libraries", items=get_libraries)
    set_list_root_toggled: BoolProperty(name="Set List Root Toggled", default=False)
    brick_list_root: EnumProperty(name="Brick List Root", items=get_brick_roots, update=update_view)
    # namespace manager
    namespace: EnumProperty(name="Namespace", items=get_namespaces)
    new_brick_namespace_alias: StringProperty(name="New Brick Namespace Alias")
    new_brick_namespace_uri: StringProperty(name="New Brick Namespace URI")
    # create brick entity
    new_brick_label: StringProperty(name="New Brick Label")
    brick_entity_create_type: EnumProperty(name="Brick Entity Types", items=get_brick_roots)
    brick_entity_class: EnumProperty(name="Brick Equipment Class", items=get_brick_entity_classes)
    # create relations
    brick_create_relations_toggled: BoolProperty(name="Brick Create Relations Toggled", default=False)
    brick_edit_relations_toggled: BoolProperty(name="Brick Edit Relations Toggled", default=False)
    new_brick_relation_type: EnumProperty(name="New Brick Relation Type", items=get_brick_relations)
    new_brick_relation_object: StringProperty(name="New Brick Relation Object")
    add_brick_relation_failed: BoolProperty(name="Add Relation Failed", default=False)
    # create relations split screen
    split_screen_toggled: BoolProperty(name="Split Screen Toggled", default=False)
    split_screen_bricks: CollectionProperty(name="Split Screen Bricks", type=Brick)
    split_screen_active_brick_index: IntProperty(
        name="Split Screen Active Brick Index", update=update_active_brick_index
    )
    split_screen_active_brick_class: StringProperty(name="Split Screen Active Brick Class")
    split_screen_brick_breadcrumbs: CollectionProperty(name="Split Screen Brick Breadcrumbs", type=StrProperty)
    split_screen_brick_list_root: EnumProperty(
        name="Split Screen Brick List Root", items=get_brick_roots, update=split_screen_update_view
    )
