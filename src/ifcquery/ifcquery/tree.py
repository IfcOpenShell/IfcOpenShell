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


def _element_summary(element: ifcopenshell.entity_instance) -> dict[str, Any]:
    """Return a minimal summary dict for an element."""
    return {
        "id": element.id(),
        "type": element.is_a(),
        "name": element.Name if hasattr(element, "Name") else None,
    }


def _build_spatial_node(element: ifcopenshell.entity_instance, max_depth: int | None, depth: int) -> dict[str, Any]:
    """Recursively build a spatial tree node."""
    node = _element_summary(element)
    # Both decomposed sub-spaces and contained elements sit one level below this node.
    expand = max_depth is None or depth < max_depth

    # Get aggregated children (Site in Project, Building in Site, Storey in Building, etc.)
    aggregates = []
    for rel in getattr(element, "IsDecomposedBy", []):
        for child in rel.RelatedObjects:
            aggregates.append(_build_spatial_node(child, max_depth, depth + 1) if expand else child)

    # Get contained elements (walls, slabs, etc. in a storey/space)
    contained = []
    for rel in getattr(element, "ContainsElements", []):
        for child in rel.RelatedElements:
            contained.append(_element_summary(child) if expand else child)

    if aggregates:
        node["children"] = aggregates if expand else {"truncated": True, "count": len(aggregates)}
    if contained:
        node["elements"] = contained if expand else {"truncated": True, "count": len(contained)}

    return node


def tree(model: ifcopenshell.file, max_depth: int | None = None) -> dict[str, Any] | list[dict[str, Any]]:
    """Return the spatial hierarchy of the model as a nested tree.

    Starts at ``IfcProject`` and descends through decomposition (site,
    building, storeys) and containment (the elements placed in each storey).
    Every node carries ``id``, ``type`` and ``name``; ``children`` holds
    decomposed sub-spaces and ``elements`` holds contained elements, and
    either key is omitted when empty. Returns a list when the file contains
    several projects, or an ``error`` key when it contains none.

    :param model: The in-memory IFC model.
    :param max_depth: Levels to expand, counting the project as level 1; a
        node's contained elements are one level below it, like its
        sub-spaces. Past the cutoff ``children`` and ``elements`` are each
        replaced by a ``{"truncated": True, "count": N}`` marker giving the
        number not expanded. ``None`` (default) expands to unlimited depth.
    """
    projects = model.by_type("IfcProject")
    if not projects:
        return {"error": "No IfcProject found in model"}
    if len(projects) == 1:
        return _build_spatial_node(projects[0], max_depth, depth=1)
    return [_build_spatial_node(p, max_depth, depth=1) for p in projects]
