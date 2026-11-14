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
import ifcopenshell.util.representation
import pytest

import bonsai.tool as tool
from bonsai.bim.module.mcp import server
from test.bim.bootstrap import NewFile, NewIfc

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

    def test_refuses_tools_that_load_save_or_run_code(self):
        tool.Ifc.set(ifcopenshell.file(schema="IFC4"))
        for name in ("ifc_execute", "ifc_save", "ifc_load", "ifc_new"):
            reply = tool_call(name)
            assert reply["status"] == "error"
            assert "not available" in reply["message"]

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


def edit(function_path: str, **params) -> dict:
    reply = tool_call("ifc_edit", function_path=function_path, params=json.dumps(params))
    assert reply["status"] == "ok", reply
    return reply["result"]


def objects() -> set[str]:
    return {obj.name for obj in bpy.data.objects}


class TestMcpEdits(NewIfc):
    @pytest.fixture(autouse=True)
    def bridge(self, setup):
        server.start(0)
        # Background mode starts with undo off, and loading the new file turns it off again.
        bpy.ops.ed.undo_push(message="Start")
        yield
        server.stop()

    def create_wall(self, name: str = "Bridged") -> int:
        return edit("root.create_entity", ifc_class="IfcWall", name=name)["result"]["id"]

    def test_a_new_product_gets_an_object(self):
        self.create_wall()
        assert "IfcWall/Bridged" in objects()

    def test_a_new_container_moves_the_object_to_its_collection(self):
        wall = self.create_wall()
        storey = tool.Ifc.get().by_type("IfcBuildingStorey")[0]
        edit("spatial.assign_container", products=str(wall), relating_structure=str(storey.id()))
        collections = bpy.data.objects["IfcWall/Bridged"].users_collection
        assert [c.name for c in collections] == ["IfcBuildingStorey/My Storey"]

    def test_new_geometry_and_placement_are_shown(self):
        wall = self.create_wall()
        body = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        rep = edit("geometry.add_wall_representation", context=str(body.id()), length=3, height=2.5, thickness=0.2)[
            "result"
        ]["id"]
        edit("geometry.assign_representation", product=str(wall), representation=str(rep))
        assert len(bpy.data.objects["IfcWall/Bridged"].data.vertices) == 8
        matrix = [[1, 0, 0, 5], [0, 1, 0, 2], [0, 0, 1, 0], [0, 0, 0, 1]]
        edit("geometry.edit_object_placement", product=str(wall), matrix=matrix)
        assert tuple(bpy.data.objects["IfcWall/Bridged"].matrix_world.translation) == (5, 2, 0)

    def test_a_renamed_product_renames_its_object(self):
        wall = self.create_wall()
        edit("attribute.edit_attributes", product=str(wall), attributes=json.dumps({"Name": "Renamed"}))
        assert "IfcWall/Renamed" in objects()
        assert "IfcWall/Bridged" not in objects()

    def test_a_removed_product_loses_its_object(self):
        wall = self.create_wall()
        edit("root.remove_product", product=str(wall))
        assert "IfcWall/Bridged" not in objects()
        assert tool.Ifc.get_object_by_identifier(wall) is None

    def test_a_storey_gets_a_collection_that_goes_with_it(self):
        building = tool.Ifc.get().by_type("IfcBuilding")[0]
        storey = edit("root.create_entity", ifc_class="IfcBuildingStorey", name="Level 2")["result"]["id"]
        edit("aggregate.assign_object", products=str(storey), relating_object=str(building.id()))
        wall = self.create_wall()
        edit("spatial.assign_container", products=str(wall), relating_structure=str(storey))
        assert [c.name for c in bpy.data.objects["IfcWall/Bridged"].users_collection] == ["IfcBuildingStorey/Level 2"]
        edit("root.remove_product", product=str(storey))
        assert "IfcBuildingStorey/Level 2" not in bpy.data.collections
        assert [c.name for c in bpy.data.objects["IfcWall/Bridged"].users_collection] == ["Unsorted"]

    def test_a_failed_edit_changes_nothing(self):
        before = len(list(tool.Ifc.get()))
        result = edit("nosuchmodule.nosuchfunction")
        assert result["ok"] is False
        assert len(list(tool.Ifc.get())) == before
        assert "not made through MCP" in tool_call("ifc_undo")["message"]

    def test_a_failed_edit_keeps_redo(self):
        self.create_wall()
        tool_call("ifc_undo")
        edit("nosuchmodule.nosuchfunction")
        assert tool_call("ifc_redo")["status"] == "ok"
        assert "IfcWall/Bridged" in objects()

    def test_an_edit_bonsai_cannot_record_is_reverted(self, monkeypatch):
        def fail():
            raise RuntimeError("no undo step")

        monkeypatch.setattr(server, "adopt_edit", fail)
        reply = tool_call("ifc_edit", function_path="root.create_entity", params='{"ifc_class": "IfcWall"}')
        assert reply["status"] == "error"
        assert "could not run the edit" in reply["message"]
        assert not tool.Ifc.get().by_type("IfcWall")

    def test_undo_and_redo_an_edit(self):
        self.create_wall()
        reply = tool_call("ifc_undo")
        assert reply == {"status": "ok", "result": {"ok": True, "undo_available": 0, "redo_available": 1}}
        assert not tool.Ifc.get().by_type("IfcWall")
        assert "IfcWall/Bridged" not in objects()
        reply = tool_call("ifc_redo")
        assert reply == {"status": "ok", "result": {"ok": True, "undo_available": 1, "redo_available": 0}}
        assert tool.Ifc.get().by_type("IfcWall")
        assert "IfcWall/Bridged" in objects()

    def test_undo_leaves_a_change_made_in_bonsai(self):
        self.create_wall()
        bpy.data.objects["IfcSite/My Site"].location.x += 7
        bpy.ops.ed.undo_push(message="Move the site")
        reply = tool_call("ifc_undo")
        assert reply["status"] == "error"
        assert "not made through MCP" in reply["message"]
        assert bpy.data.objects["IfcSite/My Site"].location.x == 7
        assert tool.Ifc.get().by_type("IfcWall")

    def test_undo_refuses_an_ifc_change_made_in_bonsai(self):
        assert tool_call("ifc_undo")["status"] == "error"
        assert tool.Ifc.get().by_type("IfcProject")

    def test_redo_leaves_a_change_made_in_bonsai_after_the_undo(self):
        self.create_wall()
        assert tool_call("ifc_undo")["status"] == "ok"
        bpy.data.objects["IfcSite/My Site"].location.x += 7
        bpy.ops.ed.undo_push(message="Move the site")
        reply = tool_call("ifc_redo")
        assert reply == {
            "status": "error",
            "message": "Nothing to redo: a change made in Bonsai since the undo discarded it.",
        }
        assert bpy.data.objects["IfcSite/My Site"].location.x == 7
        assert not tool.Ifc.get().by_type("IfcWall")


