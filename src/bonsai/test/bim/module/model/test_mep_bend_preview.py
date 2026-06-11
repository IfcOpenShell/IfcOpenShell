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

"""Unit tests for the bend-preview flow scaffolding.

Covers three surfaces:

1. ``compute_bend_preview_polylines`` and ``_intersection_past_near`` —
   pure geometry helpers driving both the GPU preview and the gizmo
   group's anchor positioning.
2. Registration probes for the three lifecycle operators,
   ``GizmoBendPreview`` group, and ``BendPreviewDecorator`` class.
3. ``FinishBendPreview``'s RuntimeError catch — when the dispatched
   ``bim.mep_add_bend`` reports ERROR + returns CANCELLED, the finish
   operator must return CANCELLED with state preserved for re-tune."""

from unittest.mock import MagicMock, Mock, patch

import bpy
import pytest

pytestmark = pytest.mark.model


# ---------------------------------------------------------------------------
# compute_bend_preview_polylines — pure geometry helper
# ---------------------------------------------------------------------------


def _mock_obj_with_axis(start_world, end_world):
    """Return (obj, (obj, axis_tuple)) — the second element is consumed by
    ``_with_axis_patches`` and makes ``tool.Model.get_flow_segment_axis(obj)``
    return the supplied axis. No real Blender object needed."""
    from mathutils import Vector

    obj = Mock()
    return obj, (obj, (Vector(start_world), Vector(end_world)))


def _with_axis_patches(*obj_axis_pairs):
    from bonsai import tool

    table = {id(obj): axis for obj, axis in obj_axis_pairs}
    return patch.object(tool.Model, "get_flow_segment_axis", side_effect=lambda o: table.get(id(o)))


def test_compute_bend_preview_polylines_invalid_for_parallel_axes():
    """Parallel axes have no defined intersection; ``MEPAddBend`` rejects
    them and the preview must too. Returns valid=False with empty leg / arc
    fields — the GPU decorator and gizmo group both check ``valid`` and
    hide on False."""
    from bonsai import tool
    from bonsai.bim.module.model.mep import compute_bend_preview_polylines

    start_obj, start_pair = _mock_obj_with_axis((0, 0, 0), (1, 0, 0))
    end_obj, end_pair = _mock_obj_with_axis((0, 1, 0), (1, 1, 0))

    with _with_axis_patches(start_pair, end_pair):
        with patch.object(tool.Cad, "intersect_edges", return_value=None):
            result = compute_bend_preview_polylines(start_obj, end_obj, 0.1, 0.1, 0.2)
    assert result["valid"] is False
    assert result["arc"] == []
    assert result["leg_a"] is None
    assert result["leg_b"] is None


