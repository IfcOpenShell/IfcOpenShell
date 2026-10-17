# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

from typing import Optional

import bpy
import ifcopenshell
import ifcopenshell.util.system
from natsort import natsorted

import bonsai.tool as tool


def refresh():
    GroupsData.is_loaded = False
    ObjectGroupsData.is_loaded = False


class GroupsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"total_groups": cls.total_groups()}
        cls.is_loaded = True

    @classmethod
    def total_groups(cls):
        props = tool.Group.get_group_props()
        return len(tool.Group.get_all_groups(props.group_kinds, include_internal=props.should_show_internal))


class ObjectGroupsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj) if obj else None
        groups, total_hidden = cls.groups(element)
        cls.data = {"groups": groups, "total_hidden": total_hidden, "group_items": cls.group_items(element)}
        cls.is_loaded = True

    @classmethod
    def get_icon(cls, group: ifcopenshell.entity_instance) -> str:
        return tool.Group.get_icon(group)

    @classmethod
    def get_sort_key(cls, group: ifcopenshell.entity_instance) -> tuple[int, str]:
        # Groups first, then systems, zones and structural analysis models.
        if group.is_a("IfcStructuralAnalysisModel"):
            rank = 3
        elif group.is_a("IfcZone"):
            rank = 2
        elif group.is_a("IfcSystem"):
            rank = 1
        else:
            rank = 0
        return rank, group.Name or "Unnamed"

    @classmethod
    def groups(cls, element: Optional[ifcopenshell.entity_instance]) -> tuple[list[dict], int]:
        """Get the groups, systems and zones to list for the element, and how many Bonsai-managed groups are hidden."""
        if not element:
            return [], 0
        show_internal = tool.Group.get_group_props().should_show_internal
        groups = []
        total_hidden = 0
        for rel in getattr(element, "HasAssignments", []) or []:
            if not rel.is_a("IfcRelAssignsToGroup"):
                continue
            if not show_internal and tool.Group.is_internal(rel.RelatingGroup):
                total_hidden += 1
                continue
            groups.append(rel.RelatingGroup)
        results = [
            {"id": g.id(), "name": g.Name or "Unnamed", "icon": cls.get_icon(g)}
            for g in natsorted(groups, key=cls.get_sort_key)
        ]
        return results, total_hidden

    @classmethod
    def group_items(cls, element: Optional[ifcopenshell.entity_instance]) -> list[tuple[str, str, str, str, int]]:
        """Get the groups, and the systems and zones the element can join, to pick from."""
        include_internal = tool.Group.get_group_props().should_show_internal
        groups = list(tool.Group.get_user_groups(include_internal=include_internal))
        if element:
            groups += [
                s for s in tool.Ifc.get().by_type("IfcSystem") if ifcopenshell.util.system.is_assignable(element, s)
            ]
        return [
            (str(g.id()), g.Name or "Unnamed", g.is_a(), cls.get_icon(g), g.id())
            for g in natsorted(groups, key=cls.get_sort_key)
        ]
