# IfcQuery - IFC model interrogation CLI
# Copyright (C) 2025 Bruno Postle <bruno@postle.net>
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
    """Filter elements using selector syntax and return matching element summaries."""
    elements = ifcopenshell.util.selector.filter_elements(model, query)
    results = []
    for element in sorted(elements, key=lambda e: e.id()):
        entry: dict[str, Any] = {
            "id": element.id(),
            "type": element.is_a(),
        }
        if hasattr(element, "Name"):
            entry["name"] = element.Name
        results.append(entry)
    return results
