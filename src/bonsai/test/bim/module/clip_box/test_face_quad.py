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
#
# This file was generated with the assistance of an AI coding tool.

"""Tests for the generic face-quad gizmo core.

Pins the three contracts the layout helper depends on:

* ``compute_face_resize`` — pure one-sided resize arithmetic.
* ``front_facing_face_mask`` — view-aware face visibility predicate.
* ``apply_face_quad_layout`` — front-facing faces upload the solid
  unit quad ("solid" state); back-facing faces upload the halo strips
  ("strips" state).
"""

import pytest
from mathutils import Matrix, Vector

from bonsai.bim.module.clip_box import face_quad

pytestmark = pytest.mark.clip_box


# ---------------------------------------------------------------- compute_face_resize ---


class TestComputeFaceResize:
    def test_outward_drag_on_max_face_grows_half_extent_and_shifts_origin(self):
        # Pulling the +X face outward by 2.0 world units must:
        # - grow the world half by half the cursor delta (one-sided);
        # - shift the empty's origin so the opposite (-X) face stays put.
        new_scale, new_loc = face_quad.compute_face_resize(
            value=10.0 + 2.0,  # init + delta
            init_world_half=10.0,
            init_location=(0.0, 0.0, 0.0),
            world_axis=(1.0, 0.0, 0.0),
            display_size=1.0,
        )
        # half-extent: 10 + 2/2 = 11
        assert new_scale == pytest.approx(11.0)
        # origin shifts by half the realized delta (= 1.0) along +X
        assert new_loc[0] == pytest.approx(1.0)
        assert new_loc[1] == pytest.approx(0.0)
        assert new_loc[2] == pytest.approx(0.0)

    def test_inward_drag_clamps_at_minimum_half_extent(self):
        # Pulling the face inward by more than the current half collapses
        # to a tiny floor instead of going negative. The realized delta
        # (post-clamp) drives the location shift so the opposite face
        # stays fixed even at the clamp.
        new_scale, new_loc = face_quad.compute_face_resize(
            value=0.0,  # delta = -1.0
            init_world_half=1.0,
            init_location=(5.0, 0.0, 0.0),
            world_axis=(1.0, 0.0, 0.0),
            display_size=1.0,
        )
        assert new_scale > 0.0
        assert new_scale < 1.0
        # New origin sits between init (5.0) and -X face (which is at 4.0
        # = init.x - init_world_half). Since the clamp limited shrinkage,
        # the new origin is just slightly less than init.x.
        assert 4.0 < new_loc[0] < 5.0

    def test_drag_on_min_face_via_negative_world_axis_grows_outward(self):
        # On the -X face, ``world_axis`` is (-1, 0, 0). A positive
        # ``delta`` (outward on this face) must still grow the half
        # extent and shift the origin in the -X direction.
        new_scale, new_loc = face_quad.compute_face_resize(
            value=10.0 + 2.0,
            init_world_half=10.0,
            init_location=(0.0, 0.0, 0.0),
            world_axis=(-1.0, 0.0, 0.0),
            display_size=1.0,
        )
        assert new_scale == pytest.approx(11.0)
        # Origin shifts toward -X.
        assert new_loc[0] == pytest.approx(-1.0)

    def test_display_size_scales_the_resulting_scale_axis(self):
        # The returned scale is half_extent / display_size — so a
        # display_size of 2.0 halves the scale relative to display_size
        # of 1.0 for the same world half-extent.
        new_scale_1, _ = face_quad.compute_face_resize(
            value=10.0,
            init_world_half=10.0,
            init_location=(0.0, 0.0, 0.0),
            world_axis=(1.0, 0.0, 0.0),
            display_size=1.0,
        )
        new_scale_2, _ = face_quad.compute_face_resize(
            value=10.0,
            init_world_half=10.0,
            init_location=(0.0, 0.0, 0.0),
            world_axis=(1.0, 0.0, 0.0),
            display_size=2.0,
        )
        assert new_scale_1 == pytest.approx(10.0)
        assert new_scale_2 == pytest.approx(5.0)


