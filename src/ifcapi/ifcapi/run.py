# IfcApi - CLI wrapper for ifcopenshell.api mutation functions
# Copyright (C) 2025 Bruno Postle <bruno@postle.net>
#
# This file is part of IfcApi.
#
# IfcApi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcApi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcApi.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

import importlib
import inspect
import typing

import ifcopenshell

from ifcapi.coerce import coerce_value


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
    for name, value_str in raw_kwargs.items():
        if name not in sig.parameters:
            return {"ok": False, "error": f"Unknown parameter '{name}' for {module}.{function}"}
        hint = hints.get(name)
        try:
            coerced_kwargs[name] = coerce_value(value_str, hint, model)
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
