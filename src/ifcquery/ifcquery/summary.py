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

from collections import Counter
from typing import Any

import ifcopenshell


def summary(model: ifcopenshell.file) -> dict[str, Any]:
    """Return a model overview with schema, element counts, and project info."""
    # Count elements by IFC type, sorted by count descending
    type_counter: Counter[str] = Counter()
    total = 0
    for entity in model:
        type_counter[entity.is_a()] += 1
        total += 1

    result: dict[str, Any] = {
        "schema": model.schema,
        "total_entities": total,
    }

    projects = model.by_type("IfcProject")
    if projects:
        project = projects[0]
        result["project"] = {
            "id": project.id(),
            "name": project.Name,
            "description": project.Description,
        }

    result["types"] = dict(type_counter.most_common())
    return result