# ----------------------------------------------------------- front_facing_face_mask ---


class TestFrontFacingFaceMask:
    def test_view_along_neg_z_lights_up_only_pos_z_face(self):
        # Camera looking down -Z (typical default front view): only the
        # +Z face (last entry) faces the camera.
        normals = (
            (-1.0, 0.0, 0.0),  # -X face
            (1.0, 0.0, 0.0),  # +X face
            (0.0, -1.0, 0.0),  # -Y face
            (0.0, 1.0, 0.0),  # +Y face
            (0.0, 0.0, -1.0),  # -Z face
            (0.0, 0.0, 1.0),  # +Z face
        )
        view_dir = (0.0, 0.0, -1.0)

        mask = face_quad.front_facing_face_mask(normals, view_dir)

        assert mask == (False, False, False, False, False, True)

    def test_view_along_pos_x_lights_up_neg_x_face(self):
        # Camera looking along +X (front of the -X face).
        normals = (
            (-1.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, -1.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, -1.0),
            (0.0, 0.0, 1.0),
        )
        view_dir = (1.0, 0.0, 0.0)

        mask = face_quad.front_facing_face_mask(normals, view_dir)

        assert mask == (True, False, False, False, False, False)

    def test_wrong_length_raises(self):
        with pytest.raises(ValueError, match="expected 6 face normals"):
            face_quad.front_facing_face_mask([(1.0, 0.0, 0.0), (-1.0, 0.0, 0.0)], (0.0, 0.0, -1.0))


# ----------------------------------------------------- apply_face_quad_layout (front/back) ---


class _FakeQuad:
    """Stand-in for ``BIM_GT_box_face_quad`` — only the slots the layout helper writes."""

    def __init__(self):
        self.matrix_basis = Matrix.Identity(4)
        self.axis = Vector((0.0, 0.0, 0.0))
        self.hide = False
        self.select_bias = 0.0
        self.is_highlight = False
        self.custom_shape = None
        self.custom_shape_select = None
        self._last_geometry_state = None
        self._strips_cache_key = None

    def new_custom_shape(self, kind, verts):
        # Layout helper only stores the result; nothing further is asked of it.
        return (kind, tuple(tuple(v) for v in verts))


class _FakeOutline:
    def __init__(self):
        self.matrix_basis = Matrix.Identity(4)
        self.alpha = 0.0
        self.alpha_highlight = 0.0


class _FakeRV3D:
    def __init__(self, view_rotation, view_matrix):
        self.view_rotation = view_rotation
        self.view_matrix = view_matrix
        # Blender's location_3d_to_region_2d reads perspective_matrix to
        # project world points; a simple ortho-projection matrix is enough
        # for the layout helper's halo-strip pixel measurement.
        self.perspective_matrix = view_matrix
        self.is_perspective = False


class _FakeRegion:
    width = 800
    height = 600


def _run_layout(view_dir: Vector) -> tuple[str, ...]:
    """Apply the layout helper for a unit cube at the origin with a
    given world-space view direction; return each route's
    ``_last_geometry_state`` in :data:`FACE_ROUTES` order."""
    quads = [_FakeQuad() for _ in range(6)]
    outlines = [_FakeOutline() for _ in range(6)]
    # view_rotation is the quaternion that rotates the camera's local
    # forward (-Z) onto the desired world view direction.
    view_rotation = Vector((0.0, 0.0, -1.0)).rotation_difference(view_dir.normalized())
    rv3d = _FakeRV3D(view_rotation, Matrix.Identity(4))
    face_quad.apply_face_quad_layout(
        quad_gizmos=quads,
        outline_gizmos=outlines,
        bmin=Vector((-1.0, -1.0, -1.0)),
        bmax=Vector((1.0, 1.0, 1.0)),
        matrix_world=Matrix.Identity(4),
        cage_rotation=Matrix.Identity(4),
        region=_FakeRegion(),
        rv3d=rv3d,
        locked=False,
    )
    return tuple(getattr(q, "_last_geometry_state", None) for q in quads)


