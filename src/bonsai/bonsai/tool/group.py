# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations
import json
import bpy
import ifcopenshell
import bonsai.bim.helper
import bonsai.core.tool
import bonsai.tool as tool
from typing import TYPE_CHECKING
from natsort import natsorted

if TYPE_CHECKING:
    from bonsai.bim.module.group.prop import BIMGroupProperties


class Group(bonsai.core.tool.System):
    @classmethod
    def get_group_props(cls) -> BIMGroupProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMGroupProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def import_groups(cls) -> None:
        props = tool.Group.get_group_props()
        expanded_groups: list[int] = json.loads(props.expanded_groups_json)
        props.groups.clear()

        groups = [
            group for group in tool.Ifc.get().by_type("IfcGroup", include_subtypes=False) if not group.HasAssignments
        ]
        sorted_groups = natsorted(groups, key=lambda group: group.Name or "Unnamed")

        def load_group(group: ifcopenshell.entity_instance, tree_depth: int = 0) -> None:
            new = props.groups.add()
            new.ifc_definition_id = group.id()
            new["name"] = group.Name or "Unnamed"
            new.tree_depth = tree_depth
            new.has_children = False
            new.is_expanded = group.id() in expanded_groups

            related_groups: list[ifcopenshell.entity_instance]
            related_groups = [
                related_object
                for rel in group.IsGroupedBy or []
                for related_object in rel.RelatedObjects
                if related_object.is_a("IfcGroup")
            ]
            sorted_related_groups = natsorted(related_groups, key=lambda group: group.Name or "Unnamed")

            if sorted_related_groups:
                new.has_children = True
                if new.is_expanded:
                    for related_group in sorted_related_groups:
                        load_group(related_group, tree_depth=tree_depth + 1)

        for group in sorted_groups:
            load_group(group)

    @classmethod
    def enable_group_editing_ui(cls) -> None:
        props = cls.get_group_props()
        props.is_editing = True

    @classmethod
    def disable_group_editing_ui(cls) -> None:
        props = cls.get_group_props()
        props.is_editing = False

    @classmethod
    def disable_editing_group(cls) -> None:
        props = cls.get_group_props()
        props.active_group_id = 0

    @classmethod
    def set_active_group_to_edit(cls, group: ifcopenshell.entity_instance) -> None:
        props = cls.get_group_props()
        props.active_group_id = group.id()
