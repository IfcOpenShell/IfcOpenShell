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
from collections.abc import Iterable
from typing import TYPE_CHECKING, Literal, Union, assert_never

import bpy
import ifcopenshell
import ifcopenshell.util.system
from natsort import natsorted

import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    from bonsai.bim.module.group.prop import BIMGroupProperties
    from bonsai.bim.module.group.prop import Group as GroupProp
    from bonsai.bim.module.system.prop import BIMSystemProperties, System


class Group(bonsai.core.tool.System):
    @classmethod
    def get_group_props(cls) -> BIMGroupProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMGroupProperties  # pyright: ignore[reportAttributeAccessIssue]

    GroupType = Literal["IfcGroup", "IfcSystem"]

    @classmethod
    def get_groups_data(
        cls, group_type: GroupType
    ) -> Union[
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

        props, blender_groups = cls.get_groups_data(group_type)
        # While the Groups list is filtered, load nested groups too so the filter can find them.
        load_all = False
        # The Groups list shows every kind of group the kind filter allows; None keeps the Systems list as it was.
        visible: Union[set[ifcopenshell.entity_instance], None] = None
        if group_type == "IfcGroup":
            load_all = bool(props.group_filter.strip())
            base_groups = cls.get_all_groups(props.group_kinds, include_internal=props.should_show_internal)
            visible = set(base_groups)
        elif group_type == "IfcSystem":
            base_groups = [g for g in tool.System.get_systems() if not g.is_a("IfcStructuralAnalysisModel")]
        else:
            assert_never(group_type)

        def is_top_level(group: ifcopenshell.entity_instance) -> bool:
            if visible is None:
                return not group.HasAssignments
            # A group nested in a group that isn't shown is listed at the top level instead.
            return not any(
                rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup in visible for rel in group.HasAssignments or []
            )

        expanded_groups_json = props.expanded_groups_json
        expanded_groups: list[int] = json.loads(expanded_groups_json)
        blender_groups.clear()

        groups = [g for g in base_groups if is_top_level(g)]
        sorted_groups = natsorted(groups, key=lambda group: group.Name or "Unnamed")

        def load_group(group: ifcopenshell.entity_instance, tree_depth: int = 0) -> None:
            new = blender_groups.add()
            new.ifc_definition_id = group.id()
            new["name"] = group.Name or "Unnamed"
            new.tree_depth = tree_depth
            new.has_children = False
            new.is_expanded = load_all or group.id() in expanded_groups
            if isinstance(new, System):
                new.ifc_class = group.is_a()
            else:
                new.icon = cls.get_icon(group)

            related_groups: list[ifcopenshell.entity_instance]
            related_groups = [
                related_object
                for rel in group.IsGroupedBy or []
                for related_object in rel.RelatedObjects
                if (related_object in visible if visible is not None else related_object.is_a(group_type))
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

    @classmethod
    def draw_visibility_buttons(cls, layout: bpy.types.UILayout, group_id: int) -> None:
        for mode, icon in (("ISOLATE", "FULLSCREEN_EXIT"), ("SHOW", "HIDE_OFF"), ("HIDE", "HIDE_ON")):
            op = layout.operator("bim.set_group_visibility", icon=icon, text="")
            op.mode = mode
            op.group = group_id

    @classmethod
    def get_description_type(cls, group: ifcopenshell.entity_instance) -> Union[str, None]:
        """Get the "type" Bonsai stores in a group's JSON Description (e.g. "BBIM_Search").

        Returns None for groups whose Description is not such JSON, e.g. user groups.
        """
        try:
            data = json.loads(group.Description or "")
        except ValueError:
            return None
        return data.get("type") if isinstance(data, dict) else None

    INTERNAL_OBJECT_TYPES = ("DRAWING", "DRAWINGS", "SEARCH")
    INTERNAL_DESCRIPTION_TYPES = ("BBIM_Search", "BBIM_AnimationColorScheme")

    @classmethod
    def is_internal(cls, group: ifcopenshell.entity_instance) -> bool:
        """Whether a plain IfcGroup stores Bonsai's own data rather than being a user's group.

        That is drawings, saved searches and colour schemes, and linked aggregates.
        """
        if group.is_a() != "IfcGroup":
            return False
        if group.ObjectType in cls.INTERNAL_OBJECT_TYPES:
            return True
        if "BBIM_Linked_Aggregate" in (group.Name or ""):
            return True
        return cls.get_description_type(group) in cls.INTERNAL_DESCRIPTION_TYPES

    GroupKind = Literal["GROUP", "SYSTEM", "ZONE", "STRUCTURAL", "OTHER"]

    @classmethod
    def get_kind(cls, group: ifcopenshell.entity_instance) -> GroupKind:
        """Sort any IfcGroup into the kinds the Groups list can filter by."""
        if any(
            group.is_a(c) for c in ("IfcStructuralAnalysisModel", "IfcStructuralLoadGroup", "IfcStructuralResultGroup")
        ):
            return "STRUCTURAL"
        if group.is_a("IfcZone"):
            return "ZONE"
        if group.is_a("IfcSystem"):
            return "SYSTEM"
        if group.is_a() == "IfcGroup":
            return "GROUP"
        return "OTHER"  # E.g. IfcAsset, IfcInventory.

    @classmethod
    def get_icon(cls, group: ifcopenshell.entity_instance) -> str:
        kind = cls.get_kind(group)
        if kind == "SYSTEM":
            return tool.System.SYSTEM_ICONS.get(group.is_a(), tool.System.SYSTEM_ICONS["IfcSystem"])
        return {"GROUP": "OUTLINER", "ZONE": "CUBE", "STRUCTURAL": "EDITMODE_HLT", "OTHER": "PACKAGE"}[kind]

    GroupAction = Literal["ASSIGN", "ADD_CHILD", "REMOVE"]

    @classmethod
    def get_group_actions(cls, group: ifcopenshell.entity_instance) -> set[GroupAction]:
        """Which Groups list actions apply to a group, besides selecting, showing and editing attributes."""
        if group.is_a("IfcStructuralAnalysisModel") or group.is_a("IfcZone"):
            return {"ASSIGN", "REMOVE"}
        if group.is_a("IfcStructuralLoadGroup"):
            return {"REMOVE"}  # Holds structural activities, not products; its children are made in Structural.
        if group.is_a("IfcStructuralResultGroup"):
            return set()
        return {"ASSIGN", "ADD_CHILD", "REMOVE"}

    @classmethod
    def get_assignable(
        cls, group: ifcopenshell.entity_instance, elements: Iterable[ifcopenshell.entity_instance]
    ) -> list[ifcopenshell.entity_instance]:
        """Get the elements that can be assigned to a group: systems and zones only take some classes."""
        if group.is_a("IfcSystem") and not group.is_a("IfcStructuralAnalysisModel"):
            return [e for e in elements if ifcopenshell.util.system.is_assignable(e, group)]
        return list(elements)

    @classmethod
    def get_all_groups(cls, kinds: Iterable[str], include_internal: bool = False) -> list[ifcopenshell.entity_instance]:
        """Get every IfcGroup, of any subtype, whose kind is in ``kinds``."""
        kinds = set(kinds)
        return [
            g
            for g in tool.Ifc.get().by_type("IfcGroup")
            if cls.get_kind(g) in kinds and (include_internal or not cls.is_internal(g))
        ]

    @classmethod
    def get_user_groups(cls, include_internal: bool = False) -> list[ifcopenshell.entity_instance]:
        """Get plain IfcGroups (no systems or zones), leaving out Bonsai's internal ones unless asked."""
        groups = tool.Ifc.get().by_type("IfcGroup", include_subtypes=False)
        if include_internal:
            return groups
        return [g for g in groups if not cls.is_internal(g)]