class TestApplyFaceQuadLayout:
    def test_oblique_view_yields_solid_fronts_and_strips_or_empty_backs(self):
        # Oblique view direction (1, 1, -1) hits the box from the +X, +Y,
        # +Z octant. Faces facing toward the camera (-X, -Y, +Z) must
        # render as "solid"; faces facing away (+X, +Y, -Z) must render
        # as back-facing — either "strips" (when adjacent front faces
        # give halo edges) or "empty" (when no front-facing neighbour).
        states = _run_layout(view_dir=Vector((1.0, 1.0, -1.0)))

        # FACE_ROUTES order: (-X, +X, -Y, +Y, -Z, +Z)
        # Front-facing routes (against the view direction): -X, -Y, +Z
        assert states[0] == "solid"  # -X
        assert states[2] == "solid"  # -Y
        assert states[5] == "solid"  # +Z
        # Back-facing routes (with the view direction): +X, +Y, -Z
        for back_idx in (1, 3, 4):
            assert states[back_idx] in ("strips", "empty")

    def test_negative_scale_host_does_not_invert_front_back_split(self):
        # User-reported bug: when the host empty has scale=-1 on an axis,
        # the visible +X side of the cube sits on world +X (negative-scale
        # flips the local +X vertex onto world -X but the local -X vertex
        # onto world +X — same set of points). The OLD layout used the
        # signed matrix for positions while rotation-only for normals,
        # which placed the "+X face" gizmo on world -X. After the
        # ``_abs_scale_matrix`` fix the gizmo for the +X face must sit
        # at world +X for an outward-X-facing view to register it as
        # front-facing.
        quads = [_FakeQuad() for _ in range(6)]
        outlines = [_FakeOutline() for _ in range(6)]
        # View toward +X: the +X face is at world +X for a standard box.
        view_rotation = Vector((0.0, 0.0, -1.0)).rotation_difference(Vector((-1.0, 0.0, 0.0)))
        rv3d = _FakeRV3D(view_rotation, Matrix.Identity(4))
        # Negative X scale (mirroring the cube along world X).
        mw = Matrix.Diagonal((-1.0, 1.0, 1.0, 1.0))

        face_quad.apply_face_quad_layout(
            quad_gizmos=quads,
            outline_gizmos=outlines,
            bmin=Vector((-1.0, -1.0, -1.0)),
            bmax=Vector((1.0, 1.0, 1.0)),
            matrix_world=mw,
            cage_rotation=Matrix.Identity(4),
            region=_FakeRegion(),
            rv3d=rv3d,
            locked=False,
        )

        # Route 1 = (axis=0, is_max=True) = the +X face. Must be solid
        # (front-facing) for a +X-facing view, regardless of sign-of-scale.
        assert quads[1]._last_geometry_state == "solid"

    def test_view_parallel_front_face_remains_interactive(self):
        # Looking dead-on at +Z (view_dir = -Z): the +Z face sits
        # antiparallel to the view direction, so it's still the
        # front-facing face. It must render solid (clickable for both
        # the resize drag and the CTRL+click align-view dispatch),
        # never hidden — the older "lockout" treatment removed
        # CTRL+click access on the very face users most want to click.
        states = _run_layout(view_dir=Vector((0.0, 0.0, -1.0)))

        assert states[5] == "solid"  # +Z face (front-facing) stays interactive.
        # -Z face has no adjacent front-facing neighbours in this view,
        # so its halo strip degenerates to empty — but that's the
        # back-face path, not a deliberate lockout.
        assert states[4] == "empty"
