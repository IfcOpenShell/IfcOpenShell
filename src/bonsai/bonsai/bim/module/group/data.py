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
import ifcopenshell
import ifcopenshell.util.cost
import ifcopenshell.util.element
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
        return len(tool.Ifc.get().by_type("IfcGroup", include_subtypes=False))


class ObjectGroupsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"total_groups": cls.total_groups(), "groups": cls.groups()}
        cls.is_loaded = True

    @classmethod
    def total_groups(cls):
        return len(tool.Ifc.get().by_type("IfcGroup", include_subtypes=False))

    @classmethod
    def groups(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if not element:
            return []
        results = []
        for rel in getattr(element, "HasAssignments", []) or []:
            if rel.is_a("IfcRelAssignsToGroup"):
                results.append({"id": rel.RelatingGroup.id(), "name": rel.RelatingGroup.Name or "Unnamed"})
        return results
