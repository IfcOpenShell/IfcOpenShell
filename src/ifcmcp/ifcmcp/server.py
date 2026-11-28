# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

import base64
import functools
import inspect
from typing import Any

from ifcmcp.core import IfcSession
from ifcmcp.instructions import BONSAI_INSTRUCTIONS, EXECUTE_INSTRUCTIONS, INSTRUCTIONS

try:
    from mcp.server.mcpserver import MCPServer  # type: ignore
    from mcp.server.mcpserver.exceptions import ToolError  # type: ignore
except ImportError:
    # mcp 1.x, which Linux distributions still ship, has the same API under its old name.
    try:
        from mcp.server.fastmcp import FastMCP as MCPServer  # type: ignore
        from mcp.server.fastmcp.exceptions import ToolError  # type: ignore
    except ImportError:  # pragma: no cover
        MCPServer = None  # type: ignore
        ToolError = None  # type: ignore
try:
    from mcp.types import ImageContent, ToolAnnotations  # type: ignore
except ImportError:  # pragma: no cover
    ImageContent = None  # type: ignore
    ToolAnnotations = None  # type: ignore

# Tools that change neither the model nor any file, so a client may run them
# without asking. Every other tool can discard unsaved edits, change the model
# or overwrite a file, and is marked destructive.
READ_ONLY_TOOLS = frozenset(
    {
        "ifc_summary",
        "ifc_tree",
        "ifc_info",
        "ifc_select",
        "ifc_relations",
        "ifc_clash",
        "ifc_contexts",
        "ifc_materials",
        "ifc_list",
        "ifc_docs",
        "ifc_search",
        "ifc_validate",
        "ifc_schedule",
        "ifc_cost",
        "ifc_structural",
        "ifc_schema",
        "ifc_shape_list",
        "ifc_shape_docs",
    }
)

# Tools offered for the model open in Bonsai. Bonsai runs each edit as one of
# its own undo steps, and ifc_undo and ifc_redo step through Bonsai's history.
BONSAI_TOOLS = READ_ONLY_TOOLS | {"ifc_edit", "ifc_shape", "ifc_quantify", "ifc_undo", "ifc_redo"}
# Tools that only Bonsai offers, on its selection and 3D viewport rather than the model.
BONSAI_VIEW_TOOLS = frozenset({"bonsai_selection", "bonsai_select", "bonsai_view", "bonsai_screenshot"})

# Descriptions for tools that behave differently on the model open in Bonsai.
BONSAI_DESCRIPTIONS = {
    "ifc_undo": """Undo the last change made by ``ifc_edit``, ``ifc_shape`` or ``ifc_quantify``.

Each of those calls is one step in Bonsai's undo history, which it shares
with the user's own changes. Fails, changing nothing, when the last step in
Bonsai is not one of these calls, so the user's work is never undone.
Returns how many of these steps can still be undone and redone in a row.""",
    "ifc_redo": """Redo the last change undone by ``ifc_undo``.

Any new change in Bonsai after an undo, made through these tools or by the
user, discards what could be redone. Fails, changing nothing, when the next
step in Bonsai's undo history is not one of these calls. Returns how many of
these steps can still be undone and redone in a row.""",
}


def _annotations(name: str) -> Any:
    # camelCase arguments, because mcp 1.x accepts no other spelling.
    if name in READ_ONLY_TOOLS or name in ("bonsai_selection", "bonsai_screenshot"):
        return ToolAnnotations(readOnlyHint=True, openWorldHint=False)
    if name in BONSAI_VIEW_TOOLS:
        # They change the selection or the view, but never the model.
        return ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False)
    return ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=False)


