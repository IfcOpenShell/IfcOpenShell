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
import ifcopenshell.util.selector


def select(model: ifcopenshell.file, query: str) -> list[dict[str, Any]]:
    """Filter elements using ifcopenshell selector syntax and return matching element summaries.

    Examples:
    - ``IfcWall`` — all walls
    - ``IfcWall, IfcColumn`` — walls and columns
    - ``! IfcWall`` — everything except walls
    - ``IfcWall, Name = "My Wall"`` — walls with a specific name attribute
    - ``type = "Concrete Wall"`` — elements assigned that type product
    - ``material = "Concrete"`` — elements with that material
    """
    elements = ifcopenshell.util.selector.filter_elements(model, query)
    results = []
    for element in sorted(elements, key=lambda e: e.id()):
        entry: dict[str, Any] = {
            "id": element.id(),
            "type": element.is_a(),
            "repr": str(element),
        }
        if hasattr(element, "Name"):
            entry["name"] = element.Name
        results.append(entry)
    return results