def test_compute_bend_preview_polylines_returns_arc_and_leg_polylines_for_right_angle():
    """Two perpendicular segments meeting at origin → a 90° bend. Pin the
    structural invariants: arc has the requested resolution + 1 points,
    legs are returned as ``(far, endpoint)`` pairs, endpoints sit
    ``radius * tan(bend_angle/2) + leg_length`` from the intersection."""
    from math import isclose, pi, tan

    from mathutils import Vector

    from bonsai import tool
    from bonsai.bim.module.model.mep import compute_bend_preview_polylines

    start_obj, start_pair = _mock_obj_with_axis((1, 0, 0), (3, 0, 0))
    end_obj, end_pair = _mock_obj_with_axis((0, 1, 0), (0, 3, 0))

    intersection = (Vector((0, 0, 0)), Vector((0, 0, 0)))
    start_length, end_length, radius = 0.5, 0.5, 0.2
    bend_angle = pi / 2
    tangent_offset = radius * tan(bend_angle / 2)

    with _with_axis_patches(start_pair, end_pair):
        with patch.object(tool.Cad, "intersect_edges", return_value=intersection):
            with patch.object(
                tool.Cad,
                "closest_and_furthest_vectors",
                side_effect=lambda p, axis: (axis[0], axis[1]),
            ):
                result = compute_bend_preview_polylines(
                    start_obj, end_obj, start_length, end_length, radius, arc_resolution=12
                )

    assert result["valid"] is True
    leg_a_far, leg_a_endpoint = result["leg_a"]
    assert tuple(leg_a_far) == (3, 0, 0)
    assert isclose(leg_a_endpoint.x, tangent_offset + start_length, abs_tol=1e-6)
    assert isclose(leg_a_endpoint.y, 0.0, abs_tol=1e-6)

    leg_b_far, leg_b_endpoint = result["leg_b"]
    assert tuple(leg_b_far) == (0, 3, 0)
    assert isclose(leg_b_endpoint.x, 0.0, abs_tol=1e-6)
    assert isclose(leg_b_endpoint.y, tangent_offset + end_length, abs_tol=1e-6)

    assert len(result["arc"]) == 13
    arc = result["arc"]
    assert isclose((arc[0] - Vector((tangent_offset, 0, 0))).length, 0.0, abs_tol=1e-6)
    assert isclose((arc[-1] - Vector((0, tangent_offset, 0))).length, 0.0, abs_tol=1e-6)


def test_compute_bend_preview_polylines_invalid_for_near_collinear():
    """Near-collinear axes (intersection exists but bend angle ≈ 0 or π)
    short-circuit to valid=False so the preview doesn't render a
    degenerate near-zero-radius arc."""
    from mathutils import Vector

    from bonsai import tool
    from bonsai.bim.module.model.mep import compute_bend_preview_polylines

    start_obj, start_pair = _mock_obj_with_axis((1, 0, 0), (3, 0, 0))
    end_obj, end_pair = _mock_obj_with_axis((-1, 0, 0), (-3, 0, 0))
    intersection = (Vector((0, 0, 0)), Vector((0, 0, 0)))

    with _with_axis_patches(start_pair, end_pair):
        with patch.object(tool.Cad, "intersect_edges", return_value=intersection):
            with patch.object(
                tool.Cad,
                "closest_and_furthest_vectors",
                side_effect=lambda p, axis: (axis[0], axis[1]),
            ):
                result = compute_bend_preview_polylines(start_obj, end_obj, 0.1, 0.1, 0.2)
    assert result["valid"] is False


def test_compute_bend_preview_polylines_returns_invalid_axes_when_intersection_inside_segment():
    """When the intersection lands inside one of the segments, ``valid`` is
    False AND the result carries ``invalid_axes`` — a pair of (far_endpoint,
    intersection) lines for each segment. ``BendPreviewDecorator`` reads
    these to draw warning-red axes instead of rendering a degenerate arc."""
    from mathutils import Vector

    from bonsai import tool
    from bonsai.bim.module.model.mep import compute_bend_preview_polylines

    start_obj, start_pair = _mock_obj_with_axis((-3, 0, 0), (-1, 0, 0))
    end_obj, end_pair = _mock_obj_with_axis((0, 5, 0), (0, 3, 0))
    intersection = (Vector((-2, 0, 0)), Vector((-2, 0, 0)))

    with _with_axis_patches(start_pair, end_pair):
        with patch.object(tool.Cad, "intersect_edges", return_value=intersection):
            with patch.object(
                tool.Cad,
                "closest_and_furthest_vectors",
                # axis[0] = closer endpoint (near), axis[1] = farther (far).
                side_effect=lambda p, axis: (axis[1], axis[0]),
            ):
                result = compute_bend_preview_polylines(start_obj, end_obj, 0.1, 0.1, 0.2)

    assert result["valid"] is False
    assert "invalid_axes" in result, "preview must return invalid_axes for the warning decorator"
    axes = result["invalid_axes"]
    assert len(axes) == 2
    for _far_endpoint, axis_end in axes:
        assert tuple(axis_end) == (-2, 0, 0)
    assert result.get("reason") in ("intersection_inside_start", "intersection_inside_end")


