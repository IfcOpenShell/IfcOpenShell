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

from collections.abc import Callable
from typing import Any

import ifcopenshell
import ifcopenshell.util.structural as structural_util


def _ref(entity: ifcopenshell.entity_instance | None) -> dict[str, Any] | None:
    if entity is None:
        return None
    return {"id": entity.id(), "type": entity.is_a(), "name": getattr(entity, "Name", None)}


def _plain(value: Any) -> Any:
    """A value as JSON: a defined type unwrapped, an entity as None."""
    if isinstance(value, ifcopenshell.entity_instance):
        return value.wrappedValue if value.id() == 0 else None
    if isinstance(value, (tuple, list)):
        values = [_plain(v) for v in value]
        return None if any(v is None for v in values) else values
    return value


def _values(entity: ifcopenshell.entity_instance | None) -> dict[str, Any]:
    """The set attributes of a load or boundary condition other than its name."""
    if entity is None:
        return {}
    values = {}
    for attribute, value in entity.get_info(include_identifier=False, recursive=False).items():
        if attribute in ("type", "Name"):
            continue
        value = _plain(value)
        if value is not None:
            values[attribute] = value
    return values


def _expand(
    entities: list[ifcopenshell.entity_instance],
    describe: Callable[[ifcopenshell.entity_instance, int], dict[str, Any]],
    max_depth: int | None,
    depth: int,
) -> list[dict[str, Any]] | dict[str, Any]:
    if max_depth is not None and depth > max_depth:
        return {"truncated": True, "count": len(entities)} if entities else []
    return [describe(e, depth) for e in entities]


def _activity(activity: ifcopenshell.entity_instance) -> dict[str, Any]:
    items = [rel.RelatingElement for rel in activity.AssignedToStructuralItem]
    return {
        **_ref(activity),
        "global_or_local": activity.GlobalOrLocal,
        "item": _ref(items[0]) if items else None,
        "load": {**_ref(activity.AppliedLoad), "values": _values(activity.AppliedLoad)},
    }


def _member(member: ifcopenshell.entity_instance, depth: int, max_depth: int | None) -> dict[str, Any]:
    return {
        **_ref(member),
        "predefined_type": getattr(member, "PredefinedType", None),
        "connections": _expand(
            structural_util.get_member_connections(member), lambda c, d: _ref(c), max_depth, depth + 1
        ),
        "building_elements": _expand(
            structural_util.get_building_elements(member), lambda e, d: _ref(e), max_depth, depth + 1
        ),
        "activities": _expand(structural_util.get_item_activities(member), lambda a, d: _ref(a), max_depth, depth + 1),
    }


def _connection(connection: ifcopenshell.entity_instance, depth: int, max_depth: int | None) -> dict[str, Any]:
    condition = connection.AppliedCondition
    return {
        **_ref(connection),
        "applied_condition": {**_ref(condition), "values": _values(condition)} if condition else None,
        "members": _expand(
            structural_util.get_connection_members(connection), lambda m, d: _ref(m), max_depth, depth + 1
        ),
        "activities": _expand(
            structural_util.get_item_activities(connection), lambda a, d: _ref(a), max_depth, depth + 1
        ),
    }


def _load_case(case: ifcopenshell.entity_instance, depth: int, max_depth: int | None) -> dict[str, Any]:
    return {
        **_ref(case),
        "action_type": case.ActionType,
        "action_source": case.ActionSource,
        "coefficient": case.Coefficient,
        "self_weight_coefficients": (
            list(case.SelfWeightCoefficients) if getattr(case, "SelfWeightCoefficients", None) else None
        ),
        "activities": _expand(
            structural_util.get_group_activities(case), lambda a, d: _activity(a), max_depth, depth + 1
        ),
    }


def _load_combination(combination: ifcopenshell.entity_instance, depth: int, max_depth: int | None) -> dict[str, Any]:
    factors = structural_util.get_combination_factors(combination)
    return {
        **_ref(combination),
        "purpose": combination.Purpose,
        "coefficient": combination.Coefficient,
        "load_cases": _expand(list(factors), lambda c, d: {**_ref(c), "factor": factors[c]}, max_depth, depth + 1),
    }


def structural(model: ifcopenshell.file, max_depth: int | None = None) -> list[dict[str, Any]]:
    """List the structural analysis models with their items and loads.

    For each ``IfcStructuralAnalysisModel``: its ``members`` with the
    connections they are joined to, the building elements they stand for
    and the activities on them; its ``connections`` with their boundary
    condition, members and activities; its ``load_cases`` with their
    activities, each with its load and the item it acts on; and its
    ``load_combinations`` with the factor of each load case.

    Load cases and combinations are those the model is loaded by
    (``LoadedBy``), and the load cases of those combinations. A load group
    that no model is loaded by is not listed. Returns an empty list when the
    model has no structural analysis model.

    :param model: The in-memory IFC model.
    :param max_depth: Levels to expand, counting the analysis models as level
        1 and their members, connections, load cases and combinations as level
        2. Past the cutoff a list is replaced by a ``{"truncated": True,
        "count": N}`` marker. ``None`` (default) expands to unlimited depth.
    """
    result = []
    for analysis_model in model.by_type("IfcStructuralAnalysisModel"):
        items = structural_util.get_model_items(analysis_model)
        members = [i for i in items if i.is_a("IfcStructuralMember")]
        connections = [i for i in items if i.is_a("IfcStructuralConnection")]
        combinations = [
            g for g in structural_util.get_model_load_groups(analysis_model) if g.PredefinedType == "LOAD_COMBINATION"
        ]
        result.append(
            {
                **_ref(analysis_model),
                "predefined_type": analysis_model.PredefinedType,
                "members": _expand(members, lambda m, d: _member(m, d, max_depth), max_depth, 2),
                "connections": _expand(connections, lambda c, d: _connection(c, d, max_depth), max_depth, 2),
                "load_cases": _expand(
                    structural_util.get_model_load_cases(analysis_model),
                    lambda c, d: _load_case(c, d, max_depth),
                    max_depth,
                    2,
                ),
                "load_combinations": _expand(
                    combinations, lambda c, d: _load_combination(c, d, max_depth), max_depth, 2
                ),
            }
        )
    return result
