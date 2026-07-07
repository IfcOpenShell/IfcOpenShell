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

"""Unit tests for the pipe/duct segment parametric-edit scaffolding.

Covers three surfaces that ship together as the first MEP dimension-gizmo
feature:

- ``tool.Parametric.is_pipe_segment`` / ``is_duct_segment`` predicates
  (registry contract — must be total).
- ``_segment_world_length`` / ``_preview_segment_via_scale`` /
  ``_restore_segment_scale`` pure helpers driving the live preview.
- ``GizmoPipeSegmentEdition`` / ``GizmoDuctSegmentEdition`` class wiring
  (bl_idname, operator bindings, dimension_gizmo_props, is_element_type).

Full operator round-trips (enable → drag → finish → IFC commit) need a real
Blender + IFC scene and are deferred to a later integration session."""

from unittest.mock import Mock, patch

import bpy
import ifcopenshell
import pytest
from mathutils import Matrix, Vector

pytestmark = pytest.mark.model


# ---------------------------------------------------------------------------
# Predicates — total over arbitrary IFC entity input
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "ifc_class,is_pipe_expected,is_duct_expected",
    [
        ("IfcPipeSegment", True, False),
        ("IfcDuctSegment", False, True),
        ("IfcFlowSegment", False, False),  # base class — neither pipe nor duct alone
        ("IfcPipeFitting", False, False),  # fitting, not a segment
        ("IfcDuctFitting", False, False),
        ("IfcWall", False, False),
        ("IfcAnnotation", False, False),  # bare schema element with no MEP semantics
    ],
)
def test_is_pipe_or_duct_segment_predicate_truth_table(ifc_class, is_pipe_expected, is_duct_expected):
    """The two predicates must classify every IFC class correctly AND
    return False (not raise) on classes that have nothing to do with MEP.
    Pinned alongside the registry-wide predicate-totality test so a
    regression in either direction surfaces in this file too."""
    from bonsai import tool

    probe = ifcopenshell.file(schema="IFC4").create_entity(ifc_class)
    assert tool.Parametric.is_pipe_segment(probe) is is_pipe_expected
    assert tool.Parametric.is_duct_segment(probe) is is_duct_expected


# ---------------------------------------------------------------------------
# _segment_world_length — pure geometric helper
# ---------------------------------------------------------------------------


def test_segment_world_length_returns_axis_magnitude():
    """The length read here drives both the dimension gizmo's display and
    the snap_length captured on enable. Pin the math on a known axis."""
    from bonsai.bim.module.model.mep import _segment_world_length

    fake_obj = object()
    axis = (Vector((1.0, 2.0, 3.0)), Vector((1.0, 2.0, 5.5)))
    with patch("bonsai.tool.Model.get_flow_segment_axis", return_value=axis):
        assert _segment_world_length(fake_obj) == pytest.approx(2.5)


# ---------------------------------------------------------------------------
# Preview helpers — obj.scale.z manipulation
# ---------------------------------------------------------------------------


class _FakeObj:
    """Stand-in for bpy.types.Object exposing only ``scale`` — enough for
    the preview helpers, which never touch IFC."""

    def __init__(self):
        self.scale = Vector((1.0, 1.0, 1.0))


def test_preview_segment_via_scale_sets_z_to_ratio():
    """The visible-stretch ratio composes ``props_length / mesh_local_length`` where
    ``mesh_local_length = snap_length / snap_object_scale_z``."""
    from bonsai.bim.module.model.mep import _preview_segment_via_scale

    obj = _FakeObj()
    _preview_segment_via_scale(obj, props_length=2.0, snap_length=1.0, snap_object_scale_z=1.0)
    assert obj.scale.z == pytest.approx(2.0)

    _preview_segment_via_scale(obj, props_length=0.5, snap_length=1.0, snap_object_scale_z=1.0)
    assert obj.scale.z == pytest.approx(0.5)


def test_preview_segment_via_scale_floors_at_min_value():
    """``props.length`` is clamped at FloatProperty min=0.01; the helper still
    defends against zero / negative so a runaway value can't invert the segment."""
    from bonsai.bim.module.model.mep import _preview_segment_via_scale

    obj = _FakeObj()
    _preview_segment_via_scale(obj, props_length=0.0, snap_length=1.0, snap_object_scale_z=1.0)
    assert obj.scale.z == pytest.approx(0.01)


