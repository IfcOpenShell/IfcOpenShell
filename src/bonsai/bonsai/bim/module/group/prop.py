# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

from typing import TYPE_CHECKING, Union

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

import bonsai.tool as tool
from bonsai.bim.module.group.data import ObjectGroupsData
from bonsai.bim.module.group.data import refresh as refresh_group
from bonsai.bim.module.pset.data import refresh as refresh_pset
from bonsai.bim.prop import Attribute


def get_object_group(self, context):
    if not ObjectGroupsData.is_loaded:
        ObjectGroupsData.load()
    return ObjectGroupsData.data["group_items"]


def update_should_show_internal(self: "BIMGroupProperties", context: object) -> None:
    refresh_group()
    if self.is_editing:
        tool.Group.import_groups("IfcGroup")
    # The toggle is shown in both Project Overview and Object Information, which may be different editors.
    tool.Blender.update_all_properties_editors()


def update_group_filter(self: "BIMGroupProperties", context: object) -> None:
    # Reload only when the filter switches on or off: while it's on, every group is loaded, expanded or not.
    is_filter_active = bool(self.group_filter.strip())
    if is_filter_active == self.is_group_filter_active:
        return
    self.is_group_filter_active = is_filter_active
    if self.is_editing:
        tool.Group.import_groups("IfcGroup")


GROUP_KIND_ITEMS = [
    ("GROUP", "Groups", "Show plain IfcGroups", "OUTLINER", 1),
    ("SYSTEM", "Systems", "Show systems, like distribution and building systems", "NETWORK_DRIVE", 2),
    ("ZONE", "Zones", "Show zones", "CUBE", 4),
    ("STRUCTURAL", "Structural", "Show structural analysis models, load groups and result groups", "EDITMODE_HLT", 8),
    ("OTHER", "Other", "Show other kinds of group, like assets and inventories", "PACKAGE", 16),
]


def update_group_kinds(self: "BIMGroupProperties", context: object) -> None:
    refresh_group()
    if self.is_editing:
        tool.Group.import_groups("IfcGroup")


def update_active_group_index(self, context):
    refresh_pset()


def update_name(self: "Group", context: object) -> None:
    group = tool.Ifc.get_entity_by_id(self.ifc_definition_id)
    # Theoretically group can be removed outside Group UI.
    if not group:
        return
    if group.Name == self.name:
        return
    group.Name = self.name


class Group(PropertyGroup):
    name: StringProperty(name="Name", update=update_name)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    is_expanded: BoolProperty(name="Is Expanded", default=False)
    has_children: BoolProperty(name="Has Children", default=False)
    tree_depth: IntProperty(name="Tree Depth")
    icon: StringProperty(name="Icon", default="OUTLINER")

    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int
        is_expanded: bool
        has_children: bool
        tree_depth: int
        icon: str


class BIMGroupProperties(PropertyGroup):
    group_attributes: CollectionProperty(name="Group Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing", default=False)
    groups: CollectionProperty(name="Groups", type=Group)
    active_group_index: IntProperty(name="Active Group Index", update=update_active_group_index)
    active_group_id: IntProperty(name="Active Group Id")
    expanded_groups_json: StringProperty(name="JSON String", default="[]")
    """JSON serialized list[group_id]."""
    is_editing_object_groups: BoolProperty(name="Is Editing Object Groups", default=False)
    object_group: EnumProperty(name="Group", items=get_object_group)
    should_show_internal: BoolProperty(
        name="Show Bonsai-Managed Groups",
        description="Also list groups Bonsai uses to store its own data: drawings, saved searches, "
        "colour schemes and linked aggregates",
        default=False,
        update=update_should_show_internal,
    )
    group_kinds: EnumProperty(
        name="Group Kinds",
        description="Which kinds of group the Groups list shows",
        items=GROUP_KIND_ITEMS,
        options={"ENUM_FLAG"},
        default={"GROUP", "SYSTEM", "ZONE", "STRUCTURAL", "OTHER"},
        update=update_group_kinds,
    )
    group_filter: StringProperty(name="Group Filter", update=update_group_filter, options={"TEXTEDIT_UPDATE"})
    is_group_filter_active: BoolProperty(name="Is Group Filter Active", default=False)

    if TYPE_CHECKING:
        group_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        is_editing: bool
        groups: bpy.types.bpy_prop_collection_idprop[Group]
        active_group_index: int
        active_group_id: int
        expanded_groups_json: str
        is_editing_object_groups: bool
        object_group: str
        should_show_internal: bool
        group_kinds: set[str]
        group_filter: str
        is_group_filter_active: bool

    @property
    def active_group(self) -> Union[Group, None]:
        return tool.Blender.get_active_uilist_element(self.groups, self.active_group_index)
