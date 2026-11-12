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

"""Offset arithmetic for the filling (Door / Window) wall-offset dimension gizmos.

The apply path (``_set_offset``) must translate ``obj.matrix_world`` so the
corresponding read path (``_get_offset``) reads back the new value — i.e.
drag a left-offset to 2.0 m, then reading the left offset must return ~2.0 m.
The tests below pin that round-trip, the rotated/flipped filling case (the
add-opening flow may 180° a filling onto the wall's opposite face), and the
visibility predicate."""

from math import pi
from unittest import mock

import pytest
from mathutils import Matrix

pytestmark = pytest.mark.model

# Module under test, plus its cache dict so each test starts from a clean slate.
import bonsai.bim.module.model.wall_offset_gizmos as subject


@pytest.fixture(autouse=True)
def _clear_geom_cache():
    """Per-test isolation — the module-level cache would otherwise carry mocks
    across tests and surface as flaky-looking failures."""
    subject._GEOM_CACHE.clear()
    yield
    subject._GEOM_CACHE.clear()


def _make_props(filling_matrix, overall_width=1.0, overall_height=2.0, name="FillingObj"):
    """Filling PropertyGroup stand-in (``BIMDoorProperties`` /
    ``BIMWindowProperties`` share the relevant shape). The wall-offset helpers
    only touch ``id_data`` (the filling obj), ``overall_width``, and
    ``overall_height``; nothing else from the real PropertyGroup matters here."""
    filling_obj = mock.Mock(name=name)
    filling_obj.name = name
    filling_obj.matrix_world = filling_matrix
    props = mock.Mock(spec=["id_data", "overall_width", "overall_height"])
    props.id_data = filling_obj
    props.overall_width = overall_width
    props.overall_height = overall_height
    return props, filling_obj


def _patch_host_wall(wall_matrix, length, height, geom_gen=1, host_present=True, x_angle=0.0):
    """Mock the chain ``Ifc.get_entity → Spatial.get_host_wall → Ifc.get_object``
    and the ``tool.Wall.*`` IFC reads so the helpers see a host wall
    positioned at ``wall_matrix`` with the supplied length, height, and
    extrusion angle. The IFC axis is taken to start at wall-local X=0 and
    extend to X=``length``. ``host_present=False`` makes the chain return
    None partway through."""
    wall_obj = mock.Mock(name="WallObj")
    wall_obj.matrix_world = wall_matrix
    host_wall = mock.Mock(name="IfcWall") if host_present else None
    return mock.patch.multiple(
        subject.tool,
        Ifc=mock.MagicMock(
            spec=subject.tool.Ifc,
            get_entity=mock.Mock(return_value=mock.Mock(name="IfcDoor")),
            get_object=mock.Mock(return_value=wall_obj if host_present else None),
        ),
        Spatial=mock.MagicMock(
            spec=subject.tool.Spatial,
            get_host_wall=mock.Mock(return_value=host_wall),
        ),
        Wall=mock.MagicMock(
            spec=subject.tool.Wall,
            get_length_and_height=mock.Mock(return_value=(length, height) if host_present else None),
            get_axis_local_extent=mock.Mock(return_value=(0.0, length) if host_present else None),
            get_x_angle=mock.Mock(return_value=x_angle if host_present else None),
        ),
        Parametric=mock.MagicMock(
            spec=subject.tool.Parametric,
            get_geom_generation=mock.Mock(return_value=geom_gen),
        ),
    )


# ----------------------------------------------------------------------
# Visibility predicate
# ----------------------------------------------------------------------


def test_has_host_wall_returns_true_when_chain_resolves():
    props, _ = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        assert subject.has_host_wall(props) is True


def test_has_host_wall_returns_false_when_no_host():
    props, _ = _make_props(Matrix.Identity(4))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0, host_present=False):
        assert subject.has_host_wall(props) is False


def test_has_host_wall_returns_true_for_slanted_wall():
    """Slanted LAYER2 walls keep ``matrix_world`` upright — the slope lives in
    the IFC extrusion direction and in the wall mesh vertices, not in the
    object transform. So wall-local Z still equals world Z, the offset math
    round-trips, and the gizmos must remain visible."""
    import math

    props, _ = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0, x_angle=math.radians(15)):
        assert subject.has_host_wall(props) is True


# ----------------------------------------------------------------------
# Compute helpers (un-flipped filling, wall at world origin)
# ----------------------------------------------------------------------


def test_get_wall_offset_left_for_filling_at_known_x():
    """Wall span 0→5 on X; filling origin at wall-local X=1.5 with +X aligned.
    Filling's left edge is at wall-X 1.5 → offset_left = 1.5."""
    props, _ = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        assert subject._get_offset(props, subject._LEFT) == pytest.approx(1.5)


