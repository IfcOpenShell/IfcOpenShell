# This file was generated with the assistance of an AI coding tool.
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

import json
import typing

import ifcopenshell


def coerce_value(value_str: str, type_hint, model: ifcopenshell.file | None = None):
    """Convert a CLI string argument to the proper Python type based on a type hint.

    Args:
        value_str: The raw string from the CLI.
        type_hint: The type annotation from the function signature.
        model: An open IFC model, needed to resolve entity instance references by ID.

    Returns:
        The converted Python value.

    Raises:
        ValueError: If the value cannot be converted.
        TypeError: If the type hint is not supported.
    """
    if type_hint is None:
        return value_str

    origin = typing.get_origin(type_hint)
    args = typing.get_args(type_hint)

    # Union / Optional
    if origin is typing.Union:
        non_none_types = [a for a in args if a is not type(None)]
        if value_str.lower() == "none":
            if type(None) in args:
                return None
        # Try each non-None type in order
        for t in non_none_types:
            try:
                return coerce_value(value_str, t, model)
            except (ValueError, TypeError):
                continue
        raise ValueError(f"Cannot convert '{value_str}' to any of {non_none_types}")

    # Literal
    if origin is typing.Literal:
        allowed = args
        if value_str in [str(a) for a in allowed]:
            # return the actual literal value with proper type
            for a in allowed:
                if str(a) == value_str:
                    return a
        raise ValueError(f"'{value_str}' is not one of: {', '.join(repr(a) for a in allowed)}")

    # list types
    if origin is list:
        if args and _is_entity_type(args[0]):
            return _coerce_entity_list(value_str, model)
        if args:
            items = _split_list(value_str)
            return [coerce_value(item.strip(), args[0], model) for item in items]
        return _split_list(value_str)

    # dict types
    if origin is dict:
        return json.loads(value_str)

    # Simple types
    if type_hint is str:
        return value_str
    if type_hint is int:
        return int(value_str.lstrip("#"))
    if type_hint is float:
        return float(value_str)
    if type_hint is bool:
        return value_str.lower() in ("true", "1", "yes")

    # entity_instance
    if _is_entity_type(type_hint):
        return _coerce_entity(value_str, model)

    # Fallback: try json.loads for complex types, then plain string
    try:
        return json.loads(value_str)
    except (json.JSONDecodeError, TypeError):
        return value_str


def _is_entity_type(hint) -> bool:
    """Check if a type hint refers to ifcopenshell.entity_instance."""
    if hint is ifcopenshell.entity_instance:
        return True
    if isinstance(hint, type) and issubclass(hint, ifcopenshell.entity_instance):
        return True
    return False


def _coerce_entity(value_str: str | int, model: ifcopenshell.file | None) -> ifcopenshell.entity_instance:
    """Resolve a step ID string like '123' or '#123' to an entity instance."""
    if model is None:
        raise ValueError("Cannot resolve entity reference without an IFC model")
    if isinstance(value_str, int):
        entity_id = value_str
    else:
        entity_id = int(value_str.strip().lstrip("#"))
    try:
        return model.by_id(entity_id)
    except RuntimeError:
        raise ValueError(f"Entity #{entity_id} not found in model")


def _coerce_entity_list(value_str: str, model: ifcopenshell.file | None) -> list[ifcopenshell.entity_instance]:
    """Resolve a comma-separated list of step IDs to entity instances."""
    items = _split_list(value_str)
    return [_coerce_entity(item.strip(), model) for item in items]


def _split_list(value_str: str) -> list[str]:
    """Split a comma-separated string, handling JSON arrays too."""
    value_str = value_str.strip()
    if value_str.startswith("["):
        try:
            parsed = json.loads(value_str)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except json.JSONDecodeError:
            pass
    return [item.strip() for item in value_str.split(",") if item.strip()]