def test_preview_segment_via_scale_skips_when_snap_is_zero():
    """A zero ``snap_length`` would divide by zero — helper skips silently."""
    from bonsai.bim.module.model.mep import _preview_segment_via_scale

    obj = _FakeObj()
    obj.scale.z = 3.0
    _preview_segment_via_scale(obj, props_length=1.0, snap_length=0.0, snap_object_scale_z=1.0)
    # No change.
    assert obj.scale.z == pytest.approx(3.0)


def test_restore_segment_scale_resets_z_to_target():
    """Pin that the reset only touches Z; X/Y stay whatever the user set."""
    from bonsai.bim.module.model.mep import _restore_segment_scale_to

    obj = _FakeObj()
    obj.scale = Vector((0.5, 0.7, 4.2))
    _restore_segment_scale_to(obj, 1.0)
    assert obj.scale.x == pytest.approx(0.5)
    assert obj.scale.y == pytest.approx(0.7)
    assert obj.scale.z == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Gizmo group class wiring — registration and config
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "gizmo_cls_name,bl_idname,is_element_predicate",
    [
        ("GizmoPipeSegmentEdition", "OBJECT_GGT_bim_pipe_segment_edition", "is_pipe_segment"),
        ("GizmoDuctSegmentEdition", "OBJECT_GGT_bim_duct_segment_edition", "is_duct_segment"),
    ],
)
def test_gizmo_group_class_wiring(gizmo_cls_name, bl_idname, is_element_predicate):
    """Each gizmo group must:
    - declare the expected ``bl_idname`` (so it actually registers under that name);
    - have the matching ``is_element_type`` delegate to the right predicate
      (so it polls in for the right IFC class).
    """
    from bonsai import tool
    from bonsai.bim.module.model import mep

    cls = getattr(mep, gizmo_cls_name)
    assert cls.bl_idname == bl_idname
    predicate = getattr(tool.Parametric, is_element_predicate)
    fake_element = Mock()
    fake_element.is_a.return_value = True
    with (
        patch.object(tool.Parametric, is_element_predicate, side_effect=predicate) as p,
        patch.object(tool.System, "has_parametric_body", return_value=True),
    ):
        cls.is_element_type(fake_element)
    assert p.called, f"{gizmo_cls_name}.is_element_type did not delegate to Parametric.{is_element_predicate}"


@pytest.mark.parametrize(
    "gizmo_cls_name,enable_op,finish_op,cancel_op",
    [
        (
            "GizmoPipeSegmentEdition",
            "bim.enable_editing_pipe_segment",
            "bim.finish_editing_pipe_segment",
            "bim.cancel_editing_pipe_segment",
        ),
        (
            "GizmoDuctSegmentEdition",
            "bim.enable_editing_duct_segment",
            "bim.finish_editing_duct_segment",
            "bim.cancel_editing_duct_segment",
        ),
    ],
)
def test_gizmo_lifecycle_bindings_reference_registered_operators(gizmo_cls_name, enable_op, finish_op, cancel_op):
    """Catches the silent-regression where the gizmo's enable/finish/cancel
    string drifts away from the actual operator ``bl_idname``."""
    from bonsai.bim.module.model import mep

    cls = getattr(mep, gizmo_cls_name)
    assert cls.enable_editing_operator == enable_op
    assert cls.finish_editing_operator == finish_op
    assert cls.cancel_editing_operator == cancel_op
    # And the operators are actually registered.
    for op in (enable_op, finish_op, cancel_op):
        namespace, _, verb = op.partition(".")
        assert hasattr(
            getattr(bpy.ops, namespace), verb
        ), f"{gizmo_cls_name} references {op!r} which is not a registered operator"


@pytest.mark.parametrize("gizmo_cls_name", ["GizmoPipeSegmentEdition", "GizmoDuctSegmentEdition"])
def test_gizmo_dimension_gizmo_props_has_single_length_entry(gizmo_cls_name):
    """Phase 1 ships a single dimension (segment length). Pin the shape so
    a Phase 2 addition (diameter / width / height) is an intentional
    expansion rather than a drive-by edit."""
    from bonsai.bim.module.drawing.gizmos import DimensionGizmoConfig
    from bonsai.bim.module.model import mep

    cls = getattr(mep, gizmo_cls_name)
    assert len(cls.dimension_gizmo_props) == 1
    config = cls.dimension_gizmo_props[0]
    assert isinstance(config, DimensionGizmoConfig)
    assert config.attr_name == "length"
    assert tuple(config.axis) == (0, 0, 1)
    assert config.min_value == pytest.approx(0.01)


