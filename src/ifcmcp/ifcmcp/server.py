# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

import base64
from typing import Any

from ifcmcp.core import IfcSession

try:
    from mcp.server.fastmcp import FastMCP  # type: ignore
    from mcp.types import ImageContent  # type: ignore
except Exception:  # pragma: no cover
    FastMCP = None  # type: ignore
    ImageContent = None  # type: ignore


def build_server() -> Any:
    """Create the FastMCP server if the dependency is available."""
    if FastMCP is None:
        raise ImportError(
            "FastMCP is not installed. Install with: pip install ifcmcp[mcp] " "(or add 'mcp' to your environment)."
        )

    session = IfcSession()

    server = FastMCP(
        name="ifc-mcp",
        instructions=(
            "MCP server for querying and editing IFC building models. "
            "Load a file first with ifc_load, then use query/edit tools. "
            "Save changes with ifc_save."
        ),
    )

    # ---- Lifecycle ----
    @server.tool()
    def ifc_new(schema: str = "IFC4") -> dict[str, Any]:
        return session.ifc_new(schema=schema)

    @server.tool()
    def ifc_load(path: str) -> str:
        return session.ifc_load(path)

    @server.tool()
    def ifc_save(path: str = "") -> str:
        return session.ifc_save(path)

    @server.tool()
    def ifc_reset() -> dict[str, Any]:
        return session.ifc_reset()

    # ---- Query ----
    @server.tool()
    def ifc_summary() -> dict[str, Any]:
        return session.ifc_summary()

    @server.tool()
    def ifc_tree() -> dict[str, Any] | list[dict[str, Any]]:
        return session.ifc_tree()

    @server.tool()
    def ifc_info(element_id: int) -> dict[str, Any]:
        return session.ifc_info(element_id)

    @server.tool()
    def ifc_select(query: str) -> list[dict[str, Any]]:
        return session.ifc_select(query)

    @server.tool()
    def ifc_relations(element_id: int, traverse: str = "") -> dict[str, Any] | list[dict[str, Any]]:
        return session.ifc_relations(element_id, traverse=traverse)

    @server.tool()
    def ifc_clash(
        element_id: int,
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

    @server.tool()
    def ifc_contexts() -> list[dict[str, Any]]:
        return session.ifc_contexts()

    @server.tool()
    def ifc_materials() -> list[dict[str, Any]]:
        return session.ifc_materials()

    # ---- Edit ----
    @server.tool()
    def ifc_list(module: str = "") -> list[dict]:
        return session.ifc_list(module=module)

    @server.tool()
    def ifc_docs(function_path: str) -> dict:
        return session.ifc_docs(function_path=function_path)

    @server.tool()
    def ifc_edit(function_path: str, params: str = "{}") -> dict:
        return session.ifc_edit(function_path=function_path, params=params)

    # ---- Extended query + edit ----
    @server.tool()
    def ifc_validate(express_rules: bool = False) -> dict[str, Any]:
        return session.ifc_validate(express_rules=express_rules)

    @server.tool()
    def ifc_schedule(max_depth: int | None = None) -> list[dict[str, Any]]:
        return session.ifc_schedule(max_depth=max_depth)

    @server.tool()
    def ifc_cost(max_depth: int | None = None) -> list[dict[str, Any]]:
        return session.ifc_cost(max_depth=max_depth)

    @server.tool()
    def ifc_schema(entity_type: str) -> dict[str, Any]:
        return session.ifc_schema(entity_type=entity_type)

    @server.tool()
    def ifc_quantify(rule: str, selector: str = "") -> dict[str, Any]:
        return session.ifc_quantify(rule=rule, selector=selector)

    # ---- Shape builder ----
    @server.tool()
    def ifc_shape_list() -> list[dict]:
        return session.ifc_shape_list()

    @server.tool()
    def ifc_shape_docs(method: str) -> dict:
        return session.ifc_shape_docs(method=method)

    @server.tool()
    def ifc_shape(method: str, params: str = "{}") -> dict:
        return session.ifc_shape(method=method, params=params)

    @server.tool(structured_output=False)
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

    @server.tool(structured_output=False)
    def ifc_render(
        selector: str = "",
        element_ids: list[int] | None = None,
        view: str = "iso",
        output_path: str = "",
    ) -> list[ImageContent]:
        """Render the loaded IFC model to a PNG image.

        Returns an inline image the LLM can inspect to understand the spatial
        layout of the model or a specific element in context.  If
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

    return server
