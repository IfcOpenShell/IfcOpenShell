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
from typing import TYPE_CHECKING, Literal, assert_never, Union
from natsort import natsorted

if TYPE_CHECKING:
    from bonsai.bim.module.group.prop import BIMGroupProperties, Group as GroupProp
    from bonsai.bim.module.system.prop import BIMSystemProperties, System


class Group(bonsai.core.tool.System):
    @classmethod
    def get_group_props(cls) -> BIMGroupProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMGroupProperties  # pyright: ignore[reportAttributeAccessIssue]

    GroupType = Literal["IfcGroup", "IfcSystem"]

    @classmethod
    def get_groups_data(cls, group_type: GroupType) -> Union[
        tuple[BIMGroupProperties, bpy.types.bpy_prop_collection_idprop[GroupProp]],
        tuple[BIMSystemProperties, bpy.types.bpy_prop_collection_idprop[System]],
    ]:
        if group_type == "IfcGroup":
            props = tool.Group.get_group_props()
            blender_groups = props.groups
            return props, blender_groups
        elif group_type == "IfcSystem":
            props = tool.System.get_system_props()
            blender_groups = props.systems
            return props, blender_groups
        else:
            assert_never(group_type)

    @classmethod
    def import_groups(cls, group_type: GroupType) -> None:
        from bonsai.bim.module.system.prop import System

        ifc_file = tool.Ifc.get()
        props, blender_groups = cls.get_groups_data(group_type)
        if group_type == "IfcGroup":
            base_groups = ifc_file.by_type("IfcGroup", include_subtypes=False)
        elif group_type == "IfcSystem":
            base_groups = [g for g in tool.System.get_systems() if not g.is_a("IfcStructuralAnalysisModel")]
        else:
            assert_never(group_type)

        expanded_groups_json = props.expanded_groups_json
        expanded_groups: list[int] = json.loads(expanded_groups_json)
        blender_groups.clear()

        groups = [g for g in base_groups if not g.HasAssignments]
        sorted_groups = natsorted(groups, key=lambda group: group.Name or "Unnamed")

        def load_group(group: ifcopenshell.entity_instance, tree_depth: int = 0) -> None:
            new = blender_groups.add()
            new.ifc_definition_id = group.id()
            new["name"] = group.Name or "Unnamed"
            new.tree_depth = tree_depth
            new.has_children = False
            new.is_expanded = group.id() in expanded_groups
            if isinstance(new, System):
                new.ifc_class = group.is_a()

            related_groups: list[ifcopenshell.entity_instance]
            related_groups = [
                related_object
                for rel in group.IsGroupedBy or []
                for related_object in rel.RelatedObjects
                if related_object.is_a(group_type)
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

    ToggleOption = Literal["EXPAND", "COLLAPSE"]

    @classmethod
    def toggle_group(cls, group: ifcopenshell.entity_instance, group_type: GroupType, option: ToggleOption) -> None:
        props, _ = cls.get_groups_data(group_type)
        expanded_groups: set[int]
        expanded_groups = set(json.loads(props.expanded_groups_json))
        ifc_definition_id = group.id()
        if option == "EXPAND":
            expanded_groups.add(ifc_definition_id)
        elif ifc_definition_id in expanded_groups:
            expanded_groups.remove(ifc_definition_id)
        props.expanded_groups_json = json.dumps(list(expanded_groups))
        cls.import_groups(group_type)

    @classmethod
    def update_uilist_index(cls, group_type: GroupType) -> None:
        props, blender_groups = cls.get_groups_data(group_type)
        props.active_group_index = tool.Blender.get_valid_uilist_index(props.active_group_index, blender_groups)
