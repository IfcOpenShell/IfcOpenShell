# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

from typing import Any

from ifcmcp.core import IfcSession

try:
    from mcp.server.fastmcp import FastMCP  # type: ignore
except Exception:  # pragma: no cover
    FastMCP = None  # type: ignore


def build_server() -> Any:
    """Create the FastMCP server if the dependency is available."""
    if FastMCP is None:
        raise ImportError(
            "FastMCP is not installed. Install with: pip install ifcmcp[mcp] "
            "(or add 'mcp' to your environment)."
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

    return server