@pytest.mark.parametrize("gizmo_cls_name", ["GizmoPipeSegmentEdition", "GizmoDuctSegmentEdition"])
def test_length_dimension_has_matrix_position_so_rotation_is_respected(gizmo_cls_name):
    """Regression guard for "edit-mode length dimension doesn't take local
    object rotation". Without ``matrix_position`` set, ``update_dimension_gizmos``
    falls back to ``base_matrix = Identity`` and the gizmo's intrinsic +X
    visual line is never rotated to the configured ``axis`` — the dimension
    renders perpendicular to the segment on a rotated pipe. Setting
    ``matrix_position`` (even to ``(0, 0, 0)``) routes through
    ``compose_gizmo_matrix`` which applies ``get_axis_rotation_matrix(axis)``
    so the line aligns with the segment's local +Z (extrusion axis) in
    world space."""
    from bonsai.bim.module.model import mep

    cls = getattr(mep, gizmo_cls_name)
    config = cls.dimension_gizmo_props[0]
    assert config.matrix_position is not None, (
        f"{gizmo_cls_name} length dimension is missing matrix_position — the gizmo will "
        "render along the object's local +X axis instead of the segment's local +Z."
    )


# ---------------------------------------------------------------------------
# Extend-to-cursor — operator + element-specific gizmo wiring
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "gizmo_cls_name,extend_operator",
    [
        ("GizmoPipeSegmentEdition", "bim.extend_pipe_segment_to_cursor"),
        ("GizmoDuctSegmentEdition", "bim.extend_duct_segment_to_cursor"),
    ],
)
def test_extend_operator_binding(gizmo_cls_name, extend_operator):
    """Each segment gizmo group must reference the matching extend operator
    AND that operator must actually be registered. Catches the silent
    regression where someone renames the extend bl_idname without updating
    the gizmo group's ``_extend_operator`` class attribute."""
    from bonsai.bim.module.model import mep

    cls = getattr(mep, gizmo_cls_name)
    assert cls._extend_operator == extend_operator
    namespace, _, verb = extend_operator.partition(".")
    assert hasattr(
        getattr(bpy.ops, namespace), verb
    ), f"{gizmo_cls_name} references {extend_operator!r} which is not a registered operator"


@pytest.mark.parametrize("feature_attr", ["pipe_segment", "duct_segment"])
def test_gizmo_preferences_field_exists(feature_attr):
    """``GizmoPreferences`` must carry pipe_segment + duct_segment PointerProperties
    so ``get_gizmo_prefs()`` on the MEP gizmo groups resolves to a real PropertyGroup."""
    import bonsai.bim.ui as ui

    assert feature_attr in ui.GizmoPreferences.__annotations__, (
        f"GizmoPreferences is missing the {feature_attr} PointerProperty; "
        f"MEP gizmo groups' get_gizmo_prefs() would raise AttributeError."
    )


# ---------------------------------------------------------------------------
# Lifecycle operators are registered
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "op",
    [
        "bim.enable_editing_pipe_segment",
        "bim.finish_editing_pipe_segment",
        "bim.cancel_editing_pipe_segment",
        "bim.extend_pipe_segment_to_cursor",
        "bim.enable_editing_duct_segment",
        "bim.finish_editing_duct_segment",
        "bim.cancel_editing_duct_segment",
        "bim.extend_duct_segment_to_cursor",
    ],
)
def test_segment_operators_are_registered(op):
    """Smoke test mirroring ``test_parametric_registry``'s
    ``test_every_entry_has_enable_op_registered`` for the operators added
    in this round. Catches the silent regression where the classes tuple
    in ``__init__.py`` drops one of them."""
    namespace, _, verb = op.partition(".")
    assert hasattr(getattr(bpy.ops, namespace), verb), f"Operator {op!r} is not registered."


# ---------------------------------------------------------------------------
# MEPSegmentExtendPreviewDecorator._compute_extend_preview_line — pure helper
# ---------------------------------------------------------------------------


def test_extend_preview_line_returns_none_for_degenerate_segment():
    """A zero-length segment has no endpoint to draw from. Pin so a future
    refactor doesn't divide-by-zero or render a phantom line at the
    object origin."""
    from bonsai.bim.module.model.decorator import MEPSegmentExtendPreviewDecorator

    result = MEPSegmentExtendPreviewDecorator._compute_extend_preview_line(
        matrix_world=Matrix.Identity(4),
        cursor_world=Vector((0.0, 0.0, 1.0)),
        current_length=0.0,
    )
    assert result is None