def test_get_wall_offset_right_complements_left_plus_width():
    """offset_left + overall_width + offset_right == wall length."""
    props, _ = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        left = subject._get_offset(props, subject._LEFT)
        right = subject._get_offset(props, subject._RIGHT)
    assert left + props.overall_width + right == pytest.approx(5.0)


def test_get_wall_offset_bottom_for_filling_at_sill_height():
    """Wall base at world Z=0; filling origin at wall-local Z=0.5 → sill at 0.5 m."""
    props, _ = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        assert subject._get_offset(props, subject._BOTTOM) == pytest.approx(0.5)


def test_get_wall_offset_top_complements_bottom_plus_height():
    """offset_bottom + overall_height + offset_top == wall height."""
    props, _ = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        bottom = subject._get_offset(props, subject._BOTTOM)
        top = subject._get_offset(props, subject._TOP)
    assert bottom + props.overall_height + top == pytest.approx(3.0)


# ----------------------------------------------------------------------
# Slanted wall (LAYER2): wall ``matrix_world`` stays upright, so the
# offset math is the same as for a vertical wall. Pinning this guards
# against the visibility gate being re-added or the math diverging.
# ----------------------------------------------------------------------


def test_get_wall_offset_bottom_for_slanted_wall():
    """For a LAYER2 slanted wall the wall matrix is identity rotation — sill
    height read in the wall's local Z is still the world Z above the wall
    base."""
    import math

    props, _ = _make_props(Matrix.Translation((1.5, 0.0, 0.9)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0, x_angle=math.radians(15)):
        assert subject._get_offset(props, subject._BOTTOM) == pytest.approx(0.9)


def test_set_wall_offset_bottom_round_trips_for_slanted_wall():
    """Round-trip on a slanted wall: setting then reading the bottom offset
    yields the input. The apply path translates along the wall's local Z
    direction in world space (``matrix_world.to_3x3().col[2]``), which equals
    world Z for an upright wall matrix regardless of IFC slope."""
    import math

    props, _ = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0, x_angle=math.radians(15)):
        subject._set_offset(props, subject._BOTTOM, 1.2)
        assert subject._get_offset(props, subject._BOTTOM) == pytest.approx(1.2)


# ----------------------------------------------------------------------
# Flipped filling (180° around Z) — add-opening flow flips a filling that
# lands on the wall's opposite face. Offset arithmetic must still report
# the leftmost/rightmost edges in wall coordinates, not in filling coordinates.
# ----------------------------------------------------------------------


def test_get_wall_offset_left_handles_flipped_filling():
    """Flipped filling at wall-local X=1.5: filling extends from X=1.5 in filling's +X
    direction, which is wall's -X. So filling's leftmost edge in wall coords is
    at wall-X 0.5, not wall-X 1.5."""
    filling_matrix = Matrix.Translation((1.5, 0.0, 0.5)) @ Matrix.Rotation(pi, 4, "Z")
    props, _ = _make_props(filling_matrix, overall_width=1.0)
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        assert subject._get_offset(props, subject._LEFT) == pytest.approx(0.5)


def test_get_wall_offset_right_handles_flipped_filling():
    """Same flipped filling — filling's rightmost edge in wall coords is at the
    filling origin (wall-X 1.5), so offset_right = wall_length - 1.5 = 3.5."""
    filling_matrix = Matrix.Translation((1.5, 0.0, 0.5)) @ Matrix.Rotation(pi, 4, "Z")
    props, _ = _make_props(filling_matrix, overall_width=1.0)
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        assert subject._get_offset(props, subject._RIGHT) == pytest.approx(3.5)


# ----------------------------------------------------------------------
# Apply helpers — must round-trip with the compute helpers.
# ----------------------------------------------------------------------


def test_set_wall_offset_left_translates_filling_along_wall_x():
    """Setting left-offset to 2.0 (from 1.5) shifts the filling origin by +0.5
    along the wall's local X axis."""
    props, filling_obj = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        subject._set_offset(props, subject._LEFT, 2.0)
    assert filling_obj.matrix_world.translation.x == pytest.approx(2.0)
    assert filling_obj.matrix_world.translation.z == pytest.approx(0.5)


def test_set_wall_offset_bottom_translates_filling_along_wall_z():
    """Setting bottom-offset to 1.0 (from 0.5) shifts the filling origin by +0.5
    along the wall's local Z axis."""
    props, filling_obj = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        subject._set_offset(props, subject._BOTTOM, 1.0)
    assert filling_obj.matrix_world.translation.z == pytest.approx(1.0)
    assert filling_obj.matrix_world.translation.x == pytest.approx(1.5)


