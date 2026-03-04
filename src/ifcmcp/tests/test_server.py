# This file was generated with the assistance of an AI coding tool.
from ifcmcp.server import build_server


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
