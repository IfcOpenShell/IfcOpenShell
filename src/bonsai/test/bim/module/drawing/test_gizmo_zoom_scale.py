# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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

"""Zoom cap for billboarded gizmo icons: icons keep their model size until they
would exceed ``gizmo_icon_max_size`` pixels on screen, then stop growing."""

import math
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from mathutils import Matrix, Vector

import bonsai.tool as tool
from bonsai.bim.module.drawing import gizmos

pytestmark = pytest.mark.drawing

REGION_WIDTH = 1000


def make_ortho_context(view_width_m: float, ui_scale: float = 1.0) -> SimpleNamespace:
    """Top-down orthographic view showing ``view_width_m`` metres across the region."""
    window_matrix = Matrix.Identity(4)
    window_matrix[0][0] = 2.0 / view_width_m
    view_matrix = Matrix.Identity(4)
    rv3d = SimpleNamespace(
        view_matrix=view_matrix,
        window_matrix=window_matrix,
        perspective_matrix=window_matrix @ view_matrix,
        view_location=Vector((0.0, 0.0, 0.0)),
    )
    return SimpleNamespace(
        region_data=rv3d,
        region=SimpleNamespace(width=REGION_WIDTH),
        preferences=SimpleNamespace(system=SimpleNamespace(ui_scale=ui_scale)),
    )


@pytest.fixture
def max_size():
    prefs = SimpleNamespace(gizmo_icon_max_size=40)
    with patch.object(tool.Blender, "get_addon_preferences", return_value=prefs):
        yield prefs


def icon_px(context) -> float:
    """On-screen width of a default-scale icon after the zoom cap."""
    px_per_metre = REGION_WIDTH / (2.0 / context.region_data.window_matrix[0][0])
    return gizmos.DEFAULT_BILLBOARD_SCALE * gizmos.get_icon_zoom_scale(context) * px_per_metre


def test_zoomed_out_icons_keep_model_size(max_size):
    # 100 m across 1000 px: a 0.5 m icon is 5 px, well under the cap.
    assert gizmos.get_icon_zoom_scale(make_ortho_context(100.0)) == 1.0


def test_zoomed_in_icons_stop_at_max_size(max_size):
    # 2 m across 1000 px: a 0.5 m icon would be 250 px uncapped.
    assert icon_px(make_ortho_context(2.0)) == pytest.approx(40.0)
    assert icon_px(make_ortho_context(0.5)) == pytest.approx(40.0)


def test_max_size_follows_ui_scale(max_size):
    assert icon_px(make_ortho_context(2.0, ui_scale=2.0)) == pytest.approx(80.0)


def test_zero_max_size_disables_cap(max_size):
    max_size.gizmo_icon_max_size = 0
    assert gizmos.get_icon_zoom_scale(make_ortho_context(0.5)) == 1.0


def test_perspective_measures_at_view_pivot(max_size):
    # 90 degree FOV: at depth d the region spans 2d metres.
    distance = 1.0
    window_matrix = Matrix(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, -1, -0.02), (0, 0, -1, 0)))
    view_matrix = Matrix.Translation((0.0, 0.0, -distance))
    context = make_ortho_context(1.0)
    context.region_data = SimpleNamespace(
        view_matrix=view_matrix,
        window_matrix=window_matrix,
        perspective_matrix=window_matrix @ view_matrix,
        view_location=Vector((0.0, 0.0, 0.0)),
    )
    px_per_metre = REGION_WIDTH / (2.0 * distance)
    capped = gizmos.DEFAULT_BILLBOARD_SCALE * gizmos.get_icon_zoom_scale(context) * px_per_metre
    assert capped == pytest.approx(40.0)


def test_billboard_rotation_carries_zoom_and_offsets_follow(max_size):
    context = make_ortho_context(2.0)
    zoom = gizmos.get_icon_zoom_scale(context)
    billboard_rot = gizmos.get_billboard_rotation(context)
    assert gizmos.get_billboard_scale(billboard_rot) == pytest.approx(zoom)
    assert gizmos.get_screen_up(billboard_rot).length == pytest.approx(zoom)
    stripped = gizmos.strip_billboard_scale(billboard_rot)
    assert gizmos.get_billboard_scale(stripped) == pytest.approx(1.0)


def test_billboarded_along_axis_applies_zoom_once():
    zoom = 0.25
    rotation = Matrix.Rotation(math.radians(30), 4, "X")
    billboard_rot = rotation @ Matrix.Scale(zoom, 4)
    result = gizmos.billboarded_along_axis(Vector((1, 2, 3)), billboard_rot, Vector((1, 0, 0)), scale=0.5)
    assert result.to_3x3().col[0].length == pytest.approx(0.5 * zoom)
    assert result.to_3x3().col[2].normalized().dot(rotation.to_3x3().col[2]) == pytest.approx(1.0)
