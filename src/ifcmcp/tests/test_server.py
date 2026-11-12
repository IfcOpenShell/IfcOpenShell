# This file was generated with the assistance of an AI coding tool.
import asyncio
import importlib
import re
from unittest.mock import patch

import pytest

from ifcmcp.__main__ import execute_allowed
from ifcmcp.instructions import EXECUTE_INSTRUCTIONS, INSTRUCTIONS
from ifcmcp.server import READ_ONLY_TOOLS, build_server

try:
    from mcp.server.mcpserver.exceptions import ToolError, UnexpectedToolError
except ImportError:
    # mcp 1.x keeps every exception's reason, so it never raises the bare message.
    from mcp.server.fastmcp.exceptions import ToolError

    class UnexpectedToolError(ToolError):
        pass


class TestServerRegistration:
    def test_server_name(self):
        server = build_server()
        assert server.name == "ifc-mcp"

    def test_all_tools_registered(self):
        server = build_server()
        tools = [t.name for t in server._tool_manager.list_tools()]
        expected = [
            "ifc_load",
            "ifc_save",
            "ifc_summary",
            "ifc_tree",
            "ifc_info",
            "ifc_select",
            "ifc_relations",
            "ifc_clash",
            "ifc_list",
            "ifc_docs",
            "ifc_edit",
        ]
        for name in expected:
            assert name in tools, f"Tool {name} not registered"

    def test_all_tools_have_descriptions(self):
        server = build_server()
        tools = server._tool_manager.list_tools()
        missing = [t.name for t in tools if not (t.description or "").strip()]
        assert not missing, f"Tools with no description: {missing}"


class TestInstructions:
    """The instructions name tools and API functions; keep them from going stale."""

    def test_server_sends_the_instructions(self):
        assert build_server().instructions == INSTRUCTIONS
        assert build_server(allow_execute=True).instructions == INSTRUCTIONS + EXECUTE_INSTRUCTIONS

    def test_every_tool_named_exists(self):
        tools = {t.name for t in build_server(allow_execute=True)._tool_manager.list_tools()}
        named = set(re.findall(r"\bifc_[a-z_]+", INSTRUCTIONS + EXECUTE_INSTRUCTIONS))
        assert named, "expected the instructions to name some tools"
        assert named <= tools, named - tools

    def test_execute_is_only_described_when_offered(self):
        assert "ifc_execute" not in INSTRUCTIONS
        assert "ifc_execute" in EXECUTE_INSTRUCTIONS

    def test_every_api_function_named_exists(self):
        named = set(re.findall(r"\b([a-z]+)\.([a-z_]+)\b", INSTRUCTIONS + EXECUTE_INSTRUCTIONS))
        named = {(m, f) for m, f in named if m != "ifcopenshell"}
        assert named, "expected the instructions to name some API functions"
        for module, function in named:
            api = importlib.import_module(f"ifcopenshell.api.{module}")
            assert hasattr(api, function), f"{module}.{function}"


