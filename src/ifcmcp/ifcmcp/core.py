# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

# inside ifcmcp/core.py
import json
from collections.abc import Callable
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


def _use_doc(source: Callable, extra: str = "") -> Callable:
    """Decorator: copy `source`'s docstring onto the decorated method.

    Keeps the query/edit logic in ``ifcquery``/``ifcedit`` as the single
    source of truth for what a delegating ``IfcSession`` method does, rather
    than maintaining a second prose description here. Only ``__doc__`` is
    copied — unlike `functools.wraps`, this leaves the method's own signature
    (and MCP tool schema derived from it) untouched.

    :param extra: Optional session-specific note appended after `source`'s
        docstring, for the handful of methods that translate an argument
        (e.g. a JSON/MCP-friendly default) before delegating.
    """

    def decorator(fn: Callable) -> Callable:
        fn.__doc__ = (source.__doc__ or "").rstrip() + extra
        return fn

    return decorator


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
        """Create a new empty IFC model in memory.

        Replaces the model currently held by the session, discarding any unsaved
        edits. The new model has no file path of its own, so ``ifc_save`` must be
        given an explicit path.

        :param schema: IFC schema version — ``IFC2X3``, ``IFC4``, ``IFC4X1``,
            ``IFC4X2`` or ``IFC4X3`` — passed straight to ``ifcopenshell.file()``
            (default ``IFC4``). ``IFC4X3_ADD2`` is also accepted and, like
            ``IFC4X3``, produces a model whose ``schema`` reports ``IFC4X3``.
        """
        self.model = ifcopenshell.file(schema=schema)
        self.model_path = None
        return {"ok": True, "schema": self.model.schema, "entities": sum(1 for _ in self.model)}

    def ifc_load(self, path: str) -> str:
        """Open an IFC file from disk into the session.

        Replaces the model currently held by the session, discarding any unsaved
        edits, and remembers the path so a later ``ifc_save`` can overwrite it.
        Call this before any query or edit method. Returns a confirmation string
        naming the schema version and entity count.

        :param path: Filesystem path of the IFC file to open.
        """
        self.model = ifcopenshell.open(path)
        self.model_path = path
        count = sum(1 for _ in self.model)
        return f"Loaded {path}: schema {self.model.schema}, {count} entities"

    def ifc_save(self, path: str = "") -> str:
        """Write the in-memory model to disk.

        Overwrites the target file without further confirmation. Edits made by
        ``ifc_edit``, ``ifc_shape`` and ``ifc_quantify`` exist only in memory
        until this is called.

        :param path: Destination path. Omit to overwrite the file the model was
            loaded from; this fails for a model created by ``ifc_new``, which has
            no original path.
        """
        model = self._require_model()
        target = path if path else self.model_path
        if not target:
            raise IfcSessionError("No path specified and no original path available.")
        model.write(target)
        return f"Saved to {target}"

    def ifc_reset(self) -> dict[str, Any]:
        """Discard the in-memory model.

        Drops the model and its file path, throwing away any edits not already
        written with ``ifc_save``. Succeeds even when no model is loaded.
        """
        self.model = None
        self.model_path = None
        return {"ok": True}

    # -------------
    # Query tools
    # -------------
    @_use_doc(summary.summary)
    def ifc_summary(self) -> dict[str, Any]:
        return summary.summary(self._require_model())

    @_use_doc(tree.tree)
    def ifc_tree(self) -> dict[str, Any] | list[dict[str, Any]]:
        return tree.tree(self._require_model())

    @_use_doc(info.info)
    def ifc_info(self, element_id: int) -> dict[str, Any]:
        model = self._require_model()
        element = model.by_id(element_id)
        if element is None:
            raise IfcSessionError(f"Element #{element_id} not found.")
        return info.info(model, element)

    @_use_doc(select.select)
    def ifc_select(self, query: str) -> list[dict[str, Any]]:
        return select.select(self._require_model(), query)

    @_use_doc(relations.relations)
    def ifc_relations(self, element_id: int, traverse: str = "") -> dict[str, Any] | list[dict[str, Any]]:
        model = self._require_model()
        element = model.by_id(element_id)
        if element is None:
            raise IfcSessionError(f"Element #{element_id} not found.")
        return relations.relations(model, element, traverse=traverse if traverse else None)

    @_use_doc(
        clash_mod.clash,
        extra=(
            "\n\nNote: this method takes a plain ``clearance: float`` rather than\n"
            '``clearance: float | None`` — ``0.0`` (the default) means "skip the\n'
            'clearance check", matching ``None`` in ``ifcquery.clash.clash()``.'
        ),
    )
    def ifc_clash(
        self,
        element_id: int,
        clearance: float = 0.0,
        tolerance: float = 0.002,
        scope: str = "storey",
    ) -> dict[str, Any]:
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

    @_use_doc(contexts_mod.contexts)
    def ifc_contexts(self) -> list[dict[str, Any]]:
        return contexts_mod.contexts(self._require_model())

    @_use_doc(materials_mod.materials)
    def ifc_materials(self) -> list[dict[str, Any]]:
        return materials_mod.materials(self._require_model())

    # ------------------------
    # Edit discovery + execute
    # ------------------------
    def ifc_list(self, module: str = "") -> list[dict]:
        """Discover the ifcopenshell.api functions available for editing.

        With no argument returns every API module with its description,
        function names and function count. With a module name returns that
        module's functions, each with a one-line description and its
        parameters. This is the starting point for ``ifc_docs`` and
        ``ifc_edit``; it inspects the installed ifcopenshell package and works
        without a model loaded.

        :param module: API module name, for example ``'root'``, ``'geometry'``
            or ``'pset'``. Omit to list all modules.
        """
        return list_functions(module) if module else list_modules()

    @_use_doc(function_docs)
    def ifc_docs(self, function_path: str) -> dict:
        module, function = function_path.split(".", 1)
        return function_docs(module, function)

    def ifc_edit(self, function_path: str, params: Any = "{}") -> dict:
        """Run an ifcopenshell.api function to modify the model.

        This is the general-purpose edit method; use ``ifc_list`` and
        ``ifc_docs`` first to find the function and its parameters. Changes
        are made to the in-memory model only, so ``ifc_save`` is needed to
        persist them. Returns ``{"ok": True, "result": ...}``, or
        ``{"ok": False, "error": ...}`` when the function is unknown, a
        parameter cannot be converted, or the call raises.

        :param function_path: ``'module.function'``, for example
            ``'root.create_entity'``.
        :param params: Keyword arguments as a JSON string, a dict (tool
            calling) or a JsProxy (handled upstream in embedded.py). Pass
            entity references as integer step IDs, and arguments typed as an
            IFC file as a file path string.
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
    @_use_doc(validate_mod.validate)
    def ifc_validate(self, express_rules: bool = False) -> dict[str, Any]:
        return validate_mod.validate(self._require_model(), express_rules=express_rules)

    @_use_doc(schedule.schedule)
    def ifc_schedule(self, max_depth: int | None = None) -> list[dict[str, Any]]:
        return schedule.schedule(self._require_model(), max_depth=max_depth)

    @_use_doc(cost_mod.cost)
    def ifc_cost(self, max_depth: int | None = None) -> list[dict[str, Any]]:
        return cost_mod.cost(self._require_model(), max_depth=max_depth)

    @_use_doc(schema.schema)
    def ifc_schema(self, entity_type: str) -> dict[str, Any]:
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
        """List the ShapeBuilder methods available for constructing geometry.

        Returns every public ``ifcopenshell.util.shape_builder.ShapeBuilder``
        method with a one-line description and its parameter names, read
        directly from that class's own docstrings. Use it to find a method,
        then ``ifc_shape_docs`` for the details and ``ifc_shape`` to call it.
        Works without a model loaded.
        """
        return _list_shape_methods()

    def ifc_shape_docs(self, method: str) -> dict:
        """Show the full documentation for one ShapeBuilder method.

        Returns the summary and long description, every parameter with its
        type and default, and the return type — read directly from
        ``ShapeBuilder``'s own docstring. Read this before ``ifc_shape`` so
        that argument names and value shapes are correct. Works without a
        model loaded.

        :param method: ShapeBuilder method name, for example ``'polyline'``,
            ``'rectangle'`` or ``'extrude'``.
        """
        return _shape_method_docs(method)

    def ifc_shape(self, method: str, params: Any = "{}") -> dict:
        """Call a ShapeBuilder method to build geometry in the model.

        The created entities are added to the in-memory model, so
        ``ifc_save`` is needed to persist them. On success the result
        identifies the created entity by step ID and type; an unknown method
        or a failed call is reported as an error instead.

        :param method: ShapeBuilder method name, as listed by
            ``ifc_shape_list``.
        :param params: JSON string of keyword arguments. Pass entity
            references as integer step IDs and vectors as JSON arrays, e.g.
            ``[1.0, 0.0, 0.0]``.
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

    @_use_doc(run_quantify, extra="\n\nCall ``ifc_save`` afterwards to persist the result.")
    def ifc_quantify(self, rule: str, selector: str = "") -> dict[str, Any]:
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
