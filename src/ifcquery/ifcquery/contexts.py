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

import ifcopenshell


def contexts(model: ifcopenshell.file) -> list[dict]:
    """Return all geometric representation contexts and subcontexts.

    :param model: The in-memory IFC model.
    :return: List of dicts with id, type, context_type, context_identifier,
        and (for subcontexts) target_view and parent_context_id.
    """
    results = []
    for ctx in model.by_type("IfcGeometricRepresentationContext"):
        entry = {
            "id": ctx.id(),
            "type": ctx.is_a(),
            "context_type": getattr(ctx, "ContextType", None),
            "context_identifier": getattr(ctx, "ContextIdentifier", None),
        }
        if ctx.is_a("IfcGeometricRepresentationSubContext"):
            entry["target_view"] = ctx.TargetView
            parent = ctx.ParentContext
            entry["parent_context_id"] = parent.id() if parent else None
        results.append(entry)
    return results