def test_set_wall_offset_right_round_trips_with_get():
    """The right-edge setter is the symmetric pair of the left-edge setter —
    they must produce mutually consistent geometry, otherwise pulling the
    right edge would silently desync the left."""
    props, _ = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        subject._set_offset(props, subject._RIGHT, 1.0)
        result = subject._get_offset(props, subject._RIGHT)
    assert result == pytest.approx(1.0)


def test_set_wall_offset_top_round_trips_with_get():
    """Same round-trip invariant for the top edge."""
    props, _ = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        subject._set_offset(props, subject._TOP, 0.25)
        result = subject._get_offset(props, subject._TOP)
    assert result == pytest.approx(0.25)


# ----------------------------------------------------------------------
# Cache invalidation
# ----------------------------------------------------------------------


def test_geom_cache_invalidates_when_generation_bumps():
    """The cache must reset when ``tool.Parametric.get_geom_generation()``
    advances so IFC mutations don't leave stale host-wall reads in memory."""
    props, _ = _make_props(Matrix.Translation((1.0, 0.0, 0.0)))
    # Patch get_geom_generation on the real class — the cache binds to the class
    # at definition time, so a mock.patch.multiple on subject.tool.Parametric
    # would be invisible to it.
    from bonsai.tool.parametric import Parametric

    with mock.patch.object(Parametric, "get_geom_generation", return_value=1):
        with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
            first = subject._get_offset(props, subject._LEFT)
    with mock.patch.object(Parametric, "get_geom_generation", return_value=2):
        with _patch_host_wall(Matrix.Identity(4), length=8.0, height=3.0):
            right_after_bump = subject._get_offset(props, subject._RIGHT)
    assert first == pytest.approx(1.0)
    # 8 m wall, filling at x=1, width 1 → right offset = 6. Reads 6 only if the
    # cache dropped on the generation bump.
    assert right_after_bump == pytest.approx(6.0)


# ----------------------------------------------------------------------
# Signed value the gizmo reports for left/right (sign-flip on filling's 180° Z rotation)
#
# Without the sign flip the dim arrow renders in the wrong world direction
# for a filling whose local +X is opposite the wall's local +X. The gizmo
# system flips its rendered dim arrow 180° around Z whenever the reported
# value is negative, so the unflipped/flipped cases produce mirrored signs
# and the arrow ends up pointing the right way visually in both orientations.
# ----------------------------------------------------------------------


def test_left_signed_value_positive_for_unflipped_filling():
    props, _ = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        assert subject._compute_value(props, subject._LEFT) == pytest.approx(1.5)


def test_left_signed_value_negative_for_flipped_filling():
    """Filling rotated 180° around Z: its leftmost edge (in wall coords) sits
    at wall-X 0.5, so the user-facing left offset is 0.5 — but the signed
    value must be -0.5 so the gizmo flips its rendered arrow 180° around Z."""
    from math import pi

    filling = Matrix.Translation((1.5, 0.0, 0.5)) @ Matrix.Rotation(pi, 4, "Z")
    props, _ = _make_props(filling, overall_width=1.0)
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        assert subject._compute_value(props, subject._LEFT) == pytest.approx(-0.5)


def test_right_signed_value_positive_for_unflipped_filling():
    props, _ = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        assert subject._compute_value(props, subject._RIGHT) == pytest.approx(2.5)


def test_right_signed_value_negative_for_flipped_filling():
    from math import pi

    filling = Matrix.Translation((1.5, 0.0, 0.5)) @ Matrix.Rotation(pi, 4, "Z")
    props, _ = _make_props(filling, overall_width=1.0)
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        assert subject._compute_value(props, subject._RIGHT) == pytest.approx(-3.5)


# ----------------------------------------------------------------------
# Matrix-position anchors at the wall edge (visual: arrow tail at wall,
# head at filling). The position is in filling-local frame so that mw @ pos
# lands at the wall edge in world.
# ----------------------------------------------------------------------


def test_left_offset_position_lands_at_wall_start_in_world():
    """For an unflipped filling at wall-local (1.5, 0, 0.5) with the wall at the
    world origin (bound_box.min_x=0), the matrix_position transformed by the
    filling's world matrix must land at world (0, 0, mid_height)."""
    props, filling_obj = _make_props(Matrix.Translation((1.5, 0.0, 0.5)), overall_height=2.0)
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        pos_filling_local = subject._edge_position(props, subject._LEFT)
        pos_world = filling_obj.matrix_world @ pos_filling_local
    # Wall's start at world X=0 (bound_box.min_x=0 in the patched wall).
    assert pos_world.x == pytest.approx(0.0)


