# This file was generated with the assistance of an AI coding tool.
from unittest.mock import patch

import pytest

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
