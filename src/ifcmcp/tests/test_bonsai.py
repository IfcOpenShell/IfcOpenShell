# This file was generated with the assistance of an AI coding tool.
import asyncio
import json
import re
import socket
import threading

import pytest

from ifcmcp.bonsai import BonsaiSession
from ifcmcp.core import IfcSession, IfcSessionError
from ifcmcp.instructions import BONSAI_INSTRUCTIONS
from ifcmcp.server import BONSAI_TOOLS, BONSAI_VIEW_TOOLS, build_server

try:
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError:
    from mcp.server.fastmcp.exceptions import ToolError


class FakeBonsai:
    """Answers bridge requests the way Bonsai's MCP bridge does, on a model held here."""

    def __init__(self, model):
        self.session = IfcSession(model=model)
        self.requests = []
        self.sock = socket.create_server(("localhost", 0))
        self.port = self.sock.getsockname()[1]
        self.thread = threading.Thread(target=self.serve, daemon=True)
        self.thread.start()

    def serve(self):
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            with conn:
                buf = bytearray()
                while b"\0" not in buf:
                    buf.extend(conn.recv(65536))
                request = json.loads(buf.partition(b"\0")[0])
                self.requests.append(request)
                try:
                    reply = {"status": "ok", "result": self.session.dispatch(request["name"], request["args"])}
                except Exception as e:
                    reply = {"status": "error", "message": str(e)}
                conn.sendall((json.dumps(reply) + "\0").encode())

    def close(self):
        self.sock.close()


@pytest.fixture
def bonsai(model):
    fake = FakeBonsai(model)
    yield fake
    fake.close()


def free_port():
    with socket.socket() as sock:
        sock.bind(("localhost", 0))
        return sock.getsockname()[1]


class TestBonsaiSession:
    def test_forwards_positional_and_keyword_arguments_by_name(self, bonsai, model):
        session = BonsaiSession(port=bonsai.port)
        wall = model.by_type("IfcWall")[0]
        assert session.ifc_info(wall.GlobalId)["attributes"]["Name"] == "Wall001"
        assert session.ifc_select("IfcWall", limit=0) == {"total": 1, "offset": 0, "elements": []}
        assert bonsai.requests[-1] == {
            "type": "tool",
            "name": "ifc_select",
            "args": {"query": "IfcWall", "limit": 0},
        }

    def test_raises_bonsai_errors_with_their_message(self, bonsai):
        with pytest.raises(IfcSessionError, match="999999"):
            BonsaiSession(port=bonsai.port).ifc_info(999999)

    def test_says_how_to_start_the_bridge_when_bonsai_is_not_listening(self):
        with pytest.raises(IfcSessionError, match="Start MCP Bridge"):
            BonsaiSession(port=free_port()).ifc_summary()

    def test_rejects_arguments_the_tool_does_not_take(self, bonsai):
        with pytest.raises(TypeError):
            BonsaiSession(port=bonsai.port).ifc_summary(path="x.ifc")
        assert not bonsai.requests


class TestBonsaiServer:
    def test_offers_only_the_bonsai_tools(self):
        server = build_server(allow_execute=True, bonsai_port=free_port())
        assert {t.name for t in server._tool_manager.list_tools()} == BONSAI_TOOLS | BONSAI_VIEW_TOOLS

    def test_sends_the_bonsai_instructions(self):
        assert build_server(bonsai_port=free_port()).instructions == BONSAI_INSTRUCTIONS

    def test_every_tool_named_in_the_instructions_is_offered(self):
        tools = {t.name for t in build_server(bonsai_port=free_port())._tool_manager.list_tools()}
        named = set(re.findall(r"\b(?:ifc|bonsai)_[a-z_]+", BONSAI_INSTRUCTIONS))
        assert named <= tools, named - tools

    def test_undo_and_redo_describe_bonsai_history(self):
        tools = {t.name: t for t in build_server(bonsai_port=free_port())._tool_manager.list_tools()}
        for name in ("ifc_undo", "ifc_redo"):
            assert "Bonsai" in tools[name].description
            assert "Loading" not in tools[name].description

    def test_tool_calls_reach_bonsai(self, bonsai):
        server = build_server(bonsai_port=bonsai.port)
        asyncio.run(server.call_tool("ifc_summary", {}))
        asyncio.run(server.call_tool("ifc_select", {"query": "IfcSlab"}))
        assert [r["name"] for r in bonsai.requests] == ["ifc_summary", "ifc_select"]

    def test_edits_reach_bonsai(self, bonsai):
        server = build_server(bonsai_port=bonsai.port)
        params = json.dumps({"ifc_class": "IfcWall", "name": "Bridged"})
        asyncio.run(server.call_tool("ifc_edit", {"function_path": "root.create_entity", "params": params}))
        asyncio.run(server.call_tool("ifc_undo", {}))
        assert [r["name"] for r in bonsai.requests] == ["ifc_edit", "ifc_undo"]
        assert bonsai.requests[0]["args"] == {"function_path": "root.create_entity", "params": params}

    def test_view_tools_reach_bonsai(self, bonsai):
        def answer(name, args):
            if name == "bonsai_screenshot":
                return {"png_base64": "iVBORw0K", "width": 1, "height": 1}
            return {"name": name, "args": args}

        bonsai.session.dispatch = answer
        server = build_server(bonsai_port=bonsai.port)
        asyncio.run(server.call_tool("bonsai_selection", {}))
        asyncio.run(server.call_tool("bonsai_select", {"element_ids": [5, "2O2Fr$t4X7Zf8NOew3FLOH"]}))
        asyncio.run(server.call_tool("bonsai_view", {"direction": "top"}))
        image = asyncio.run(server.call_tool("bonsai_screenshot", {}))
        assert bonsai.requests == [
            {"type": "tool", "name": "bonsai_selection", "args": {}},
            {
                "type": "tool",
                "name": "bonsai_select",
                "args": {"element_ids": [5, "2O2Fr$t4X7Zf8NOew3FLOH"], "frame": True},
            },
            {"type": "tool", "name": "bonsai_view", "args": {"direction": "top", "frame": "selected"}},
            {"type": "tool", "name": "bonsai_screenshot", "args": {}},
        ]
        # mcp 2.x returns a CallToolResult, 1.x the content list.
        content = getattr(image, "content", image)
        assert [(c.type, c.data) for c in content] == [("image", "iVBORw0K")]

    def test_view_tools_are_not_offered_without_bonsai(self):
        tools = {t.name for t in build_server()._tool_manager.list_tools()}
        assert not tools & BONSAI_VIEW_TOOLS

    def test_reason_reaches_the_client_when_bonsai_is_not_listening(self):
        server = build_server(bonsai_port=free_port())
        with pytest.raises(ToolError, match="Start MCP Bridge"):
            asyncio.run(server.call_tool("ifc_summary", {}))
