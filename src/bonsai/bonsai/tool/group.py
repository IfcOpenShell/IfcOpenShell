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
from typing import TYPE_CHECKING, Literal, Union, assert_never

import bpy
import ifcopenshell
from natsort import natsorted

import bonsai.bim.helper
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
        
        # Store connection groups data for Systems
        connection_groups_data: dict[int, list[list[int]]] = {}

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
                new.is_element = False

            related_groups: list[ifcopenshell.entity_instance]
            related_groups = [
                related_object
                for rel in group.IsGroupedBy or []
                for related_object in rel.RelatedObjects
                if related_object.is_a(group_type)
            ]
            sorted_related_groups = natsorted(related_groups, key=lambda group: group.Name or "Unnamed")

            # Get assigned elements if this is a System
            assigned_elements: list[ifcopenshell.entity_instance] = []
            if group_type == "IfcSystem":
                import ifcopenshell.util.system
                assigned_elements = [
                    elem for elem in ifcopenshell.util.system.get_system_elements(group)
                    if elem.is_a("IfcDistributionElement")
                ]
                sorted_assigned_elements = natsorted(assigned_elements, key=lambda elem: elem.Name or "Unnamed")
            else:
                sorted_assigned_elements = []

            if sorted_related_groups or sorted_assigned_elements:
                new.has_children = True
                if new.is_expanded:
                    for related_group in sorted_related_groups:
                        load_group(related_group, tree_depth=tree_depth + 1)
                    
                    # Group elements by their connectivity (only for Systems)
                    if sorted_assigned_elements and group_type == "IfcSystem":
                        connection_groups = cls._group_connected_elements(sorted_assigned_elements)
                        
                        # Store connection groups for this system
                        connection_groups_data[group.id()] = [
                            [elem.id() for elem in conn_group]
                            for conn_group in connection_groups
                        ]
                        
                        for group_idx, connected_group in enumerate(connection_groups):
                            if len(connected_group) > 1:
                                # Check if we should use a custom start element for this connection group
                                start_element = None
                                import json
                                custom_start_elements = json.loads(bpy.context.scene.BIMSystemProperties.custom_start_elements_json)
                                rebuild_key = f"{group.id()}:{group_idx}"
                                if rebuild_key in custom_start_elements:
                                    start_elem_id = custom_start_elements[rebuild_key]
                                    start_element = tool.Ifc.get().by_id(start_elem_id) if start_elem_id in [e.id() for e in connected_group] else None
                                
                                # Order elements within this connection group
                                ordered_tree = cls._order_connected_elements(connected_group, start_element=start_element)
                                
                                # Create a connection group item
                                group_item = blender_groups.add()
                                # Use negative IDs to distinguish from real IFC entities
                                # Format: -((parent_system_id * 1000) + group_idx + 1)
                                conn_group_id = -((group.id() * 1000) + group_idx + 1)
                                group_item.ifc_definition_id = conn_group_id
                                group_item["name"] = f"({len(connected_group)} elements)"
                                group_item.tree_depth = tree_depth + 1
                                group_item.has_children = True
                                group_item.is_expanded = conn_group_id in expanded_groups
                                if isinstance(group_item, System):
                                    group_item.is_element = False
                                    group_item.is_connection_group = True
                                    group_item.connection_group_id = group_idx
                                    group_item.ifc_class = "ConnectionGroup"
                                    group_item.synthetic_group_type = "connectedElements"
                                
                                # Add elements under this connection group if expanded
                                if group_item.is_expanded:
                                    cls._add_ordered_elements_to_ui(
                                        ordered_tree, blender_groups, tree_depth + 2, expanded_groups
                                    )
                            else:
                                # Single unconnected element, add directly
                                element = connected_group[0]
                                elem_item = blender_groups.add()
                                elem_item.ifc_definition_id = element.id()
                                obj = tool.Ifc.get_object(element)
                                elem_item["name"] = obj.name if obj else (element.Name or "Unnamed")
                                elem_item.tree_depth = tree_depth + 1
                                elem_item.has_children = False
                                elem_item.is_expanded = False
                                if isinstance(elem_item, System):
                                    elem_item.is_element = True
                                    elem_item.is_connection_group = False
                                    elem_item.ifc_class = element.is_a()

        for group in sorted_groups:
            load_group(group)
        
        # Store connection groups data for Systems
        if group_type == "IfcSystem":
            from bonsai.bim.module.system.prop import BIMSystemProperties
            if isinstance(props, BIMSystemProperties):
                props.connection_groups_json = json.dumps(connection_groups_data)

    @classmethod
    def _group_connected_elements(
        cls, elements: list[ifcopenshell.entity_instance]
    ) -> list[list[ifcopenshell.entity_instance]]:
        """Group elements by their port connectivity.
        
        Returns a list of groups, where each group contains elements that are
        connected to each other via ports.
        """
        import ifcopenshell.util.system
        
        ungrouped = set(elements)
        connection_groups: list[list[ifcopenshell.entity_instance]] = []
        
        while ungrouped:
            # Pick an element to start a new group
            seed_element = ungrouped.pop()
            current_group = [seed_element]
            to_explore = [seed_element]
            
            # Find all elements connected to this seed
            while to_explore:
                current = to_explore.pop()
                
                # Get connected elements via ports
                connected_from = ifcopenshell.util.system.get_connected_from(current)
                connected_to = ifcopenshell.util.system.get_connected_to(current)
                connected = set(connected_from + connected_to)
                
                # Add connected elements that are in our element list and not yet grouped
                for connected_elem in connected:
                    if connected_elem in ungrouped:
                        ungrouped.remove(connected_elem)
                        current_group.append(connected_elem)
                        to_explore.append(connected_elem)
            
            connection_groups.append(current_group)
        
        # Sort groups by size (largest first)
        connection_groups.sort(key=len, reverse=True)
        
        return connection_groups
    
    # Branch ID counter for unique synthetic IDs
    _branch_id_counter = 0
    # Store branch data for toggle operations: {branch_id: (branch_tree, blender_groups, depth)}
    _branch_data = {}
    
    @classmethod
    def _add_ordered_elements_to_ui(
        cls,
        ordered_tree: list[dict],
        blender_groups,
        base_depth: int,
        expanded_groups: list[int] | None = None
    ) -> None:
        """Add ordered elements to the UI list with proper indentation and branching."""
        from bonsai.bim.module.system.prop import System
        
        if expanded_groups is None:
            expanded_groups = []
        
        for item in ordered_tree:
            element = item['element']
            is_reference = item['is_reference']
            children = item['children']
            
            elem_item = blender_groups.add()
            elem_item.ifc_definition_id = element.id()
            obj = tool.Ifc.get_object(element)
            
            if is_reference:
                # This is a circular reference
                elem_item["name"] = f"-> {item['reference_name']}"
                elem_item.tree_depth = base_depth
                elem_item.has_children = False
                elem_item.is_expanded = False
                if isinstance(elem_item, System):
                    elem_item.is_element = True
                    elem_item.is_reference = True
                    elem_item.reference_element_name = item['reference_name']
                    elem_item.ifc_class = element.is_a()
            else:
                elem_item["name"] = obj.name if obj else (element.Name or "Unnamed")
                elem_item.tree_depth = base_depth
                elem_item.has_children = False
                elem_item.is_expanded = False
                if isinstance(elem_item, System):
                    elem_item.is_element = True
                    elem_item.is_reference = False
                    elem_item.ifc_class = element.is_a()
                    print(f"DEBUG: Set is_element=True for {element.is_a()} #{element.id()} at depth {base_depth}")
                
                # Handle children
                if len(children) == 1:
                    # Single continuation - add at same depth (no branch)
                    # children[0] is a list of dicts from _build_connection_tree
                    cls._add_ordered_elements_to_ui(children[0], blender_groups, base_depth, expanded_groups)
                elif len(children) > 1:
                    # Multiple branches - create toggleable branch groups
                    print(f"DEBUG: Creating {len(children)} branch groups at element {element.is_a()} #{element.id()}, base_depth={base_depth}")
                    for branch_idx, branch_tree in enumerate(children):
                        # Create a deterministic branch ID based on parent element ID and branch index
                        # Format: -2000000 - (parent_id * 100 + branch_idx)
                        # This ensures the same branch always gets the same ID across re-imports
                        branch_id = -2000000 - (element.id() * 100 + branch_idx)
                        
                        # Count elements in this branch
                        branch_size = cls._count_tree_elements(branch_tree)
                        
                        branch_item = blender_groups.add()
                        branch_item.ifc_definition_id = branch_id
                        branch_item["name"] = f"({branch_size} elements)"
                        branch_item.tree_depth = base_depth + 1
                        branch_item.has_children = True
                        branch_item.is_expanded = branch_id in expanded_groups
                        
                        if isinstance(branch_item, System):
                            branch_item.is_element = False
                            branch_item.is_connection_group = True  # Reuse flag for branch groups
                            branch_item.ifc_class = "Branch"
                            branch_item.synthetic_group_type = "subConnectedPaths"
                        
                        print(f"DEBUG:   Created branch group {branch_id} with {branch_size} elements, expanded={branch_item.is_expanded}")
                        
                        # Add branch elements if expanded
                        if branch_item.is_expanded:
                            cls._add_ordered_elements_to_ui(branch_tree, blender_groups, base_depth + 2, expanded_groups)
    
    @classmethod
    def _order_connected_elements(
        cls, elements: list[ifcopenshell.entity_instance], start_element: ifcopenshell.entity_instance | None = None
    ) -> list[dict]:
        """Order elements in a connection group based on flow direction.
        
        Args:
            elements: List of connected elements to order
            start_element: Optional element to use as starting point. If None, will auto-detect.
        
        Returns a hierarchical list where each item is a dict with:
        - 'element': the IFC element
        - 'is_reference': True if this is a circular reference
        - 'reference_name': Name of referenced element (if is_reference)
        - 'children': List of child items (for branches)
        """
        import ifcopenshell.util.system
        
        if not elements:
            return []
        
        # Use provided start element or find one automatically
        if not start_element:
            # Find starting element: boundary element with SINK port
            start_element = cls._find_start_element(elements)
        if not start_element or start_element not in elements:
            # Fallback: use first element
            start_element = elements[0]
        
        # Build ordered tree structure
        visited = set()
        return cls._build_connection_tree(start_element, elements, visited)
    
    @classmethod
    def _find_start_element(cls, elements: list[ifcopenshell.entity_instance]):
        """Find the best starting element for ordering.
        
        Looks for elements with at least one port not connected to other elements
        in the group, preferring those with SINK ports.
        """
        import ifcopenshell.util.system
        
        print("\n--- Finding start element ---")
        element_set = set(elements)
        boundary_elements = []
        
        for element in elements:
            ports = ifcopenshell.util.system.get_ports(element)
            has_external_port = False
            has_sink_port = False
            
            print(f"  Checking {element.is_a()} #{element.id()}: {len(ports)} ports")
            
            for port in ports:
                flow_dir = getattr(port, 'FlowDirection', 'NOTDEFINED')
                connected_port = ifcopenshell.util.system.get_connected_port(port)
                
                if not connected_port:
                    # Unconnected port
                    print(f"    Port (unconnected, {flow_dir})")
                    has_external_port = True
                    if flow_dir == "SINK":
                        has_sink_port = True
                else:
                    # Check if connected to element outside the group
                    connected_elem = None
                    for rel in connected_port.ContainedIn or []:
                        connected_elem = rel.RelatingElement
                        break
                    
                    if connected_elem and connected_elem not in element_set:
                        print(f"    Port (external, {flow_dir}) -> {connected_elem.is_a()} #{connected_elem.id()}")
                        has_external_port = True
                        if flow_dir == "SINK":
                            has_sink_port = True
                    elif connected_elem:
                        print(f"    Port ({flow_dir}) -> {connected_elem.is_a()} #{connected_elem.id()} (in group)")
            
            if has_external_port:
                boundary_elements.append((element, has_sink_port))
                print(f"    -> Boundary element (has_sink: {has_sink_port})")
        
        print(f"\nFound {len(boundary_elements)} boundary elements")
        
        # Prefer elements with SINK ports
        for elem, has_sink in boundary_elements:
            if has_sink:
                print(f"Selected (has SINK): {elem.is_a()} #{elem.id()} ({elem.Name})")
                return elem
        
        # Otherwise return first boundary element
        if boundary_elements:
            elem = boundary_elements[0][0]
            print(f"Selected (first boundary): {elem.is_a()} #{elem.id()} ({elem.Name})")
            return elem
        
        print("No boundary elements found!")
        return None
    
    @classmethod
    def _build_connection_tree(
        cls,
        element: ifcopenshell.entity_instance,
        all_elements: list[ifcopenshell.entity_instance],
        visited: set[ifcopenshell.entity_instance],
        depth: int = 0
    ) -> list[dict]:
        """Recursively build connection tree starting from element."""
        import ifcopenshell.util.system
        
        indent = "  " * depth
        result = []
        element_set = set(all_elements)
        
        obj = tool.Ifc.get_object(element)
        elem_name = obj.name if obj else (element.Name or "Unnamed")
        
        if element in visited:
            # Circular reference - create reference item
            print(f"{indent}CIRCULAR REF: {element.is_a()} #{element.id()} ({elem_name})")
            result.append({
                'element': element,
                'is_reference': True,
                'reference_name': elem_name,
                'children': []
            })
            return result
        
        print(f"{indent}Building: {element.is_a()} #{element.id()} ({elem_name})")
        visited.add(element)
        
        # Add current element
        item = {
            'element': element,
            'is_reference': False,
            'reference_name': '',
            'children': []
        }
        
        # Find connected elements (follow flow direction)
        connected_to_elements = ifcopenshell.util.system.get_connected_to(element)
        connected_from_elements = ifcopenshell.util.system.get_connected_from(element)
        
        print(f"{indent}  Connected TO: {len(connected_to_elements)} elements")
        for conn_elem in connected_to_elements:
            print(f"{indent}    -> {conn_elem.is_a()} #{conn_elem.id()} ({conn_elem.Name})")
        
        print(f"{indent}  Connected FROM: {len(connected_from_elements)} elements")
        for conn_elem in connected_from_elements:
            print(f"{indent}    <- {conn_elem.is_a()} #{conn_elem.id()} ({conn_elem.Name})")
        
        # Filter to only elements in our group and deduplicate (remove elements in both TO and FROM)
        # Use dict.fromkeys to preserve order while removing duplicates
        combined_elements = list(dict.fromkeys(connected_to_elements + connected_from_elements))
        next_elements = [
            e for e in combined_elements
            if e in element_set and e not in visited
        ]
        
        print(f"{indent}  Next elements (in group, not visited): {len(next_elements)}")
        for next_elem in next_elements:
            print(f"{indent}    => {next_elem.is_a()} #{next_elem.id()} ({next_elem.Name})")
        
        if len(next_elements) == 0:
            # Leaf node
            print(f"{indent}  LEAF (no next elements)")
            result.append(item)
        elif len(next_elements) == 1:
            # Single path - continue on same level
            print(f"{indent}  SINGLE PATH (continuing)")
            result.append(item)
            result.extend(cls._build_connection_tree(next_elements[0], all_elements, visited, depth))
        else:
            # Multiple branches - add each as a separate child branch
            print(f"{indent}  BRANCHING ({len(next_elements)} branches)")
            for branch_idx, next_elem in enumerate(next_elements):
                print(f"{indent}  Branch {branch_idx + 1}:")
                child_tree = cls._build_connection_tree(next_elem, all_elements, visited, depth + 1)
                # Keep each branch as a separate list in children
                item['children'].append(child_tree)
            result.append(item)
        
        return result

    @classmethod
    def _count_tree_elements(cls, tree: list[dict]) -> int:
        """Count total number of elements in a tree."""
        count = 0
        for item in tree:
            count += 1  # The item itself
            children = item.get('children', [])
            for child_list in children:
                count += cls._count_tree_elements(child_list)
        return count
    
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
    def toggle_connection_group(cls, connection_group_id: int, group_type: GroupType, option: ToggleOption) -> None:
        """Toggle expansion state of a connection group or branch group (synthetic group with negative ID)."""
        print(f"DEBUG toggle_connection_group: ID={connection_group_id}, type={group_type}, option={option}")
        # Branch groups use IDs < -2000000, connection groups use IDs < -1000000
        if connection_group_id < -2000000:
            print(f"DEBUG: This is a BRANCH group")
            # Branch group - use similar pattern with expanded_groups_json
            props, _ = cls.get_groups_data(group_type)
            expanded_groups: set[int]
            expanded_groups = set(json.loads(props.expanded_groups_json))
            print(f"DEBUG: Current expanded groups: {expanded_groups}")
            if option == "EXPAND":
                expanded_groups.add(connection_group_id)
                print(f"DEBUG: Added {connection_group_id} to expanded groups")
            elif connection_group_id in expanded_groups:
                expanded_groups.remove(connection_group_id)
                print(f"DEBUG: Removed {connection_group_id} from expanded groups")
            props.expanded_groups_json = json.dumps(list(expanded_groups))
            print(f"DEBUG: New expanded groups: {expanded_groups}")
            print(f"DEBUG: Re-importing groups...")
            cls.import_groups(group_type)
        else:
            print(f"DEBUG: This is a CONNECTION group")
            # Connection group - original logic
            props, _ = cls.get_groups_data(group_type)
            expanded_groups: set[int]
            expanded_groups = set(json.loads(props.expanded_groups_json))
            if option == "EXPAND":
                expanded_groups.add(connection_group_id)
            elif connection_group_id in expanded_groups:
                expanded_groups.remove(connection_group_id)
            props.expanded_groups_json = json.dumps(list(expanded_groups))
            cls.import_groups(group_type)

    @classmethod
    def update_uilist_index(cls, group_type: GroupType) -> None:
        props, blender_groups = cls.get_groups_data(group_type)
        props.active_group_index = tool.Blender.get_valid_uilist_index(props.active_group_index, blender_groups)