# ---------------------------------------------------------------------------
# _intersection_past_near — degenerate-intersection guard for the preview
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "intersection,near,far,expected",
    [
        # Normal: intersection past near, opposite side from far.
        ((0, 0, 0), (-1, 0, 0), (-3, 0, 0), True),
        # Degenerate: intersection BETWEEN near and far (inside the segment).
        ((-2, 0, 0), (-1, 0, 0), (-3, 0, 0), False),
        # Degenerate: intersection past FAR (opposite side from the bend).
        ((-4, 0, 0), (-1, 0, 0), (-3, 0, 0), False),
        # Borderline: intersection coincides with near — within tolerance → False.
        ((-1, 0, 0), (-1, 0, 0), (-3, 0, 0), False),
        # Degenerate: zero-length segment — can't classify, False.
        ((0, 0, 0), (-1, 0, 0), (-1, 0, 0), False),
    ],
)
def test_intersection_past_near(intersection, near, far, expected):
    """Pins the degenerate-intersection classification used by
    ``compute_bend_preview_polylines`` to reject in-segment intersections."""
    from mathutils import Vector

    from bonsai.bim.module.model.mep import _intersection_past_near

    assert _intersection_past_near(Vector(intersection), Vector(near), Vector(far)) is expected


# ---------------------------------------------------------------------------
# Registration probes
# ---------------------------------------------------------------------------


def test_bend_preview_operators_are_registered():
    """The three bend-preview operators must resolve via ``bpy.ops.bim.*`` —
    enable populates scene props, finish dispatches ``bim.mep_add_bend``
    with the tuned params, cancel clears the state."""
    assert hasattr(bpy.ops.bim, "enable_bend_preview")
    assert hasattr(bpy.ops.bim, "finish_bend_preview")
    assert hasattr(bpy.ops.bim, "cancel_bend_preview")


def test_mep_join_segments_dispatcher_is_registered():
    """``bim.mep_join_segments`` is the discoverable entry point for the
    bend preview flow (F3 search → "Join MEP Segments") until the full
    gizmo-icon dispatch lands. Routes parallel → transition, non-parallel
    → enable_bend_preview."""
    assert hasattr(bpy.ops.bim, "mep_join_segments")


def test_bend_preview_gizmo_group_is_registered():
    """``GizmoBendPreview`` polls when ``scene.BIMPreviewProperties.bend.is_active``
    is True. Pin the bl_idname so a typo wouldn't silently hide the preview
    gizmos at runtime."""
    from bonsai.bim.module.model.mep_bend_preview import GizmoBendPreview

    assert GizmoBendPreview.bl_idname == "OBJECT_GGT_bim_bend_preview"
    assert issubclass(GizmoBendPreview, bpy.types.GizmoGroup)


def test_bim_bend_preview_properties_attached_to_scene():
    """The Scene PointerProperty must be bound in ``register()`` so the
    lifecycle operators and the GPU decorator can read
    ``context.scene.BIMPreviewProperties.bend.is_active``."""
    assert hasattr(bpy.types.Scene, "BIMPreviewProperties")
    assert hasattr(bpy.context.scene.BIMPreviewProperties, "bend")


def test_bend_preview_decorator_class_present():
    """The GPU decorator is installed at addon load (via
    ``bim/handler.py:load_post``). Verify the class exists with the
    install / uninstall interface the handler expects."""
    from bonsai.bim.module.model.decorator import BendPreviewDecorator

    assert hasattr(BendPreviewDecorator, "install")
    assert hasattr(BendPreviewDecorator, "uninstall")


def test_enable_bend_preview_from_bend_is_registered():
    """The re-edit entry point is discoverable via ``bpy.ops.bim`` so the
    pen-icon dispatch in ``GizmoMEPActions`` resolves at click time."""
    assert hasattr(bpy.ops.bim, "enable_bend_preview_from_bend")


