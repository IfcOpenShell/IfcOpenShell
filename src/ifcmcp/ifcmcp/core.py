# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

import ifcopenshell

from ifcedit.discover import function_docs, list_functions, list_modules
from ifcedit.run import run_api
from ifcquery import clash as clash_mod
from ifcquery import info, relations, select, summary, tree


# inside ifcmcp/core.py
import json
from typing import Any

def _jsonify(x: Any) -> Any:
    """Convert IfcOpenShell objects / iterables into JSON-safe primitives."""
    if x is None or isinstance(x, (str, int, float, bool)):
        return x

    # IfcOpenShell entity instances: normalize
    if isinstance(x, ifcopenshell.entity_instance):
        return {
            "id": int(x.id()),
            "type": x.is_a(),
            "repr": str(x),
            "name": getattr(x, "Name", None),
        }

    if isinstance(x, dict):
        return {str(k): _jsonify(v) for k, v in x.items()}

    if isinstance(x, (list, tuple, set)):
        return [_jsonify(v) for v in x]

    # Try JSON as-is, else fallback to string
    try:
        json.dumps(x)
        return x
    except Exception:
        return str(x)

class IfcSessionError(RuntimeError):
    pass


@dataclass
class IfcSession:
    """In-memory IFC session (no FastMCP dependency).

    Designed to work in:
      - FastMCP server (single global session)
      - Embedded runtimes like Pyodide (one session per browser tab/worker)
    """

    model: ifcopenshell.file | None = None
    model_path: str | None = None

    # -----------------
    # Session lifecycle
    # -----------------
    def _require_model(self) -> ifcopenshell.file:
        if self.model is None:
            raise IfcSessionError("No model loaded. Call ifc_load() or ifc_new() first.")
        return self.model

    def ifc_new(self, schema: str = "IFC4") -> dict[str, Any]:
        """Create a new empty IFC model in memory."""
        self.model = ifcopenshell.file(schema=schema)
        self.model_path = None
        return {"ok": True, "schema": self.model.schema, "entities": sum(1 for _ in self.model)}

    def ifc_load(self, path: str) -> str:
        """Open an IFC file into memory. Returns confirmation string."""
        self.model = ifcopenshell.open(path)
        self.model_path = path
        count = sum(1 for _ in self.model)
        return f"Loaded {path}: schema {self.model.schema}, {count} entities"

    def ifc_save(self, path: str = "") -> str:
        """Write the in-memory model to disk. Empty path overwrites the original file."""
        model = self._require_model()
        target = path if path else self.model_path
        if not target:
            raise IfcSessionError("No path specified and no original path available.")
        model.write(target)
        return f"Saved to {target}"

    def ifc_reset(self) -> dict[str, Any]:
        """Drop the in-memory model."""
        self.model = None
        self.model_path = None
        return {"ok": True}

    # -------------
    # Query tools
    # -------------
    def ifc_summary(self) -> dict[str, Any]:
        """Model overview: schema, entity counts, project info."""
        return summary.summary(self._require_model())

    def ifc_tree(self) -> dict[str, Any] | list[dict[str, Any]]:
        """Full spatial hierarchy tree (Project -> Site -> Building -> Storeys -> Elements)."""
        return tree.tree(self._require_model())

    def ifc_info(self, element_id: int) -> dict[str, Any]:
        """Deep inspection of an entity by step ID (attributes, psets, placement, type, material)."""
        model = self._require_model()
        element = model.by_id(element_id)
        if element is None:
            raise IfcSessionError(f"Element #{element_id} not found.")
        return info.info(model, element)

    def ifc_select(self, query: str) -> list[dict[str, Any]]:
        """Filter elements using ifcopenshell selector syntax (e.g. 'IfcWall', 'IfcWindow')."""
        return select.select(self._require_model(), query)

    def ifc_relations(self, element_id: int, traverse: str = "") -> dict[str, Any] | list[dict[str, Any]]:
        """Show relationships for an element. Set traverse='up' to walk hierarchy to IfcProject."""
        model = self._require_model()
        element = model.by_id(element_id)
        if element is None:
            raise IfcSessionError(f"Element #{element_id} not found.")
        return relations.relations(model, element, traverse=traverse if traverse else None)

    def ifc_clash(
        self,
        element_id: int,
        clearance: float = 0.0,
        tolerance: float = 0.002,
        scope: str = "storey",
    ) -> dict[str, Any]:
        """Check element for geometric clashes. clearance=0.0 means no clearance check."""
        model = self._require_model()
        element = model.by_id(element_id)
        if element is None:
            raise IfcSessionError(f"Element #{element_id} not found.")
        return clash_mod.clash(
            model,
            element,
            clearance=clearance if clearance and clearance > 0.0 else None,
            tolerance=tolerance,
            scope=scope,
        )

    # ------------------------
    # Edit discovery + execute
    # ------------------------
    def ifc_list(self, module: str = "") -> list[dict]:
        """List all API modules, or functions within a module. Empty module = all modules."""
        return list_functions(module) if module else list_modules()

    def ifc_docs(self, function_path: str) -> dict:
        """Show full documentation for an API function. Input format: 'module.function'."""
        module, function = function_path.split(".", 1)
        return function_docs(module, function)

    def ifc_edit(self, function_path: str, params: Any = "{}") -> dict:
        """Execute an ifcopenshell.api mutation.

        params may be:
        - JSON string
        - dict (from tool calling / JS)
        - JsProxy (handled upstream in embedded.py)
        """
        model = self._require_model()
        module, function = function_path.split(".", 1)

        if isinstance(params, str):
            raw_kwargs = json.loads(params) if params.strip() else {}
        elif isinstance(params, dict):
            raw_kwargs = params
        else:
            # e.g. list/None/etc
            raw_kwargs = dict(params) if params is not None else {}

        res = run_api(model, module, function, raw_kwargs)
        return _jsonify(res)

    # ------------------------
    # Generic dispatcher + tool specs for LLMs
    # ------------------------
    def dispatch(self, name: str, args: dict[str, Any] | None = None) -> Any:
        args = args or {}
        fn = getattr(self, name, None)
        if not callable(fn):
            raise IfcSessionError(f"Unknown tool: {name}")
        return _jsonify(fn(**args))

    def openai_tools(self) -> list[dict[str, Any]]:
        """Tool schemas in the OpenAI 'Responses API' format (type=function)."""
        # Keep schemas tight so the model calls tools correctly.
        return [
            {
                "type": "function",
                "name": "ifc_new",
                "description": "Create a new empty IFC model in memory.",
                "parameters": {
                    "type": "object",
                    "properties": {"schema": {"type": "string", "description": "IFC schema, e.g. IFC4"}},
                    "required": [],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "ifc_summary",
                "description": "Get a concise overview of the loaded IFC model.",
                "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
            },
            {
                "type": "function",
                "name": "ifc_tree",
                "description": "Get the full spatial hierarchy tree.",
                "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
            },
            {
                "type": "function",
                "name": "ifc_select",
                "description": "Select elements using ifcopenshell selector syntax (e.g. 'IfcWall').",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "ifc_info",
                "description": "Inspect an entity by STEP id.",
                "parameters": {
                    "type": "object",
                    "properties": {"element_id": {"type": "integer"}},
                    "required": ["element_id"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "ifc_relations",
                "description": "Get relationships for an element. traverse='up' walks to IfcProject.",
                "parameters": {
                    "type": "object",
                    "properties": {"element_id": {"type": "integer"}, "traverse": {"type": "string"}},
                    "required": ["element_id"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "ifc_clash",
                "description": "Run clash/clearance checks for an element.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "element_id": {"type": "integer"},
                        "clearance": {"type": "number"},
                        "tolerance": {"type": "number"},
                        "scope": {"type": "string", "description": "storey or all"},
                    },
                    "required": ["element_id"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "ifc_list",
                "description": "List ifcopenshell.api modules or functions within a module.",
                "parameters": {
                    "type": "object",
                    "properties": {"module": {"type": "string"}},
                    "required": [],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "ifc_docs",
                "description": "Get documentation for an ifcopenshell.api function, 'module.function'.",
                "parameters": {
                    "type": "object",
                    "properties": {"function_path": {"type": "string"}},
                    "required": ["function_path"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "ifc_edit",
                "description": "Execute an ifcopenshell.api mutation; params is a JSON string of stringly-typed kwargs.",
                "parameters": {
                    "type": "object",
                    "properties": {"function_path": {"type": "string"}, "params": {"type": "string"}},
                    "required": ["function_path"],
                    "additionalProperties": False,
                },
            },
        ]