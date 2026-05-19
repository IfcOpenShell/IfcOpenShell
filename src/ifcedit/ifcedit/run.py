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

import importlib
import inspect
import typing

import ifcopenshell

from ifcedit.coerce import coerce_value


def _is_file_type(hint) -> bool:
    """Check if a type hint refers to ifcopenshell.file (or Optional[ifcopenshell.file])."""
    if hint is ifcopenshell.file:
        return True
    origin = typing.get_origin(hint)
    args = typing.get_args(hint)
    if origin is typing.Union and ifcopenshell.file in args:
        return True
    return False


def run_api(
    model: ifcopenshell.file,
    module: str,
    function: str,
    raw_kwargs: dict[str, str],
) -> dict:
    """Execute an ifcopenshell.api function with CLI-provided string arguments.

    Args:
        model: The open IFC model.
        module: API module name (e.g. "root").
        function: Function name (e.g. "create_entity").
        raw_kwargs: String keyword arguments from the CLI.

    Returns:
        A dict with {"ok": True, "result": ...} on success,
        or {"ok": False, "error": "..."} on failure.
    """
    try:
        fn = _import_function(module, function)
    except (ImportError, AttributeError) as e:
        return {"ok": False, "error": f"Cannot find function '{module}.{function}': {e}"}

    try:
        hints = typing.get_type_hints(fn)
    except Exception:
        hints = {}

    sig = inspect.signature(fn)
    coerced_kwargs = {}

    # Pass 1: coerce ifcopenshell.file-typed params first (e.g. library= in append_asset).
    # The opened file is then used as the lookup file for entity resolution in pass 2.
    opened_files: list[ifcopenshell.file] = []
    for name, value_str in raw_kwargs.items():
        if name not in sig.parameters:
            return {"ok": False, "error": f"Unknown parameter '{name}' for {module}.{function}"}
        hint = hints.get(name)
        if not _is_file_type(hint):
            continue
        try:
            coerced = coerce_value(value_str, hint, model)
            coerced_kwargs[name] = coerced
            if isinstance(coerced, ifcopenshell.file):
                opened_files.append(coerced)
        except (ValueError, TypeError) as e:
            return {"ok": False, "error": f"Cannot convert parameter '{name}': {e}"}

    # Pass 2: coerce remaining params. Entity instance IDs are resolved from the opened
    # library file (if any), since you are always appending from another file, never
    # from the current model.
    lookup_file = opened_files[0] if opened_files else None
    for name, value_str in raw_kwargs.items():
        if name in coerced_kwargs:
            continue
        if name not in sig.parameters:
            return {"ok": False, "error": f"Unknown parameter '{name}' for {module}.{function}"}
        hint = hints.get(name)
        try:
            coerced_kwargs[name] = coerce_value(value_str, hint, model, lookup_file=lookup_file)
        except (ValueError, TypeError) as e:
            return {"ok": False, "error": f"Cannot convert parameter '{name}': {e}"}

    # Determine if the function takes 'file' as its first parameter
    first_param = next(iter(sig.parameters), None)
    try:
        if first_param == "file":
            result = fn(model, **coerced_kwargs)
        else:
            result = fn(**coerced_kwargs)
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    return {"ok": True, "result": serialize_result(result)}


def _import_function(module: str, function: str):
    """Import and return the underlying function from ifcopenshell.api."""
    fn_module = importlib.import_module(f"ifcopenshell.api.{module}.{function}")
    fn = getattr(fn_module, function)
    return fn


def serialize_result(value) -> object:
    """Serialize an API result to a JSON-friendly structure."""
    if value is None:
        return None
    if isinstance(value, ifcopenshell.entity_instance):
        return _serialize_entity(value)
    if isinstance(value, (list, tuple, set, frozenset)):
        return [serialize_result(item) for item in value]
    if isinstance(value, dict):
        return {str(k): serialize_result(v) for k, v in value.items()}
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _serialize_entity(entity: ifcopenshell.entity_instance) -> dict:
    """Serialize an entity instance to a summary dict."""
    result = {
        "id": entity.id(),
        "type": entity.is_a(),
    }
    if hasattr(entity, "Name") and entity.Name:
        result["name"] = entity.Name
    return result
