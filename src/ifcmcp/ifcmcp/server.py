from __future__ import annotations

import json
from typing import Any

import ifcopenshell
from ifcedit.discover import function_docs, list_functions, list_modules
from ifcedit.run import run_api
from ifcquery import clash as clash_mod
from ifcquery import info, relations, select, summary, tree
from mcp.server.fastmcp import FastMCP

server = FastMCP(
    name="ifc-mcp",
    instructions="MCP server for querying and editing IFC building models. "
    "Load a file first with ifc_load, then use query/edit tools. "
    "Save changes with ifc_save.",
)

_model: ifcopenshell.file | None = None
_model_path: str | None = None


def _require_model() -> ifcopenshell.file:
    if _model is None:
        raise ValueError("No model loaded. Call ifc_load first.")
    return _model


# -- Session tools --


@server.tool()
def ifc_load(path: str) -> str:
    """Open an IFC file into memory. Returns confirmation with schema and entity count."""
    global _model, _model_path
    _model = ifcopenshell.open(path)
    _model_path = path
    count = sum(1 for _ in _model)
    return f"Loaded {path}: schema {_model.schema}, {count} entities"


@server.tool()
def ifc_save(path: str = "") -> str:
    """Write the in-memory model to disk. Empty path overwrites the original file."""
    model = _require_model()
    target = path if path else _model_path
    if not target:
        raise ValueError("No path specified and no original path available.")
    model.write(target)
    return f"Saved to {target}"


# -- Query tools --


@server.tool()
def ifc_summary() -> dict[str, Any]:
    """Model overview: schema, entity counts, project info."""
    return summary.summary(_require_model())


@server.tool()
def ifc_tree() -> dict[str, Any] | list[dict[str, Any]]:
    """Full spatial hierarchy tree (Project -> Site -> Building -> Storeys -> Elements)."""
    return tree.tree(_require_model())


@server.tool()
def ifc_info(element_id: int) -> dict[str, Any]:
    """Deep inspection of an entity by step ID (attributes, psets, placement, type, material)."""
    model = _require_model()
    element = model.by_id(element_id)
    return info.info(model, element)


@server.tool()
def ifc_select(query: str) -> list[dict[str, Any]]:
    """Filter elements using ifcopenshell selector syntax (e.g. 'IfcWall', 'IfcWindow')."""
    return select.select(_require_model(), query)


@server.tool()
def ifc_relations(element_id: int, traverse: str = "") -> dict[str, Any] | list[dict[str, Any]]:
    """Show relationships for an element. Set traverse='up' to walk hierarchy to IfcProject."""
    model = _require_model()
    element = model.by_id(element_id)
    return relations.relations(model, element, traverse=traverse if traverse else None)


@server.tool()
def ifc_clash(
    element_id: int,
    clearance: float = 0.0,
    tolerance: float = 0.002,
    scope: str = "storey",
) -> dict[str, Any]:
    """Check element for geometric clashes. clearance=0.0 means no clearance check."""
    model = _require_model()
    element = model.by_id(element_id)
    return clash_mod.clash(
        model,
        element,
        clearance=clearance if clearance > 0.0 else None,
        tolerance=tolerance,
        scope=scope,
    )


# -- Edit discovery tools --


@server.tool()
def ifc_list(module: str = "") -> list[dict]:
    """List all API modules, or functions within a module. Empty module = all modules."""
    if module:
        return list_functions(module)
    return list_modules()


@server.tool()
def ifc_docs(function_path: str) -> dict:
    """Show full documentation for an API function. Input format: 'module.function'."""
    module, function = function_path.split(".", 1)
    return function_docs(module, function)


# -- Edit execution tool --


@server.tool()
def ifc_edit(function_path: str, params: str = "{}") -> dict:
    """Execute an ifcopenshell.api mutation. params is a JSON string of {"param": "value"} pairs.

    Values are strings coerced by ifcedit's type system (entity IDs as "123",
    dicts as JSON strings, etc). Does NOT auto-save; call ifc_save() after edits.
    """
    model = _require_model()
    module, function = function_path.split(".", 1)
    raw_kwargs = json.loads(params)
    return run_api(model, module, function, raw_kwargs)