class TestMcpView(NewIfc):
    @pytest.fixture(autouse=True)
    def bridge(self, setup):
        server.start(0)
        bpy.ops.ed.undo_push(message="Start")
        yield
        server.stop()

    def create_wall(self, name: str) -> ifcopenshell.entity_instance:
        """A wall in the storey, as one not yet in a container is hidden."""
        wall = edit("root.create_entity", ifc_class="IfcWall", name=name)["result"]["id"]
        storey = tool.Ifc.get().by_type("IfcBuildingStorey")[0].id()
        edit("spatial.assign_container", products=str(wall), relating_structure=str(storey))
        return tool.Ifc.get().by_id(wall)

    def test_selection_lists_the_selected_elements(self):
        wall = self.create_wall("Picked")
        self.create_wall("Other")
        bpy.ops.object.select_all(action="DESELECT")
        bpy.ops.mesh.primitive_cube_add()  # Not an IFC element, so not listed.
        obj = tool.Ifc.get_object(wall)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        result = tool_call("bonsai_selection")["result"]
        assert result == {
            "count": 1,
            "active": {"id": wall.id(), "type": "IfcWall", "name": "Picked"},
            "selected": [{"id": wall.id(), "type": "IfcWall", "name": "Picked"}],
        }

    def test_select_replaces_the_selection(self):
        first, second = self.create_wall("First"), self.create_wall("Second")
        bpy.data.objects["IfcSite/My Site"].select_set(True)
        reply = tool_call("bonsai_select", element_ids=[second.GlobalId, str(first.id())])
        # Without a window there is no viewport to frame.
        assert reply == {"status": "ok", "result": {"selected": [second.id(), first.id()], "framed": False}}
        assert {o.name for o in bpy.context.selected_objects} == {"IfcWall/First", "IfcWall/Second"}
        assert bpy.context.view_layer.objects.active.name == "IfcWall/Second"

    def test_select_reports_elements_it_cannot_select(self):
        wall, hidden = self.create_wall("Shown"), self.create_wall("Hidden")
        tool.Ifc.get_object(hidden).hide_set(True)
        unshown = ifcopenshell.api.root.create_entity(tool.Ifc.get(), ifc_class="IfcWall")
        result = tool_call("bonsai_select", element_ids=[wall.id(), hidden.id(), unshown.id()], frame=False)["result"]
        assert result == {"selected": [wall.id()], "no_object": [unshown.id()], "hidden": [hidden.id()]}

    def test_select_fails_when_nothing_can_be_selected(self):
        unshown = ifcopenshell.api.root.create_entity(tool.Ifc.get(), ifc_class="IfcWall")
        reply = tool_call("bonsai_select", element_ids=[unshown.id()])
        assert reply["status"] == "error"
        assert "no object" in reply["message"]

    def test_view_and_screenshot_need_a_window(self):
        for name in ("bonsai_view", "bonsai_screenshot"):
            reply = tool_call(name)
            assert reply["status"] == "error"
            assert "without a window" in reply["message"]
