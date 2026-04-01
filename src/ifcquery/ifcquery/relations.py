# This file was generated with the assistance of an AI coding tool.
# IfcQuery - IFC model interrogation CLI
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
#
# This file is part of IfcQuery.
#
# IfcQuery is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcQuery is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcQuery.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

from typing import Any

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.system


def _ref(element: ifcopenshell.entity_instance) -> dict[str, Any]:
    """Serialize an element to a compact reference dict."""
    result: dict[str, Any] = {"id": element.id(), "type": element.is_a()}
    if hasattr(element, "Name") and element.Name:
        result["name"] = element.Name
    return result


def _ref_or_none(element: ifcopenshell.entity_instance | None) -> dict[str, Any] | None:
    return _ref(element) if element is not None else None


def _ref_list(elements) -> list[dict[str, Any]]:
    return [_ref(e) for e in elements]


def _traverse_up(element: ifcopenshell.entity_instance) -> list[dict[str, Any]]:
    """Walk the hierarchy from element up to IfcProject."""
    chain = [_ref(element)]
    current = element
    while True:
        parent = ifcopenshell.util.element.get_parent(current)
        if parent is None:
            break
        chain.append(_ref(parent))
        current = parent
    return chain


def _all_relations(model: ifcopenshell.file, element: ifcopenshell.entity_instance) -> dict[str, Any]:
    """Collect all relationships for an element."""
    result: dict[str, Any] = {
        "id": element.id(),
        "type": element.is_a(),
    }
    if hasattr(element, "Name") and element.Name:
        result["name"] = element.Name

    # Hierarchy (upward)
    hierarchy: dict[str, Any] = {}
    parent = ifcopenshell.util.element.get_parent(element)
    if parent is not None:
        hierarchy["parent"] = _ref(parent)
    container = ifcopenshell.util.element.get_container(element)
    if container is not None:
        hierarchy["container"] = _ref(container)
    aggregate = ifcopenshell.util.element.get_aggregate(element)
    if aggregate is not None:
        hierarchy["aggregate"] = _ref(aggregate)
    nest = ifcopenshell.util.element.get_nest(element)
    if nest is not None:
        hierarchy["nest"] = _ref(nest)
    filled_void = ifcopenshell.util.element.get_filled_void(element)
    if filled_void is not None:
        hierarchy["filled_void"] = _ref(filled_void)
    voided_element = ifcopenshell.util.element.get_voided_element(element)
    if voided_element is not None:
        hierarchy["voided_element"] = _ref(voided_element)
    if hierarchy:
        result["hierarchy"] = hierarchy

    # Children (downward)
    children: dict[str, Any] = {}
    contained = ifcopenshell.util.element.get_contained(element)
    if contained:
        children["contained"] = _ref_list(contained)
    parts = ifcopenshell.util.element.get_parts(element)
    if parts:
        children["parts"] = _ref_list(parts)
    components = ifcopenshell.util.element.get_components(element)
    if components:
        children["components"] = _ref_list(components)
    openings = list(ifcopenshell.util.element.get_openings(element))
    if openings:
        children["openings"] = _ref_list(openings)
    if children:
        result["children"] = children

    # Type relationship
    type_relationship: dict[str, Any] = {}
    element_type = ifcopenshell.util.element.get_type(element)
    if element_type is not None:
        type_relationship["type_of"] = _ref(element_type)
    try:
        occurrences = ifcopenshell.util.element.get_types(element)
        if occurrences:
            type_relationship["occurrences"] = _ref_list(occurrences)
    except Exception:
        pass
    if type_relationship:
        result["type_relationship"] = type_relationship

    # Groups
    groups = ifcopenshell.util.element.get_groups(element)
    if groups:
        result["groups"] = _ref_list(groups)

    # Systems
    systems = ifcopenshell.util.system.get_element_systems(element)
    if systems:
        result["systems"] = _ref_list(systems)

    # Zones
    zones = ifcopenshell.util.system.get_element_zones(element)
    if zones:
        result["zones"] = _ref_list(zones)

    # Material
    material = ifcopenshell.util.element.get_material(element)
    if material is not None:
        result["material"] = _ref(material)

    # Referenced structures
    referenced = ifcopenshell.util.element.get_referenced_structures(element)
    if referenced:
        result["referenced_structures"] = _ref_list(referenced)

    # Connections
    connections: dict[str, Any] = {}
    connected_to = ifcopenshell.util.system.get_connected_to(element)
    if connected_to:
        connections["connected_to"] = _ref_list(connected_to)
    connected_from = ifcopenshell.util.system.get_connected_from(element)
    if connected_from:
        connections["connected_from"] = _ref_list(connected_from)
    ports = ifcopenshell.util.system.get_ports(element)
    if ports:
        connections["ports"] = _ref_list(ports)
    if connections:
        result["connections"] = connections

    return result


def _collect_elements(data: Any, seen: set[int], result: list[dict[str, Any]]) -> None:
    """Recursively collect all element refs (dicts with 'id') from a nested structure."""
    if isinstance(data, dict):
        if "id" in data and isinstance(data["id"], int):
            eid = data["id"]
            if eid not in seen:
                seen.add(eid)
                result.append(
                    {"id": data["id"], "type": data.get("type"), "name": data.get("name")}
                    if "name" in data
                    else {"id": data["id"], "type": data.get("type")}
                )
        for v in data.values():
            _collect_elements(v, seen, result)
    elif isinstance(data, list):
        for item in data:
            _collect_elements(item, seen, result)


def relations(
    model: ifcopenshell.file, element: ifcopenshell.entity_instance, traverse: str | None = None
) -> dict[str, Any] | list[dict[str, Any]]:
    """Return relationships for an element, or hierarchy chain if traverse='up'."""
    if traverse == "up":
        return _traverse_up(element)
    result = _all_relations(model, element)

    # Flat list of subject + all referenced elements, deduplicated.
    # Allows --format ids to extract all involved IDs without jq.
    seen: set[int] = set()
    elements: list[dict[str, Any]] = []
    _collect_elements(result, seen, elements)
    result["elements"] = elements

    return result
