# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

# inside ifcmcp/core.py
import json
from collections.abc import Callable  # noqa: F401 — Callable used in helpers below
from dataclasses import dataclass
from typing import Any

import ifcopenshell
from ifcedit.discover import function_docs, list_functions, list_modules
from ifcedit.quantify import run_quantify
from ifcedit.run import run_api
from ifcquery import clash as clash_mod
from ifcquery import contexts as contexts_mod
from ifcquery import cost as cost_mod
from ifcquery import (
    info,
    relations,
    schedule,
    schema,
    select,
    summary,
    tree,
)
from ifcquery import (
    materials as materials_mod,
)
from ifcquery import (
    plot as plot_mod,
)
from ifcquery import (
    render as render_mod,
)
from ifcquery import validate as validate_mod


def _jsonify(x: Any) -> Any:
    """Convert IfcOpenShell objects / iterables into JSON-safe primitives."""
    if x is None or isinstance(x, (str, int, float, bool)):
        return x

    # numpy arrays (and any array-like with tolist)
    if hasattr(x, "tolist"):
        return x.tolist()

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


# ---------------------------------------------------------------------------
# Shape builder helpers
# ---------------------------------------------------------------------------


def _list_shape_methods() -> list[dict]:
    """Introspect ShapeBuilder and return a summary of all public methods."""
    import inspect

    from ifcedit.discover import _extract_params
    from ifcopenshell.util.shape_builder import ShapeBuilder

    results = []
    for name, fn in inspect.getmembers(ShapeBuilder, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        doc = fn.__doc__ or ""
        description = doc.strip().split("\n")[0] if doc.strip() else ""
        results.append({"method": name, "description": description, "params": _extract_params(fn)})
    return results


def _shape_method_docs(method_name: str) -> dict:
    """Return full documentation for a single ShapeBuilder method."""
    import typing

    from ifcedit.discover import (
        _extract_params,
        _format_type_hint,
        _parse_docstring_body,
        _parse_param_docs,
        _parse_return_doc,
    )
    from ifcopenshell.util.shape_builder import ShapeBuilder

    if method_name.startswith("_"):
        raise ValueError(f"ShapeBuilder has no method '{method_name}'")
    fn = getattr(ShapeBuilder, method_name, None)
    if fn is None:
        raise ValueError(f"ShapeBuilder has no method '{method_name}'")

    doc = fn.__doc__ or ""
    description, long_description = _parse_docstring_body(doc)
    params = _extract_params(fn)
    for param in params:
        param_desc = _parse_param_docs(doc)
        if param["name"] in param_desc:
            param["description"] = param_desc[param["name"]]

    try:
        hints = typing.get_type_hints(fn)
    except Exception:
        hints = {}

    result: dict[str, Any] = {
        "method": method_name,
        "description": description,
        "long_description": long_description,
        "params": params,
    }
    return_type = _format_type_hint(hints.get("return"))
    if return_type:
        result["return_type"] = return_type
    return_description = _parse_return_doc(doc)
    if return_description:
        result["return_description"] = return_description
    return result


def _coerce_shape_params(fn: Callable, raw_kwargs: dict, model: ifcopenshell.file) -> dict:
    """Coerce JSON-parsed kwargs to proper Python types for a ShapeBuilder method."""
    import inspect
    import typing

    sig = inspect.signature(fn)
    try:
        hints = typing.get_type_hints(fn)
    except Exception:
        hints = {}

    return {
        key: _coerce_shape_value(value, hints.get(key), model)
        for key, value in raw_kwargs.items()
        if key in sig.parameters and key != "self"
    }


def _coerce_shape_value(value: Any, hint: Any, model: ifcopenshell.file) -> Any:
    """Convert a single JSON-parsed value to the correct Python type."""
    import typing

    if hint is None or value is None:
        return value

    origin = typing.get_origin(hint)
    args = typing.get_args(hint)

    # Optional[X] / Union — try each non-None branch in order
    if origin is typing.Union:
        if value is None:
            return None
        for t in (a for a in args if a is not type(None)):
            try:
                return _coerce_shape_value(value, t, model)
            except (ValueError, TypeError):
                continue
        return value

    # entity_instance: resolve integer or "#N" string step ID
    if hint is ifcopenshell.entity_instance or (
        isinstance(hint, type) and issubclass(hint, ifcopenshell.entity_instance)
    ):
        entity_id = int(str(value).lstrip("#"))
        entity = model.by_id(entity_id)
        if entity is None:
            raise ValueError(f"Entity #{entity_id} not found in model")
        return entity

    # Sequence[entity_instance]: resolve each element in the list
    import collections.abc

    if origin is not None and issubclass(origin, collections.abc.Sequence) and not isinstance(value, str):
        if args and (
            args[0] is ifcopenshell.entity_instance
            or (isinstance(args[0], type) and issubclass(args[0], ifcopenshell.entity_instance))
        ):
            if isinstance(value, (list, tuple)):
                return [_coerce_shape_value(v, args[0], model) for v in value]

    # bool: JSON gives actual bools; also accept string representations
    if hint is bool:
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "1", "yes")

    # Everything else (float, int, VectorType lists, dicts, Literals) passes through
    return value


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
        """Filter elements using ifcopenshell selector syntax.

        Examples: ``IfcWall``, ``IfcWall, IfcColumn``, ``! IfcWall``,
        ``IfcWall, Name = "My Wall"``, ``type = "Concrete Wall"``,
        ``material = "Concrete"``.
        """
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

    def ifc_contexts(self) -> list[dict[str, Any]]:
        """List all geometric representation contexts and subcontexts with their step IDs."""
        return contexts_mod.contexts(self._require_model())

    def ifc_materials(self) -> list[dict[str, Any]]:
        """List all materials and material sets (layers, constituents, profiles)."""
        return materials_mod.materials(self._require_model())

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
    # Extended query + edit tools
    # ------------------------
    def ifc_validate(self, express_rules: bool = False) -> dict[str, Any]:
        """Validate the loaded model. Returns {'valid': bool, 'issues': [...]}."""
        return validate_mod.validate(self._require_model(), express_rules=express_rules)

    def ifc_schedule(self, max_depth: int | None = None) -> list[dict[str, Any]]:
        """List work schedules and nested tasks from the model.

        max_depth limits subtask expansion (None = unlimited). At the cutoff,
        subtasks is replaced with {"truncated": True, "count": N}.
        """
        return schedule.schedule(self._require_model(), max_depth=max_depth)

    def ifc_cost(self, max_depth: int | None = None) -> list[dict[str, Any]]:
        """List cost schedules and nested cost items from the model.

        max_depth limits cost item expansion (None = unlimited). At the cutoff,
        subitems is replaced with {"truncated": True, "count": N}.
        """
        return cost_mod.cost(self._require_model(), max_depth=max_depth)

    def ifc_schema(self, entity_type: str) -> dict[str, Any]:
        """Return IFC class documentation for entity_type using the model's schema version."""
        return schema.schema(self._require_model(), entity_type)

    def ifc_plot(
        self,
        selector: str = "",
        element_ids: list[int] | None = None,
        view: str = "floorplan",
        width_mm: float = 297.0,
        height_mm: float = 420.0,
        scale: float = 1.0 / 100.0,
        png_width: int = 1024,
        png_height: int = 1024,
        output_format: str = "png",
    ) -> bytes:
        """Generate a 2D technical drawing (floor plan, elevation, or section) and return image bytes.

        Uses ifcopenshell.draw to produce SVG output which is rasterised to PNG via CairoSVG
        when output_format is 'png'.

        :param selector: ifcopenshell selector to restrict plotted elements
            (e.g. ``'IfcWall'``). Omit to plot the whole model.
        :param element_ids: Step IDs of elements to highlight. Other elements
            are faded to 10% opacity so the subject stands out.
        :param view: Drawing view — ``floorplan`` (default), ``elevation``,
            ``section``, or ``auto``.
        :param width_mm: Paper width in mm (default 297 = A4).
        :param height_mm: Paper height in mm (default 420 = A4).
        :param scale: Model-to-paper scale ratio (default 0.01 = 1:100).
        :param png_width: Raster output width in pixels (default 1024).
        :param png_height: Raster output height in pixels (default 1024).
        :param output_format: ``'svg'`` or ``'png'`` (default ``'png'``).
        :return: SVG or PNG bytes depending on output_format.
        """
        model = self._require_model()
        return plot_mod.plot(
            model,
            output_format=output_format,
            selector=selector if selector else None,
            element_ids=element_ids,
            view=view,
            width_mm=width_mm,
            height_mm=height_mm,
            scale=scale,
            png_width=png_width,
            png_height=png_height,
        )

    def ifc_render(
        self,
        selector: str = "",
        element_ids: list[int] | None = None,
        view: str = "iso",
    ) -> bytes:
        """Render the loaded model to a PNG image and return raw bytes.

        :param selector: ifcopenshell selector to restrict rendered elements
            (e.g. ``'IfcWall'``). Omit to render the whole model.
        :param element_ids: Step IDs of elements to highlight. Other elements
            are rendered in translucent grey.
        :param view: Camera angle: ``iso``, ``top``, ``south``, ``north``,
            ``east``, or ``west``.
        :return: PNG image as raw bytes.
        """
        model = self._require_model()
        return render_mod.render(
            model,
            selector=selector if selector else None,
            element_ids=element_ids,
            view=view,
        )

    # ------------------------
    # Shape builder tools
    # ------------------------
    def ifc_shape_list(self) -> list[dict]:
        """List all ShapeBuilder geometry methods with one-line descriptions and parameter names."""
        return _list_shape_methods()

    def ifc_shape_docs(self, method: str) -> dict:
        """Full documentation for a ShapeBuilder method: params, types, return value."""
        return _shape_method_docs(method)

    def ifc_shape(self, method: str, params: Any = "{}") -> dict:
        """Call a ShapeBuilder method by name. Returns the created entity's step ID.

        params is a JSON string of keyword arguments. Pass entity references as integer
        step IDs; vectors as JSON arrays (e.g. [1.0, 0.0, 0.0]).
        """
        model = self._require_model()

        from ifcopenshell.util.shape_builder import ShapeBuilder

        if method.startswith("_"):
            raise IfcSessionError(f"Private method '{method}' is not accessible")
        fn = getattr(ShapeBuilder, method, None)
        if fn is None:
            return {"ok": False, "error": f"ShapeBuilder has no method '{method}'"}

        if isinstance(params, str):
            raw_kwargs = json.loads(params) if params.strip() else {}
        elif isinstance(params, dict):
            raw_kwargs = params
        else:
            raw_kwargs = {}

        try:
            coerced = _coerce_shape_params(fn, raw_kwargs, model)
            result = fn(ShapeBuilder(model), **coerced)
            return {"ok": True, "result": _jsonify(result)}
        except Exception as e:
            return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    def ifc_quantify(self, rule: str, selector: str = "") -> dict[str, Any]:
        """Run quantity take-off on the model using the named rule.

        Modifies the model in-place; call ifc_save() after.
        """
        model = self._require_model()
        return run_quantify(model, rule, selector=selector if selector else None)

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
                "description": (
                    "Select elements using ifcopenshell selector syntax. "
                    "Examples: 'IfcWall', 'IfcWall, IfcColumn', '! IfcWall', "
                    "'IfcWall, Name = \"My Wall\"', 'type = \"Concrete Wall\"', "
                    "'material = \"Concrete\"'."
                ),
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
                "name": "ifc_contexts",
                "description": "List all geometric representation contexts and subcontexts with their step IDs, context type, identifier, and target view. Use this to find the context ID required for geometry-creation API calls.",
                "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
            },
            {
                "type": "function",
                "name": "ifc_materials",
                "description": "List all materials and material sets (IfcMaterial, IfcMaterialLayerSet, IfcMaterialConstituentSet, IfcMaterialProfileSet) with their layers, constituents, or profiles.",
                "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
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
            {
                "type": "function",
                "name": "ifc_validate",
                "description": "Validate the loaded model. Returns valid bool and list of issues.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "express_rules": {"type": "boolean", "description": "Also check EXPRESS rules (slower)"}
                    },
                    "required": [],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "ifc_schedule",
                "description": "List work schedules and nested tasks. Use max_depth=1 for top-level phases only on large projects.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_depth": {
                            "type": "integer",
                            "description": "Max levels of subtask expansion (omit for unlimited)",
                        }
                    },
                    "required": [],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "ifc_cost",
                "description": "List cost schedules and nested cost items. Use max_depth=1 for top-level sections only on large BoQs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_depth": {
                            "type": "integer",
                            "description": "Max levels of cost item expansion (omit for unlimited)",
                        }
                    },
                    "required": [],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "ifc_schema",
                "description": "Return IFC class documentation for an entity type.",
                "parameters": {
                    "type": "object",
                    "properties": {"entity_type": {"type": "string", "description": "IFC entity type, e.g. IfcWall"}},
                    "required": ["entity_type"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "ifc_quantify",
                "description": "Run quantity take-off (QTO) on the model. Modifies model in-place; call ifc_save() after.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rule": {"type": "string", "description": "QTO rule name, e.g. IFC4QtoBaseQuantities"},
                        "selector": {
                            "type": "string",
                            "description": "ifcopenshell selector to restrict elements (default: all IfcElement and IfcSpace)",
                        },
                    },
                    "required": ["rule"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "ifc_render",
                "description": (
                    "Render the loaded IFC model to a PNG image for visual inspection. "
                    "Use selector to restrict which elements are rendered (e.g. a single storey). "
                    "Use element_ids to highlight elements against a greyed-out background. "
                    "Returns base64-encoded PNG bytes."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "description": "ifcopenshell selector (default: whole model)"},
                        "element_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Step IDs of elements to highlight",
                        },
                        "view": {
                            "type": "string",
                            "enum": ["iso", "top", "south", "north", "east", "west"],
                            "description": "Camera angle (default: iso)",
                        },
                    },
                    "required": [],
                    "additionalProperties": False,
                },
            },
        ]
