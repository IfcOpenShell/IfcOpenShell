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

import bpy
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
        cls.data = {"total_groups": cls.total_groups(), "group_items": cls.group_items()}
        cls.is_loaded = True

    @classmethod
    def total_groups(cls):
        return len(tool.Group.get_user_groups(include_internal=tool.Group.get_group_props().should_show_internal))

    @classmethod
    def group_items(cls) -> list[tuple[str, str, str, int]]:
        include_internal = tool.Group.get_group_props().should_show_internal
        groups = natsorted(tool.Group.get_user_groups(include_internal=include_internal), key=lambda g: g.Name or "")
        return [(str(g.id()), g.Name or "Unnamed", g.Description or "", g.id()) for g in groups]


class ObjectGroupsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        groups, total_hidden = cls.groups()
        cls.data = {"groups": groups, "total_hidden": total_hidden}
        cls.is_loaded = True

    @classmethod
    def groups(cls) -> tuple[list[dict], int]:
        """Get the groups to list for the active object, and how many Bonsai-managed ones are hidden."""
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if not element:
            return [], 0
        show_internal = tool.Group.get_group_props().should_show_internal
        results = []
        total_hidden = 0
        for rel in getattr(element, "HasAssignments", []) or []:
            if not rel.is_a("IfcRelAssignsToGroup"):
                continue
            if not show_internal and tool.Group.is_internal(rel.RelatingGroup):
                total_hidden += 1
                continue
            results.append({"id": rel.RelatingGroup.id(), "name": rel.RelatingGroup.Name or "Unnamed"})
        return results, total_hidden