def test_bim_bend_preview_properties_has_editing_bend_id():
    """The re-edit dispatch flag rides on the same preview PropertyGroup as
    the rest of the bend draft state. Without this field on the umbrella,
    re-edit cancel / commit cleanup would not zero it via
    ``clear_preview_state`` (which iterates ``*_id`` IntProperty fields)."""
    bend_props = bpy.context.scene.BIMPreviewProperties.bend
    assert hasattr(bend_props, "editing_bend_id")
    assert bend_props.editing_bend_id == 0


@pytest.mark.parametrize(
    "ifc_class,predefined_type,expected",
    [
        ("IfcFlowFitting", "BEND", True),
        ("IfcFlowFitting", "TRANSITION", False),
        ("IfcFlowFitting", "OBSTRUCTION", False),
        ("IfcFlowFitting", None, False),
        ("IfcFlowSegment", "BEND", False),
        ("IfcWall", "BEND", False),
    ],
)
def test_is_bend_fitting_predicate_truth_table(ifc_class, predefined_type, expected):
    """The predicate classifies each occurrence by walking up to its type's
    ``PredefinedType``. Pin the four-way branch: matching class + matching
    type, matching class + other type, wrong class, no type at all."""
    from unittest.mock import Mock

    from bonsai.bim.module.model.mep import _is_bend_fitting

    element = Mock()
    element.is_a = Mock(side_effect=lambda c: c == ifc_class)
    if predefined_type is None:
        element_type = None
    else:
        element_type = Mock()
        element_type.PredefinedType = predefined_type

    with patch("ifcopenshell.util.element.get_type", return_value=element_type):
        assert _is_bend_fitting(element) is expected


def test_is_bend_fitting_predicate_returns_false_on_none():
    """The predicate is total — callers pass it raw ``tool.Ifc.get_entity``
    results which can be ``None`` for unbound Blender objects, and the
    visibility-condition lambda must not raise from a gizmo poll."""
    from bonsai.bim.module.model.mep import _is_bend_fitting

    assert _is_bend_fitting(None) is False


# ---------------------------------------------------------------------------
# Finish-catches-RuntimeError contract
# ---------------------------------------------------------------------------


def test_finish_bend_preview_catches_runtime_error_from_dispatch():
    """When the dispatched ``bim.mep_add_bend`` reports ERROR + returns
    CANCELLED, ``bpy.ops`` promotes that to RuntimeError. Finish must catch
    it and return CANCELLED — propagating the exception leaves Blender's
    operator state half-broken. Preview state must remain active so the
    user can re-tune."""
    from types import SimpleNamespace

    from bonsai import tool
    from bonsai.bim.module.model.mep_bend_preview import FinishBendPreview

    class _Stand:
        def __init__(self):
            self.report = MagicMock()

    op_self = _Stand()
    fake_props = SimpleNamespace(
        is_active=True,
        start_segment_id=42,
        end_segment_id=43,
        start_length=0.1,
        end_length=0.1,
        radius=0.2,
        editing_bend_id=0,
    )
    context = SimpleNamespace(
        screen=MagicMock(),
        scene=SimpleNamespace(BIMPreviewProperties=SimpleNamespace(bend=fake_props)),
    )

    mock_ops_bim = MagicMock()
    mock_ops_bim.mep_add_bend.side_effect = RuntimeError("synthetic dispatch error")

    with (
        patch.object(tool.Ifc, "get", return_value=MagicMock(name="ifc_file")),
        patch.object(bpy.ops, "bim", new=mock_ops_bim),
    ):
        result = FinishBendPreview.execute(op_self, context)

    assert "CANCELLED" in result, "RuntimeError from dispatch must be converted to CANCELLED"
    assert fake_props.is_active is True, "failed dispatch must leave preview active for re-tune"
    op_self.report.assert_called()
