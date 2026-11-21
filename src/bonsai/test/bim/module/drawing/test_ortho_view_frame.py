# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import ast
import textwrap
import types
from pathlib import Path

import pytest

pytestmark = pytest.mark.drawing


def _load_frame_helpers():
    bonsai_root = Path(__file__).resolve().parents[4] / "bonsai"

    def grab(rel_path: str, names: set[str]) -> dict[str, str]:
        src = (bonsai_root / rel_path).read_text(encoding="utf-8")
        return {
            node.name: textwrap.dedent(ast.get_source_segment(src, node))
            for node in ast.walk(ast.parse(src))
            if isinstance(node, ast.FunctionDef) and node.name in names
        }

    helper = grab("bim/module/drawing/helper.py", {"ortho_view_frame"})
    prop = grab("bim/module/drawing/prop.py", {"update_camera_resolution", "get_scale_and_aspect_ratio"})

    class Props:
        dpi = 75

        def __init__(self, width: float, height: float):
            self.width = width
            self.height = height

    class Camera:
        clip_start = 0.0
        clip_end = 10.0

        def __init__(self, props: Props):
            self.props = props
            props.id_data = self

    drawing_tool = types.SimpleNamespace(
        get_camera_props=lambda cam: cam.props,
        get_diagram_scale=lambda cam: {"Scale": "1/50"},
        get_scale_ratio=lambda scale: 1 / 50,
    )
    ns = {
        "tool": types.SimpleNamespace(Drawing=drawing_tool),
        "bpy": types.SimpleNamespace(types=types.SimpleNamespace(Camera=Camera)),
        "parse_diagram_scale": lambda camera: 1 / 50,
    }
    for code in (*prop.values(), *helper.values()):
        exec(code, ns)

    Props.update_camera_resolution = ns["update_camera_resolution"]
    Props.get_scale_and_aspect_ratio = ns["get_scale_and_aspect_ratio"]
    return Props, Camera, ns["ortho_view_frame"]


class TestOrthoViewFrame:
    @pytest.mark.parametrize(("width", "height"), [(20.0, 3.0), (3.0, 20.0), (10.0, 10.0)])
    def test_frame_matches_landscape_and_portrait_dimensions(self, width: float, height: float):
        props_cls, camera_cls, ortho_view_frame = _load_frame_helpers()
        props = props_cls(width, height)
        camera = camera_cls(props)
        props.update_camera_resolution()

        xmin, xmax, ymin, ymax = ortho_view_frame(camera, margin=0.0)[:4]
        assert abs((xmax - xmin) - width) < 0.01 * width
        assert abs((ymax - ymin) - height) < 0.01 * height
