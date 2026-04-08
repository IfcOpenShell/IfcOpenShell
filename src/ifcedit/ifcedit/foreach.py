# IfcEdit - CLI wrapper for ifcopenshell.api mutation functions
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
#
# This file is part of IfcEdit.
#
# IfcEdit is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcEdit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcEdit.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import ifcopenshell

from ifcedit.run import run_api


def _substitute(template: str, item: dict) -> str:
    """Replace {key} placeholders in template with values from item."""
    for key, value in item.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template


def run_foreach(
    model: ifcopenshell.file,
    module: str,
    function: str,
    raw_kwargs_template: dict[str, str],
    items: list[dict],
) -> dict:
    """Apply an API function to each item in a list, substituting {field} placeholders.

    Opens the model once, applies the mutation for every item, and returns a summary.
    The caller is responsible for saving the model.

    Args:
        model: The open IFC model (mutated in place).
        module: API module name (e.g. "root").
        function: Function name (e.g. "remove_product").
        raw_kwargs_template: Arg templates with {field} placeholders, e.g. {"product": "{id}"}.
        items: List of dicts (e.g. from ifcquery select output).

    Returns:
        {"ok": True, "count": N, "errors": []} on full success,
        {"ok": False, "count": N, "errors": [{...}]} if any item failed.
    """
    errors = []
    count = 0

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append({"index": i, "item": item, "error": "item is not a dict"})
            continue

        substituted = {k: _substitute(v, item) for k, v in raw_kwargs_template.items()}
        result = run_api(model, module, function, substituted)

        if result["ok"]:
            count += 1
        else:
            errors.append({"index": i, "item": item, "error": result["error"]})

    return {
        "ok": len(errors) == 0,
        "count": count,
        "errors": errors,
    }