class TestToolAnnotations:
    """Clients use these hints to decide which calls need the user's approval."""

    @pytest.fixture
    def hints(self):
        server = build_server()
        return {
            t.name: t.annotations.model_dump(by_alias=True, exclude_none=True)
            for t in server._tool_manager.list_tools()
        }

    def test_every_read_only_name_is_a_tool(self, hints):
        assert READ_ONLY_TOOLS <= hints.keys()

    def test_read_only_tools(self, hints):
        for name in READ_ONLY_TOOLS:
            assert hints[name] == {"readOnlyHint": True, "openWorldHint": False}, name

    def test_every_other_tool_is_destructive(self, hints):
        for name in hints.keys() - READ_ONLY_TOOLS:
            assert hints[name] == {"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False}, name

    @pytest.mark.parametrize(
        "name",
        [
            "ifc_edit",
            "ifc_shape",
            "ifc_quantify",
            "ifc_save",
            "ifc_load",
            "ifc_new",
            "ifc_reset",
            "ifc_plot",
            "ifc_render",
        ],
    )
    def test_tools_that_change_state_are_not_read_only(self, name):
        assert name not in READ_ONLY_TOOLS


class TestElementLookup:
    """The server accepts a GlobalId or a STEP id wherever it takes element_id."""

    @pytest.mark.parametrize("tool", ["ifc_info", "ifc_relations", "ifc_clash"])
    def test_by_global_id(self, tool, model, model_file):
        server = build_server()
        asyncio.run(server.call_tool("ifc_load", {"path": model_file}))
        wall = model.by_type("IfcWall")[0]
        for element_id in (wall.GlobalId, wall.id()):
            asyncio.run(server.call_tool(tool, {"element_id": element_id}))


class TestExecuteOption:
    def test_off_by_default(self):
        assert "ifc_execute" not in [t.name for t in build_server()._tool_manager.list_tools()]

    def test_offered_when_allowed(self):
        assert "ifc_execute" in [t.name for t in build_server(allow_execute=True)._tool_manager.list_tools()]

    def test_not_callable_when_not_offered(self, model_file):
        server = build_server()
        asyncio.run(server.call_tool("ifc_load", {"path": model_file}))
        with pytest.raises(Exception, match="ifc_execute"):
            asyncio.run(server.call_tool("ifc_execute", {"code": "result = 1"}))

    @pytest.mark.parametrize(
        "transport, no_execute, allowed",
        [
            ("stdio", False, True),
            ("stdio", True, False),
            ("sse", False, False),
            ("streamable-http", False, False),
        ],
    )
    def test_only_offered_over_stdio(self, transport, no_execute, allowed):
        assert execute_allowed(transport, no_execute) is allowed


class TestToolErrorsKeepTheirReason:
    """MCPServer replaces the text of any exception but ToolError with a bare
    "Error executing tool <name>". Each tool raises ToolError, so the agent is told
    why its call failed."""

    @pytest.mark.parametrize(
        "name, arguments, reason",
        [
            ("ifc_summary", {}, "No model loaded"),
            ("ifc_load", {"path": "/nonexistent/model.ifc"}, "/nonexistent/model.ifc"),
            ("ifc_info", {"element_id": 999999}, "#999999"),
            ("ifc_plot", {}, "No model loaded"),
            ("ifc_render", {}, "No model loaded"),
        ],
    )
    def test_reason_reaches_the_client(self, name, arguments, reason):
        server = build_server()
        if name == "ifc_info":
            asyncio.run(server.call_tool("ifc_new", {}))
        with pytest.raises(ToolError) as caught:
            asyncio.run(server.call_tool(name, arguments))
        assert not isinstance(caught.value, UnexpectedToolError)
        assert reason in str(caught.value)

    def test_no_tool_loses_its_reason(self):
        """Every registered tool, however it is registered: called with no model
        loaded, it either works or fails with its reason, never the bare message."""
        server = build_server()
        dummy = {"string": "", "integer": 0, "number": 0, "boolean": False, "array": [], "object": {}}
        for tool in server._tool_manager.list_tools():
            schema = tool.parameters or {}
            props = schema.get("properties", {})
            args = {name: dummy.get(props.get(name, {}).get("type"), "") for name in schema.get("required", [])}
            try:
                asyncio.run(server.call_tool(tool.name, args))
            except UnexpectedToolError as e:
                pytest.fail(f"{tool.name} lost its reason: {e}")
            except ToolError:
                pass


@pytest.fixture
def tool_fns():
    """Return a dict of tool name → raw function from a freshly built server."""
    server = build_server()
    return {t.name: t.fn for t in server._tool_manager.list_tools()}


PNG_FAKE = b"\x89PNG\r\n\x1a\nFAKE"
SVG_FAKE = b"<svg>FAKE</svg>"


class TestRenderOutputPath:
    def test_no_output_path_no_file_written(self, tool_fns, tmp_path):
        with patch("ifcmcp.core.IfcSession.ifc_render", return_value=PNG_FAKE):
            tool_fns["ifc_render"](selector="", element_ids=None, view="iso", output_path="")
        assert list(tmp_path.iterdir()) == []

    def test_png_output_path_writes_file(self, tool_fns, tmp_path):
        out = str(tmp_path / "render.png")
        with patch("ifcmcp.core.IfcSession.ifc_render", return_value=PNG_FAKE):
            tool_fns["ifc_render"](selector="", element_ids=None, view="iso", output_path=out)
        assert open(out, "rb").read() == PNG_FAKE


class TestPlotOutputPath:
    def test_no_output_path_no_file_written(self, tool_fns, tmp_path):
        with patch("ifcmcp.core.IfcSession.ifc_plot", return_value=PNG_FAKE):
            tool_fns["ifc_plot"](
                selector="",
                element_ids=None,
                view="floorplan",
                width_mm=297.0,
                height_mm=420.0,
                scale=0.01,
                png_width=1024,
                png_height=1024,
                output_path="",
            )
        assert list(tmp_path.iterdir()) == []

    def test_png_output_path_writes_png(self, tool_fns, tmp_path):
        out = str(tmp_path / "plot.png")
        with patch("ifcmcp.core.IfcSession.ifc_plot", return_value=PNG_FAKE):
            tool_fns["ifc_plot"](
                selector="",
                element_ids=None,
                view="floorplan",
                width_mm=297.0,
                height_mm=420.0,
                scale=0.01,
                png_width=1024,
                png_height=1024,
                output_path=out,
            )
        assert open(out, "rb").read() == PNG_FAKE

    def test_svg_output_path_writes_svg(self, tool_fns, tmp_path):
        out = str(tmp_path / "plot.svg")
        # ifc_plot is called twice: once with "png" for the inline image,
        # once with "svg" for the file.
        with patch("ifcmcp.core.IfcSession.ifc_plot", side_effect=[PNG_FAKE, SVG_FAKE]):
            tool_fns["ifc_plot"](
                selector="",
                element_ids=None,
                view="floorplan",
                width_mm=297.0,
                height_mm=420.0,
                scale=0.01,
                png_width=1024,
                png_height=1024,
                output_path=out,
            )
        assert open(out, "rb").read() == SVG_FAKE