def test_top_offset_position_lands_at_wall_top_in_world():
    """The top arrow anchors at wall-top — filling-local Z must equal
    ``overall_height + top_offset`` so the mw-multiplied point lands on the
    wall's top edge at world height."""
    props, filling_obj = _make_props(Matrix.Translation((1.5, 0.0, 0.5)), overall_height=2.0)
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        pos_filling_local = subject._edge_position(props, subject._TOP)
        pos_world = filling_obj.matrix_world @ pos_filling_local
    # Wall height 3.0, wall base at world Z=0 → wall top at world Z=3.
    assert pos_world.z == pytest.approx(3.0)


def test_bottom_offset_position_lands_at_wall_base_in_world():
    """Same idea for the bottom anchor — filling-local Z = ``-bottom_offset``
    so the point lands at world Z=0 (the wall's base)."""
    props, filling_obj = _make_props(Matrix.Translation((1.5, 0.0, 0.5)), overall_height=2.0)
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        pos_filling_local = subject._edge_position(props, subject._BOTTOM)
        pos_world = filling_obj.matrix_world @ pos_filling_local
    assert pos_world.z == pytest.approx(0.0)


def test_apply_value_takes_absolute_value():
    """Apply lambdas use ``abs(v)`` so the apply path stays correct even when
    the compute side returned a negative signed value (flipped filling)."""
    props, filling_obj = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        # Simulate the gizmo handing back a negative value (flipped-filling scenario).
        # The user-facing offset is +2.0, the filling must end up at wall-X=2.0.
        left_cfg = next(c for c in subject.WALL_OFFSET_GIZMO_CONFIGS if c.attr_name == "host_wall_offset_left")
        left_cfg.apply_value(props, -2.0)
    assert filling_obj.matrix_world.translation.x == pytest.approx(2.0)


def test_clear_caches_drops_all_entries():
    """The ``load_post`` handler calls ``clear_caches`` so a fresh file
    doesn't inherit stale entries from the previous one. Pin the contract."""
    props, _ = _make_props(Matrix.Translation((1.0, 0.0, 0.0)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        subject._get_offset(props, subject._LEFT)
    assert subject._GEOM_CACHE._data
    subject.clear_caches()
    assert not subject._GEOM_CACHE._data


# ----------------------------------------------------------------------
# Stale-cache edge cases — cache keys are Blender object names, invalidated
# only by parametric generation bumps and ``load_post``. Anything that
# changes scene state without bumping the generation (Blender rename,
# external Python script deleting a wall) leaves the cache holding stale
# entries until the next IFC mutation. These tests pin that behavior.
# ----------------------------------------------------------------------


def test_filling_rename_within_session_reads_correctly_under_new_name():
    """Reading offsets after a Blender rename hits a cache miss under the
    new name and recomputes — the old-name entry is leaked but harmless,
    and the new-name read returns correct geometry."""
    props, filling_obj = _make_props(Matrix.Translation((1.5, 0.0, 0.5)), name="Door1")
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        first = subject._get_offset(props, subject._LEFT)
        assert "Door1" in subject._GEOM_CACHE._data
        filling_obj.name = "Door1_renamed"
        second = subject._get_offset(props, subject._LEFT)
    assert first == pytest.approx(1.5)
    assert second == pytest.approx(1.5)
    assert "Door1_renamed" in subject._GEOM_CACHE._data


def test_host_wall_deletion_serves_stale_cache_until_invalidation():
    """If the host wall is removed without bumping the generation counter
    (e.g. external script), the cache keeps returning the pre-deletion
    geometry — only an IFC mutation or ``clear_caches()`` drops the stale
    entry."""
    props, _ = _make_props(Matrix.Translation((1.5, 0.0, 0.5)))
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        assert subject.has_host_wall(props) is True
    # Even after the patch exits and the chain would now return None, the
    # cached entry under the filling's name is still served.
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0, host_present=False):
        assert subject.has_host_wall(props) is True  # stale
        subject.clear_caches()
        assert subject.has_host_wall(props) is False  # recomputed


def test_filling_rotated_90_degrees_in_wall_plane_falls_back_to_positive_sign():
    """A filling rotated exactly 90° around Z has ``col[0].x == 0.0``, which
    is the ambiguous boundary for the X-sign. The implementation falls back
    to +1 (the ``>= 0.0`` branch), so the renderer-side value reads as
    positive — same sign as an unflipped filling."""
    filling_matrix = Matrix.Translation((1.5, 0.0, 0.5)) @ Matrix.Rotation(pi / 2, 4, "Z")
    props, _ = _make_props(filling_matrix, overall_width=1.0)
    with _patch_host_wall(Matrix.Identity(4), length=5.0, height=3.0):
        signed = subject._compute_value(props, subject._LEFT)
    # +1 fallback × unflipped-equivalent left offset = +1.5 (filling origin in wall coords).
    assert signed == pytest.approx(1.5)