def test_extend_preview_line_returns_none_when_cursor_at_current_end():
    """If the cursor projection matches the current segment length exactly,
    the extend operator would be a no-op — don't render the line either."""
    from bonsai.bim.module.model.decorator import MEPSegmentExtendPreviewDecorator

    result = MEPSegmentExtendPreviewDecorator._compute_extend_preview_line(
        matrix_world=Matrix.Identity(4),
        cursor_world=Vector((0.0, 0.0, 1.5)),
        current_length=1.5,
    )
    assert result is None


def test_extend_preview_line_renders_extension_when_cursor_past_end():
    """Happy path: cursor past current end → line runs from current end to
    the cursor's projected length. Identity matrix: local-Z maps 1:1 to
    world-Z. Pin the endpoints exactly."""
    from bonsai.bim.module.model.decorator import MEPSegmentExtendPreviewDecorator

    result = MEPSegmentExtendPreviewDecorator._compute_extend_preview_line(
        matrix_world=Matrix.Identity(4),
        cursor_world=Vector((0.0, 0.0, 3.0)),
        current_length=1.0,
    )
    assert result is not None
    start, end = result
    assert tuple(start) == pytest.approx((0.0, 0.0, 1.0))
    assert tuple(end) == pytest.approx((0.0, 0.0, 3.0))


def test_extend_preview_line_renders_trim_when_cursor_inside_segment():
    """Cursor inside the segment → line runs from current end BACK to the
    projected (shorter) length."""
    from bonsai.bim.module.model.decorator import MEPSegmentExtendPreviewDecorator

    result = MEPSegmentExtendPreviewDecorator._compute_extend_preview_line(
        matrix_world=Matrix.Identity(4),
        cursor_world=Vector((0.0, 0.0, 0.4)),
        current_length=1.0,
    )
    assert result is not None
    start, end = result
    assert tuple(start) == pytest.approx((0.0, 0.0, 1.0))
    assert tuple(end) == pytest.approx((0.0, 0.0, 0.4))


def test_extend_preview_line_follows_raw_projection_behind_segment_origin():
    """When the cursor's projected Z is negative (behind segment origin),
    the preview line must follow the raw cursor projection — the user is
    pointing somewhere and expects to see where, even though the operator
    would floor the actual commit. Matching the operator's clamp would
    hide the line whenever the cursor crossed the segment origin."""
    from bonsai.bim.module.model.decorator import MEPSegmentExtendPreviewDecorator

    result = MEPSegmentExtendPreviewDecorator._compute_extend_preview_line(
        matrix_world=Matrix.Identity(4),
        cursor_world=Vector((0.0, 0.0, -2.0)),
        current_length=1.0,
    )
    assert result is not None
    start, end = result
    assert tuple(start) == pytest.approx((0.0, 0.0, 1.0))
    assert tuple(end) == pytest.approx((0.0, 0.0, -2.0))


def test_extend_preview_line_respects_object_rotation():
    """A rotated segment (90° around Y) should produce world-space endpoints
    rotated accordingly. Pin so a future refactor doesn't drop the
    matrix_world multiplication."""
    import math

    from bonsai.bim.module.model.decorator import MEPSegmentExtendPreviewDecorator

    rotation = Matrix.Rotation(math.pi / 2, 4, "Y")
    result = MEPSegmentExtendPreviewDecorator._compute_extend_preview_line(
        matrix_world=rotation,
        cursor_world=Vector((3.0, 0.0, 0.0)),
        current_length=1.0,
    )
    assert result is not None
    start, end = result
    # local (0, 0, 1) rotated by 90° around Y → world (1, 0, 0).
    assert tuple(start) == pytest.approx((1.0, 0.0, 0.0), abs=1e-6)
    # local (0, 0, 3) rotated by 90° around Y → world (3, 0, 0).
    assert tuple(end) == pytest.approx((3.0, 0.0, 0.0), abs=1e-6)


# ---------------------------------------------------------------------------
# Lifecycle drift handling — Enable / Finish / Cancel must commit / restore
# matrix_world ↔ IFC ObjectPlacement at the appropriate lifecycle points.
# The AST forward-compat guard pins "a drift hook IS called somewhere"; these
# tests pin "the hook is called in the right branch with the right args."
# ---------------------------------------------------------------------------


