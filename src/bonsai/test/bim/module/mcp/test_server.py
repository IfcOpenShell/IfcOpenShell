# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

#
# This file was generated with the assistance of an AI coding tool.

import json
import socket
import threading
import time

import bpy
import ifcopenshell
import ifcopenshell.api.root
import pytest

import bonsai.tool as tool
from bonsai.bim.module.mcp import server
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.mcp


def ask(request: bytes) -> dict:
    """Send one request while the main thread polls, as the Blender timer would."""
    reply = {}

    def client():
        with socket.create_connection(("localhost", server.port()), timeout=10) as sock:
            sock.sendall(request)
            buf = bytearray()
            while b"\0" not in buf:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                buf.extend(chunk)
        reply.update(json.loads(buf.partition(b"\0")[0]))

    thread = threading.Thread(target=client)
    thread.start()
    deadline = time.monotonic() + 10
    while thread.is_alive() and time.monotonic() < deadline:
        server.poll()
        time.sleep(0.01)
    thread.join(timeout=1)
    return reply


def tool_call(name: str, **args) -> dict:
    return ask((json.dumps({"type": "tool", "name": name, "args": args}) + "\0").encode())


class TestMcpBridge(NewFile):
    @pytest.fixture(autouse=True)
    def bridge(self):
        # Port 0 lets the OS pick a free port.
        server.start(0)
        yield
        server.stop()

    def test_answers_read_only_tools_on_the_open_model(self):
        ifc = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject", name="Bridge")
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall", name="W1")
        tool.Ifc.set(ifc)

        reply = tool_call("ifc_select", query="IfcWall")
        assert reply["status"] == "ok"
        assert reply["result"]["total"] == 1
        reply = tool_call("ifc_info", element_id=wall.GlobalId)
        assert reply["result"]["attributes"]["Name"] == "W1"

    def test_sees_changes_made_in_bonsai_since_the_last_call(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        assert tool_call("ifc_select", query="IfcWall")["result"]["total"] == 0
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        assert tool_call("ifc_select", query="IfcWall")["result"]["total"] == 1

    def test_refuses_tools_that_change_the_model(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        reply = tool_call("ifc_edit", function_path="root.create_entity", params='{"ifc_class": "IfcWall"}')
        assert reply["status"] == "error"
        assert "read-only" in reply["message"]
        assert not ifc.by_type("IfcWall")

    def test_reports_that_no_project_is_open(self):
        reply = tool_call("ifc_summary")
        assert reply == {"status": "error", "message": "No IFC project is open in Bonsai"}

    def test_reports_tool_errors(self):
        tool.Ifc.set(ifcopenshell.file(schema="IFC4"))
        reply = tool_call("ifc_info", element_id=999999)
        assert reply["status"] == "error"
        assert "999999" in reply["message"]

    def test_rejects_other_request_types(self):
        reply = ask(b'{"type": "execute", "code": "import os"}\0')
        assert reply["status"] == "error"
        assert "execute" in reply["message"]

    def test_finishes_a_reply_too_large_for_one_send(self, monkeypatch):
        monkeypatch.setattr(server, "handle_request", lambda request: {"status": "ok", "result": "x" * 5_000_000})
        reply = tool_call("ifc_summary")
        assert len(reply["result"]) == 5_000_000

    def test_operators_start_and_stop_the_bridge(self):
        port = server.port()
        server.stop()
        bpy.context.scene.BIMMcpProperties.port = port
        assert bpy.ops.bim.start_mcp_bridge() == {"FINISHED"}
        assert server.port() == port
        assert bpy.ops.bim.stop_mcp_bridge() == {"FINISHED"}
        assert not server.is_running()
