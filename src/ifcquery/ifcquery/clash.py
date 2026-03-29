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

import multiprocessing
import sys
from typing import Any

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element


def _ref(element: ifcopenshell.entity_instance) -> dict[str, Any]:
    """Serialize an element to a compact reference dict."""
    result: dict[str, Any] = {"id": element.id(), "type": element.is_a()}
    if hasattr(element, "Name") and element.Name:
        result["name"] = element.Name
    return result


def _get_scope_elements(
    model: ifcopenshell.file, element: ifcopenshell.entity_instance, scope: str
) -> tuple[set[ifcopenshell.entity_instance], str]:
    """Return set of elements to check against and the effective scope used.

    Returns (elements, effective_scope) where effective_scope may differ from
    the requested scope if fallback was needed.
    """
    if scope == "storey":
        container = ifcopenshell.util.element.get_container(element)
        if container is not None:
            siblings = set(ifcopenshell.util.element.get_contained(container))
            siblings.discard(element)
            return siblings, "storey"
        else:
            print(
                f"Warning: Element #{element.id()} has no spatial container, falling back to --scope all",
                file=sys.stderr,
            )

    # scope == "all" or fallback
    elements = set(model.by_type("IfcElement"))
    elements -= set(model.by_type("IfcFeatureElement"))
    elements.discard(element)
    return elements, "all"


def _build_tree(model: ifcopenshell.file, elements: set[ifcopenshell.entity_instance]) -> ifcopenshell.geom.tree | None:
    """Build geometry tree for given elements using iterator.

    Returns None if iterator fails to initialize (no geometry available).
    """
    geom_settings = ifcopenshell.geom.settings()
    geom_settings.set("use-world-coords", True)
    geom_tree = ifcopenshell.geom.tree()
    iterator = ifcopenshell.geom.iterator(geom_settings, model, multiprocessing.cpu_count(), include=list(elements))
    if not iterator.initialize():
        return None
    while True:
        geom_tree.add_element(iterator.get())
        if not iterator.next():
            break
    return geom_tree


def _format_clash(clash_result, geom_tree: ifcopenshell.geom.tree, model: ifcopenshell.file) -> dict[str, Any]:
    """Format a single clash result to dict."""
    # clash result .a/.b are C++ wrapper entity_instances without .Name;
    # look up the Python entity from the model by id for proper serialization
    other = model.by_id(clash_result.b.id())
    return {
        "element": _ref(other),
        "type": geom_tree.get_clash_type(clash_result.clash_type),
        "distance": clash_result.distance,
        "p1": list(clash_result.p1),
        "p2": list(clash_result.p2),
    }


def clash(
    model: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    clearance: float | None = None,
    tolerance: float = 0.002,
    scope: str = "storey",
) -> dict[str, Any]:
    """Check element for geometric clashes against other elements.

    :param model: The IFC model.
    :param element: The element to check.
    :param clearance: Minimum clearance distance; if provided, runs clearance check.
    :param tolerance: Intersection tolerance in meters (default 0.002).
    :param scope: Which elements to check against: "storey" or "all".
    :return: Dict with clash results suitable for JSON serialization.
    """
    result: dict[str, Any] = {"element": _ref(element)}

    # Get scope elements
    scope_elements, effective_scope = _get_scope_elements(model, element, scope)
    result["scope"] = effective_scope

    if not scope_elements:
        result["pass"] = True
        result["checks"] = {"intersection": {"pass": True, "tolerance": tolerance, "clashes": []}}
        if clearance is not None:
            result["checks"]["clearance"] = {"pass": True, "clearance": clearance, "clashes": []}
        return result

    # Build geometry tree for target element + scope elements
    all_elements = scope_elements | {element}
    geom_tree = _build_tree(model, all_elements)

    if geom_tree is None:
        result["pass"] = None
        result["error"] = f"No geometry for element #{element.id()}"
        return result

    # Run intersection check
    intersection_clashes = geom_tree.clash_intersection_many(
        [element], list(scope_elements), tolerance=tolerance, check_all=True
    )
    intersection_results = [_format_clash(c, geom_tree, model) for c in intersection_clashes]
    checks: dict[str, Any] = {
        "intersection": {
            "pass": len(intersection_results) == 0,
            "tolerance": tolerance,
            "clashes": intersection_results,
        }
    }

    all_pass = len(intersection_results) == 0

    # Run clearance check if requested
    if clearance is not None:
        clearance_clashes = geom_tree.clash_clearance_many(
            [element], list(scope_elements), clearance=clearance, check_all=True
        )
        clearance_results = [_format_clash(c, geom_tree, model) for c in clearance_clashes]
        checks["clearance"] = {
            "pass": len(clearance_results) == 0,
            "clearance": clearance,
            "clashes": clearance_results,
        }
        if clearance_results:
            all_pass = False

    result["pass"] = all_pass
    result["checks"] = checks

    # Flat list of subject + all clashing elements across all checks, deduplicated.
    # Allows --format ids to extract all involved IDs without jq.
    seen: set[int] = {element.id()}
    involved = [_ref(element)]
    for check in checks.values():
        for clash_item in check.get("clashes", []):
            eid = clash_item["element"]["id"]
            if eid not in seen:
                seen.add(eid)
                involved.append(clash_item["element"])
    result["elements"] = involved

    return result
