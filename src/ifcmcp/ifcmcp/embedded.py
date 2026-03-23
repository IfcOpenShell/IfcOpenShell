# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ifcmcp.core import IfcSession

session = IfcSession()

# Optional imports only available under Pyodide
try:
    from pyodide.ffi import JsProxy, to_py  # type: ignore
except Exception:  # pragma: no cover
    JsProxy = None  # type: ignore
    to_py = None  # type: ignore


def _coerce_args(args: Any) -> dict[str, Any]:
    """Convert JS objects / JsProxy / mappings into a real Python dict."""
    if args is None:
        return {}

    # Pyodide: JS object arrives as JsProxy; convert recursively to Python.
    if JsProxy is not None and isinstance(args, JsProxy):
        # dict_converter=dict ensures JS object -> Python dict (not Map)
        return to_py(args, dict_converter=dict)

    # Already a Python dict
    if isinstance(args, dict):
        return args

    # Any Mapping-like object
    if isinstance(args, Mapping):
        return dict(args)

    # Last resort: try dict() coercion
    try:
        return dict(args)
    except Exception as e:
        raise TypeError(f"Tool args must be a mapping/dict; got {type(args)}") from e


def tools_openai() -> list[dict[str, Any]]:
    return session.openai_tools()


def call_tool(name: str, args: Any = None) -> dict[str, Any]:
    """
    Non-throwing tool dispatcher.
    Always returns: {"ok": bool, "data": ...} or {"ok": false, "error": "...", "error_type": "...", ...}
    """
    try:
        py_args = _coerce_args(args)
        data = session.dispatch(name, py_args)
        return {"ok": True, "data": data}

    except Exception as e:
        # Keep it short; avoid full tracebacks in tool output unless debugging.
        return {"ok": False, "error_type": type(e).__name__, "error": str(e)}
