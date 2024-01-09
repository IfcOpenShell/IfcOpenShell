# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import ifcopenshell.util.cost
import ifcopenshell.util.element
import blenderbim.tool as tool
from typing import Any

def refresh():
    GroupsData.is_loaded = False
    ObjectGroupsData.is_loaded = False


class GroupsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"total_groups": cls.total_groups(),
                    "collections_dict": cls.collections_dict()
                    }
        cls.is_loaded = True

    @classmethod
    def total_groups(cls):
        return len(tool.Ifc.get().by_type("IfcGroup", include_subtypes=False))

    @classmethod
    def collections_dict(cls) -> dict[ifcopenshell.entity_instance,bpy.types.Collection]:
        group_dict = dict()
        for col in bpy.data.collections:
            props = col.get("BIMCollectionProperties")
            if not props:
                continue

            obj = props.get("obj")
            if not obj:
                continue

            entity = tool.Ifc.get_entity(obj)
            if not entity:
                continue

            if entity.is_a("IfcGroup"):
                group_dict[entity] = col
        return group_dict

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
