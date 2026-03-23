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
import re
import typing
from pathlib import Path


def _api_package_path() -> Path:
    """Return the filesystem path to the ifcopenshell.api package."""
    import ifcopenshell.api

    return Path(ifcopenshell.api.__file__).parent


def list_modules() -> list[dict]:
    """List all API modules with their function counts and descriptions.

    Returns a list of dicts: [{"module": "root", "description": "...", "functions": [...], "count": 4}, ...]
    """
    api_path = _api_package_path()
    modules = []
    for child in sorted(api_path.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        init_file = child / "__init__.py"
        if not init_file.exists():
            continue
        try:
            mod = importlib.import_module(f"ifcopenshell.api.{child.name}")
        except Exception:
            continue
        all_names = getattr(mod, "__all__", [])
        if not all_names:
            continue
        description = ""
        if mod.__doc__:
            description = mod.__doc__.strip().split("\n")[0]
        modules.append(
            {
                "module": child.name,
                "description": description,
                "functions": list(all_names),
                "count": len(all_names),
            }
        )
    return modules


def list_functions(module: str) -> list[dict]:
    """List functions in an API module with one-line descriptions and parameter info.

    Returns a list of dicts: [{"name": "create_entity", "description": "...", "params": [...]}]
    """
    mod = importlib.import_module(f"ifcopenshell.api.{module}")
    all_names = getattr(mod, "__all__", [])
    functions = []
    for name in all_names:
        fn = _get_underlying_function(module, name)
        if fn is None:
            continue
        description = ""
        if fn.__doc__:
            description = fn.__doc__.strip().split("\n")[0]
        params = _extract_params(fn)
        functions.append(
            {
                "name": name,
                "description": description,
                "params": params,
            }
        )
    return functions


def function_docs(module: str, function: str) -> dict:
    """Full documentation for a single API function.

    Returns a dict with: module, function, description, params (with types/defaults/descriptions), return_type
    """
    fn = _get_underlying_function(module, function)
    if fn is None:
        raise ValueError(f"Function '{module}.{function}' not found")

    description = ""
    long_description = ""
    if fn.__doc__:
        description, long_description = _parse_docstring_body(fn.__doc__)

    params = _extract_params(fn)
    param_descriptions = _parse_param_docs(fn.__doc__ or "")
    for param in params:
        if param["name"] in param_descriptions:
            param["description"] = param_descriptions[param["name"]]

    return_type = _format_type_hint(typing.get_type_hints(fn).get("return"))
    return_description = _parse_return_doc(fn.__doc__ or "")

    result = {
        "module": module,
        "function": function,
        "description": description,
        "long_description": long_description,
        "params": params,
    }
    if return_type:
        result["return_type"] = return_type
    if return_description:
        result["return_description"] = return_description
    return result


def _get_underlying_function(module: str, function: str):
    """Get the actual function object (unwrapping the listener wrapper if needed)."""
    try:
        fn_module = importlib.import_module(f"ifcopenshell.api.{module}.{function}")
        fn = getattr(fn_module, function, None)
        return fn
    except (ImportError, AttributeError):
        return None


def _extract_params(fn) -> list[dict]:
    """Extract parameter info from a function's signature and type hints."""
    sig = inspect.signature(fn)
    try:
        hints = typing.get_type_hints(fn)
    except Exception:
        hints = {}

    params = []
    for name, param in sig.parameters.items():
        if name == "file" or name == "self":
            continue
        info = {"name": name}
        if name in hints:
            info["type"] = _format_type_hint(hints[name])
        if param.default is not inspect.Parameter.empty:
            info["default"] = _serialize_default(param.default)
        else:
            info["required"] = True
        params.append(info)
    return params


def _format_type_hint(hint) -> str | None:
    """Format a type hint to a readable string."""
    import ifcopenshell

    if hint is None:
        return None
    if hint is type(None):
        return "None"
    # ifcopenshell.file params are passed as a file path string
    if hint is ifcopenshell.file:
        return "file_path"
    origin = typing.get_origin(hint)
    args = typing.get_args(hint)

    # Union (including Optional)
    if origin is typing.Union:
        formatted = [_format_type_hint(a) for a in args]
        # Optional[X] is Union[X, None] — render as "Optional[X]"
        if len(formatted) == 2 and "None" in formatted:
            inner = next(f for f in formatted if f != "None")
            return f"Optional[{inner}]"
        return " | ".join(formatted)

    # Literal
    if origin is typing.Literal:
        values = ", ".join(repr(a) for a in args)
        return f"Literal[{values}]"

    # Generic types (list, dict, etc.)
    if origin is not None:
        origin_name = getattr(origin, "__name__", str(origin))
        if args:
            inner = ", ".join(_format_type_hint(a) for a in args)
            return f"{origin_name}[{inner}]"
        return origin_name

    # Simple types
    return getattr(hint, "__name__", str(hint))


def _serialize_default(value):
    """Serialize a default value to something JSON-friendly."""
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    return repr(value)


def _parse_docstring_body(docstring: str) -> tuple[str, str]:
    """Parse the summary and long description from a docstring."""
    lines = docstring.strip().split("\n")
    summary = lines[0].strip() if lines else ""
    body_lines = []
    in_body = False
    for line in lines[1:]:
        stripped = line.strip()
        if stripped.startswith(":param") or stripped.startswith(":return"):
            break
        if stripped.startswith("Example"):
            break
        if not in_body and not stripped:
            in_body = True
            continue
        if in_body:
            body_lines.append(stripped)

    long_description = " ".join(body_lines).strip()
    # collapse multiple spaces
    long_description = re.sub(r"\s+", " ", long_description)
    return summary, long_description


_FIELD_MARKER = re.compile(r":(?:param|returns?|rtype|type|raises?)\b")


def _parse_param_docs(docstring: str) -> dict[str, str]:
    """Extract :param name: description lines from a docstring."""
    params = {}
    current_param = None
    current_lines = []
    for line in docstring.split("\n"):
        stripped = line.strip()
        match = re.match(r":param\s+(\w+):\s*(.*)", stripped)
        if match:
            if current_param:
                params[current_param] = " ".join(current_lines).strip()
            current_param = match.group(1)
            current_lines = [match.group(2)]
        elif current_param and stripped and not _FIELD_MARKER.match(stripped):
            current_lines.append(stripped)
        elif _FIELD_MARKER.match(stripped) or (stripped == "" and current_param):
            if current_param:
                params[current_param] = " ".join(current_lines).strip()
                current_param = None
                current_lines = []
    if current_param:
        params[current_param] = " ".join(current_lines).strip()
    # collapse whitespace
    return {k: re.sub(r"\s+", " ", v) for k, v in params.items()}


def _parse_return_doc(docstring: str) -> str:
    """Extract :return: description from a docstring."""
    lines = []
    in_return = False
    for line in docstring.split("\n"):
        stripped = line.strip()
        match = re.match(r":return:\s*(.*)", stripped)
        if match:
            in_return = True
            lines = [match.group(1)]
        elif in_return:
            if _FIELD_MARKER.match(stripped) or stripped == "":
                break
            lines.append(stripped)
    return re.sub(r"\s+", " ", " ".join(lines).strip())