def _make_segment_context(length=2.0, snap_length=2.0, scale_z=1.0):
    """Build (context, props, obj, element) fakes for the MEP edit-lifecycle bases.
    The bases access ``self.__class__._predicate`` / ``_props_getter`` so
    callers must instantiate a concrete test subclass and call
    ``instance._execute(context)`` rather than passing a Mock as ``self``."""
    obj = Mock(name="obj")
    obj.scale = Vector((1.0, 1.0, scale_z))
    element = Mock(name="element")
    props = Mock(name="props")
    props.length = length
    props.snap_length = snap_length
    props.snap_object_scale_z = scale_z
    props.mesh_dirty = False

    context = Mock(name="context")
    context.active_object = obj
    return context, props, obj, element


def _concrete_mep_mixin(props):
    """Build a concrete ``_MEPSegmentEditMixin`` subclass that bypasses the
    IFC predicate gate and returns the supplied ``props`` from ``_get_props``.
    The unified mixin replaced the three-base-class lifecycle pattern; tests now
    target the single mixin and override the two ParametricEditMixinBase
    hooks instead of class-level ``_predicate`` / ``_props_getter``."""
    from bonsai.bim.module.model.mep import _MEPSegmentEditMixin

    class _ConcreteMEPMixin(_MEPSegmentEditMixin):
        @classmethod
        def _is_element_type(cls, element):
            return True

        @classmethod
        def _get_props(cls, obj):
            return props

    return _ConcreteMEPMixin


def test_enable_pipe_segment_commits_pre_edit_placement_drift():
    """Enable must call ``commit_placement_if_moved(obj, apply_scale=False)``
    BEFORE ``_segment_world_length`` captures ``snap_length``. Without the
    commit, snap_length is read from a dragged matrix_world while the IFC
    ObjectPlacement is stale — Finish's set_depth would then write
    representation coords relative to the wrong origin."""
    context, props, obj, element = _make_segment_context()
    cls = _concrete_mep_mixin(props)

    with (
        patch("bonsai.bim.module.model.mep.tool") as mock_tool,
        patch("bonsai.bim.parametric_lifecycle.tool", mock_tool),
        patch("bonsai.bim.module.model.mep._segment_world_length", return_value=2.0),
    ):
        mock_tool.Ifc.get_entity.return_value = element
        cls()._enable_targets(context)

    mock_tool.Geometry.commit_placement_if_moved.assert_called_once_with(obj, apply_scale=False)


def test_finish_pipe_segment_commits_drift_when_no_length_change():
    """Finish without a length change must STILL commit matrix_world drift —
    the bug class that motivated this guard. The conditional ``set_depth``
    branch covers the length-changed path transitively; the unconditional
    ``commit_placement_if_moved`` after the if/else closes the silent-drop
    path."""
    # length == snap_length → no-op session.
    context, props, obj, element = _make_segment_context(length=2.0, snap_length=2.0)
    cls = _concrete_mep_mixin(props)

    with (
        patch("bonsai.bim.module.model.mep.tool") as mock_tool,
        patch("bonsai.bim.parametric_lifecycle.tool", mock_tool),
        patch("bonsai.bim.module.model.mep.DumbProfileJoiner") as mock_joiner,
        patch("bonsai.bim.module.model.mep._restore_segment_mesh_if_dirty"),
        patch("bonsai.bim.module.model.mep._restore_segment_scale_to"),
    ):
        mock_tool.Ifc.get_entity.return_value = element
        cls()._finish_targets(context)
        mock_joiner.return_value.set_depth.assert_not_called()  # no-length branch

    mock_tool.Geometry.commit_placement_if_moved.assert_called_once_with(obj)


def test_cancel_pipe_segment_delegates_to_restore_or_rebaseline():
    """Cancel must call ``tool.Geometry.restore_or_rebaseline_placement`` so
    matrix_world reverts in lockstep with the props draft. The helper owns
    the is_moved / ObjectPlacement gate."""
    context, props, obj, element = _make_segment_context()
    cls = _concrete_mep_mixin(props)

    with (
        patch("bonsai.bim.module.model.mep.tool") as mock_tool,
        patch("bonsai.bim.parametric_lifecycle.tool", mock_tool),
        patch("bonsai.bim.module.model.mep._restore_segment_mesh_if_dirty"),
    ):
        mock_tool.Ifc.get_entity.return_value = element
        cls()._cancel_targets(context)

    mock_tool.Geometry.restore_or_rebaseline_placement.assert_called_once_with(obj, element)