def build_server(allow_execute: bool = False, bonsai_port: int | None = None) -> Any:
    """Create the MCP server if the dependency is available.

    :param allow_execute: Offer ``ifc_execute``, which runs arbitrary Python
        sent by the client.
    :param bonsai_port: Work on the model open in Bonsai, through the MCP
        bridge listening on this port, instead of a model held here. Only
        ``BONSAI_TOOLS`` are offered, and never ``ifc_execute``.
    """
    if MCPServer is None:
        raise ImportError(
            "The mcp package is not installed. Install with: pip install ifcmcp[mcp] (or add 'mcp' to your environment)."
        )

    if bonsai_port is None:
        session = IfcSession(allow_execute=allow_execute)
        instructions = INSTRUCTIONS + (EXECUTE_INSTRUCTIONS if allow_execute else "")
    else:
        from ifcmcp.bonsai import BonsaiSession

        session = BonsaiSession(port=bonsai_port)
        instructions = BONSAI_INSTRUCTIONS

    def _keep_reason(fn):
        """Raise a tool's failure as ToolError so its reason reaches the agent.

        MCPServer passes on a ToolError's text but replaces any other exception
        with a bare "Error executing tool <name>", which leaves the agent nothing
        to correct. Every tool, however it is registered, goes through this.
        """

        @functools.wraps(fn)
        def call(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except ToolError:
                raise
            except Exception as e:
                raise ToolError(str(e) or type(e).__name__) from e

        return call

    def _tool(fn):
        """Register a tool, taking its MCP description from the identically-named
        IfcSession method rather than duplicating it here. Bonsai is offered
        only BONSAI_TOOLS, with BONSAI_DESCRIPTIONS where they differ."""
        description = inspect.getdoc(getattr(IfcSession, fn.__name__))
        if bonsai_port is not None:
            if fn.__name__ not in BONSAI_TOOLS:
                return fn
            description = BONSAI_DESCRIPTIONS.get(fn.__name__, description)
        return server.tool(
            description=description,
            annotations=_annotations(fn.__name__),
        )(_keep_reason(fn))

    server = MCPServer(
        name="ifc-mcp",
        instructions=instructions,
    )

    # ---- Lifecycle ----
    @_tool
    def ifc_new(schema: str = "IFC4") -> dict[str, Any]:
        return session.ifc_new(schema=schema)

    @_tool
    def ifc_load(path: str) -> str:
        return session.ifc_load(path)

    @_tool
    def ifc_save(path: str = "") -> str:
        return session.ifc_save(path)

    @_tool
    def ifc_reset() -> dict[str, Any]:
        return session.ifc_reset()

    @_tool
    def ifc_undo() -> dict[str, Any]:
        return session.ifc_undo()

    @_tool
    def ifc_redo() -> dict[str, Any]:
        return session.ifc_redo()

    # ---- Query ----
    @_tool
    def ifc_summary() -> dict[str, Any]:
        return session.ifc_summary()

    @_tool
    def ifc_tree(max_depth: int | None = None) -> dict[str, Any] | list[dict[str, Any]]:
        return session.ifc_tree(max_depth=max_depth)

    @_tool
    def ifc_info(element_id: int | str) -> dict[str, Any]:
        return session.ifc_info(element_id)

    @_tool
    def ifc_select(query: str, limit: int = 200, offset: int = 0) -> dict[str, Any]:
        return session.ifc_select(query, limit=limit, offset=offset)

    @_tool
    def ifc_relations(element_id: int | str, traverse: str = "") -> dict[str, Any] | list[dict[str, Any]]:
        return session.ifc_relations(element_id, traverse=traverse)

    @_tool
    def ifc_clash(
        element_id: int | str,
        clearance: float = 0.0,
        tolerance: float = 0.002,
        scope: str = "storey",
    ) -> dict[str, Any]:
        return session.ifc_clash(
            element_id=element_id,
            clearance=clearance,
            tolerance=tolerance,
            scope=scope,
        )

    @_tool
    def ifc_contexts() -> list[dict[str, Any]]:
        return session.ifc_contexts()

    @_tool
    def ifc_materials() -> list[dict[str, Any]]:
        return session.ifc_materials()

    # ---- Edit ----
    @_tool
    def ifc_list(module: str = "") -> list[dict]:
        return session.ifc_list(module=module)

    @_tool
    def ifc_search(query: str, limit: int = 20) -> list[dict]:
        return session.ifc_search(query=query, limit=limit)

    @_tool
    def ifc_docs(function_path: str) -> dict:
        return session.ifc_docs(function_path=function_path)

    @_tool
    def ifc_edit(function_path: str, params: str = "{}") -> dict:
        return session.ifc_edit(function_path=function_path, params=params)

    # ---- Extended query + edit ----
    @_tool
    def ifc_validate(express_rules: bool = False) -> dict[str, Any]:
        return session.ifc_validate(express_rules=express_rules)

    @_tool
    def ifc_schedule(max_depth: int | None = None) -> list[dict[str, Any]]:
        return session.ifc_schedule(max_depth=max_depth)

    @_tool
    def ifc_cost(max_depth: int | None = None) -> list[dict[str, Any]]:
        return session.ifc_cost(max_depth=max_depth)

    @_tool
    def ifc_structural(max_depth: int | None = None) -> list[dict[str, Any]]:
        return session.ifc_structural(max_depth=max_depth)

    @_tool
    def ifc_schema(entity_type: str) -> dict[str, Any]:
        return session.ifc_schema(entity_type=entity_type)

    @_tool
    def ifc_quantify(rule: str, selector: str = "") -> dict[str, Any]:
        return session.ifc_quantify(rule=rule, selector=selector)

    if allow_execute and bonsai_port is None:

        @_tool
        def ifc_execute(code: str) -> dict[str, Any]:
            return session.ifc_execute(code=code)

    # ---- Shape builder ----
    @_tool
    def ifc_shape_list() -> list[dict]:
        return session.ifc_shape_list()

    @_tool
    def ifc_shape_docs(method: str) -> dict:
        return session.ifc_shape_docs(method=method)

    @_tool
    def ifc_shape(method: str, params: str = "{}") -> dict:
        return session.ifc_shape(method=method, params=params)

    @server.tool(structured_output=False, annotations=_annotations("ifc_plot"))
    @_keep_reason
    def ifc_plot(
        selector: str = "",
        element_ids: list[int] | None = None,
        view: str = "floorplan",
        width_mm: float = 297.0,
        height_mm: float = 420.0,
        scale: float = 1.0 / 100.0,
        png_width: int = 1024,
        png_height: int = 1024,
        output_path: str = "",
    ) -> list[ImageContent]:
        """Generate a 2D technical drawing of the loaded IFC model.

        Returns an inline PNG image (floor plan, elevation, or section) that the
        LLM can inspect to understand the 2D layout of the model.  If
        ``output_path`` is provided the drawing is also saved to disk — as SVG
        when the path ends in ``.svg``, otherwise as PNG.

        :param selector: ifcopenshell selector to restrict plotted elements
            (e.g. ``'IfcWall'``). Omit to plot the whole model.
        :param element_ids: Step IDs of elements to highlight. Other elements
            are faded so the subject stands out.
        :param view: Drawing view — ``floorplan`` (default), ``elevation``,
            ``section``, or ``auto``.
        :param width_mm: Paper width in mm (default 297 = A4 landscape width).
        :param height_mm: Paper height in mm (default 420 = A4 landscape height).
        :param scale: Model-to-paper scale ratio (default 0.01 = 1:100).
        :param png_width: Raster output width in pixels (default 1024).
        :param png_height: Raster output height in pixels (default 1024).
        :param output_path: Optional file path to save the drawing to disk.
        """
        png_bytes = session.ifc_plot(
            selector=selector,
            element_ids=element_ids,
            view=view,
            width_mm=width_mm,
            height_mm=height_mm,
            scale=scale,
            png_width=png_width,
            png_height=png_height,
            output_format="png",
        )
        if output_path:
            if output_path.endswith(".svg"):
                svg_bytes = session.ifc_plot(
                    selector=selector,
                    element_ids=element_ids,
                    view=view,
                    width_mm=width_mm,
                    height_mm=height_mm,
                    scale=scale,
                    output_format="svg",
                )
                with open(output_path, "wb") as f:
                    f.write(svg_bytes)
            else:
                with open(output_path, "wb") as f:
                    f.write(png_bytes)
        return [ImageContent(type="image", data=base64.b64encode(png_bytes).decode(), mimeType="image/png")]

    @server.tool(structured_output=False, annotations=_annotations("ifc_render"))
    @_keep_reason
    def ifc_render(
        selector: str = "",
        element_ids: list[int] | None = None,
        view: str = "iso",
        output_path: str = "",
    ) -> list[ImageContent]:
        """Render the loaded IFC model to a PNG image.

        Returns an inline image the LLM can inspect to understand the spatial
        layout of the model or a specific element in context.  Structural
        analysis items are drawn from their topology: curve members (blue) and
        connections (orange) as lines, point connections as points; select
        ``IfcStructuralItem`` for the analysis model alone, ``IfcElement`` for
        the building without it, or highlight the structural items to see
        them inside a translucent building.  If
        ``output_path`` is provided the PNG is also saved to that file path.

        :param selector: ifcopenshell selector to restrict rendered elements
            (e.g. ``'IfcWall'``, ``'IfcBuildingStorey[Name="0"]'``).
            Omit to render the whole model.
        :param element_ids: Step IDs of elements to highlight. Other elements
            are rendered in translucent grey so the subject stands out.
        :param view: Camera angle — ``iso`` (default), ``top``, ``south``,
            ``north``, ``east``, or ``west``.
        :param output_path: Optional file path to save the PNG to disk.
        """
        png_bytes = session.ifc_render(selector=selector, element_ids=element_ids, view=view)
        if output_path:
            with open(output_path, "wb") as f:
                f.write(png_bytes)
        return [ImageContent(type="image", data=base64.b64encode(png_bytes).decode(), mimeType="image/png")]

    if bonsai_port is not None:
        # These draw the model held here, and can write files.
        server.remove_tool("ifc_plot")
        server.remove_tool("ifc_render")
        _add_bonsai_view_tools(server, session, _keep_reason)

    return server


def _add_bonsai_view_tools(server: Any, session: Any, keep_reason: Any) -> None:
    """Register the tools on Bonsai's selection and 3D viewport."""

    @server.tool(annotations=_annotations("bonsai_selection"))
    @keep_reason
    def bonsai_selection() -> dict[str, Any]:
        """List the elements the user has selected in Bonsai, and the active one.

        Call this when the user refers to "this", "these" or "the selected"
        elements. Returns ``count``, ``active`` and up to 200 ``selected``
        elements, each with its STEP ``id``, ``type`` and ``name``.
        """
        return session.call("bonsai_selection", {})

    @server.tool(annotations=_annotations("bonsai_select"))
    @keep_reason
    def bonsai_select(element_ids: list[int | str], frame: bool = True) -> dict[str, Any]:
        """Select elements in Bonsai, replacing the user's selection, to show the user what you mean.

        The first element becomes the active one. Elements without an object
        in Bonsai, and hidden ones, are left out and listed in ``no_object``
        and ``hidden``; an element not yet in a spatial container is hidden.

        :param element_ids: STEP ids or GlobalIds of the elements.
        :param frame: Zoom the 3D viewport to the selected elements.
        """
        return session.call("bonsai_select", {"element_ids": element_ids, "frame": frame})

    @server.tool(annotations=_annotations("bonsai_view"))
    @keep_reason
    def bonsai_view(direction: str = "", frame: str = "selected") -> dict[str, Any]:
        """Turn and zoom the 3D viewport in Bonsai.

        :param direction: ``iso`` (from the front right, above), ``top``,
            ``bottom``, ``front``, ``back``, ``left`` or ``right``. Leave
            empty to keep the current direction.
        :param frame: ``selected`` to zoom to the selected elements (or to
            everything if none are selected), ``all`` to zoom to everything,
            or empty to keep the zoom.
        """
        return session.call("bonsai_view", {"direction": direction, "frame": frame})

    @server.tool(structured_output=False, annotations=_annotations("bonsai_screenshot"))
    @keep_reason
    def bonsai_screenshot() -> list[ImageContent]:
        """Show the 3D viewport in Bonsai as the user sees it, as a PNG image.

        Use it to check the result of an edit, after bonsai_select or
        bonsai_view has pointed the viewport at it.
        """
        result = session.call("bonsai_screenshot", {})
        return [ImageContent(type="image", data=result["png_base64"], mimeType="image/png")]
