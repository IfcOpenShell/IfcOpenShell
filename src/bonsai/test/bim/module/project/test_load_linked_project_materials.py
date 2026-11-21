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

from types import SimpleNamespace

import pytest

import bonsai.bim.module.project.operator as project_operator
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.project


def _make_material(*, use_nodes=True, with_bsdf=True, has_render_method=True):
    base_color_socket = SimpleNamespace(default_value=(0.0, 0.0, 0.0, 1.0))
    alpha_socket = SimpleNamespace(default_value=1.0)
    socket_map = {"Base Color": base_color_socket, "Alpha": alpha_socket}
    inputs = SimpleNamespace(get=lambda name: socket_map.get(name))
    nodes = [SimpleNamespace(type="BSDF_PRINCIPLED", inputs=inputs)] if with_bsdf else []
    mat = SimpleNamespace(
        diffuse_color=(0.8, 0.8, 0.8, 1.0),
        use_nodes=use_nodes,
        node_tree=SimpleNamespace(nodes=nodes),
    )
    if has_render_method:
        mat.surface_render_method = "DITHERED"
    return mat, base_color_socket, alpha_socket


class TestLoadLinkedProjectMaterials(NewFile):
    def test_sets_principled_base_color_and_alpha(self):
        op = project_operator.LoadLinkedProject()
        mat, base_color_socket, alpha_socket = _make_material()

        op._apply_material_color(mat, (0.2, 0.4, 0.6, 0.5))

        assert mat.diffuse_color == (0.2, 0.4, 0.6, 0.5)
        assert base_color_socket.default_value == (0.2, 0.4, 0.6, 1.0)
        assert alpha_socket.default_value == 0.5
        assert mat.surface_render_method == "BLENDED"

    def test_opaque_color_keeps_default_render_method(self):
        op = project_operator.LoadLinkedProject()
        mat, base_color_socket, alpha_socket = _make_material()

        op._apply_material_color(mat, (0.9, 0.1, 0.2, 1.0))

        assert mat.diffuse_color == (0.9, 0.1, 0.2, 1.0)
        assert base_color_socket.default_value == (0.9, 0.1, 0.2, 1.0)
        assert alpha_socket.default_value == 1.0
        assert mat.surface_render_method == "DITHERED"
