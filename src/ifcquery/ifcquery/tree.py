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


def _element_summary(element: ifcopenshell.entity_instance) -> dict[str, Any]:
    """Return a minimal summary dict for an element."""
    return {
        "id": element.id(),
        "type": element.is_a(),
        "name": element.Name if hasattr(element, "Name") else None,
    }


def _build_spatial_node(element: ifcopenshell.entity_instance) -> dict[str, Any]:
    """Recursively build a spatial tree node."""
    node = _element_summary(element)

    # Get aggregated children (Site in Project, Building in Site, Storey in Building, etc.)
    aggregates = []
    for rel in getattr(element, "IsDecomposedBy", []):
        for child in rel.RelatedObjects:
            aggregates.append(_build_spatial_node(child))

    # Get contained elements (walls, slabs, etc. in a storey/space)
    contained = []
    for rel in getattr(element, "ContainsElements", []):
        for child in rel.RelatedElements:
            contained.append(_element_summary(child))

    if aggregates:
        node["children"] = aggregates
    if contained:
        node["elements"] = contained

    return node


def tree(model: ifcopenshell.file) -> dict[str, Any] | list[dict[str, Any]]:
    """Return the spatial hierarchy tree starting from IfcProject."""
    projects = model.by_type("IfcProject")
    if not projects:
        return {"error": "No IfcProject found in model"}
    if len(projects) == 1:
        return _build_spatial_node(projects[0])
    return [_build_spatial_node(p) for p in projects]
