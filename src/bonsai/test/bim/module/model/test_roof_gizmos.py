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

"""Unit tests for the roof parametric gizmo group.

Covers the parts of ``GizmoRoofEdition`` that don't need a live Blender
viewport: the mode-conditional ``visibility_condition`` lambdas, the
slope ``compute_value`` / ``apply_value`` roundtrip, the
``CycleRoofGenerationMethod`` operator metadata + cycle behaviour, and
the ``_update_dimension_gizmo_positions`` override that anchors all three
dimension gizmos at the object's local origin."""

import math
from types import SimpleNamespace
from unittest.mock import patch

import bpy
import pytest

pytestmark = pytest.mark.model


def _get_config(attr_name):
    """Return the ``DimensionGizmoConfig`` for ``attr_name`` from the roof gizmo."""
    from bonsai.bim.module.model.roof import GizmoRoofEdition

    for cfg in GizmoRoofEdition.dimension_gizmo_props:
        if cfg.attr_name == attr_name:
            return cfg
    raise AssertionError(f"no DimensionGizmoConfig with attr_name={attr_name!r}")


# ----------------------------------------------------------------------------
# Mode-conditional visibility
# ----------------------------------------------------------------------------
#
# ``height`` and ``angle`` are mutually exclusive — exactly one is shown
# depending on ``generation_method``. ``roof_thickness`` applies regardless
# of the generation mode.


def test_height_gizmo_visible_only_in_height_mode():
    cfg = _get_config("height")
    assert cfg.visibility_condition(SimpleNamespace(generation_method="HEIGHT")) is True
    assert cfg.visibility_condition(SimpleNamespace(generation_method="ANGLE")) is False


def test_angle_gizmo_visible_only_in_angle_mode():
    cfg = _get_config("angle")
    assert cfg.visibility_condition(SimpleNamespace(generation_method="ANGLE")) is True
    assert cfg.visibility_condition(SimpleNamespace(generation_method="HEIGHT")) is False


def test_thickness_has_no_mode_gate():
    """Slab thickness applies to both generation modes — pinning
    ``visibility_condition is None`` guards against an accidental mode-gate
    being added later that would silently hide it when toggling modes."""
    assert _get_config("roof_thickness").visibility_condition is None


# ----------------------------------------------------------------------------
# Slope (angle) ↔ rise roundtrip
# ----------------------------------------------------------------------------
#
# The slope handle displays vertical rise at a fixed 1m run; dragging it
# updates ``props.angle`` via ``atan2(rise, run)``. Roundtrip preservation
# is the contract — feeding ``compute_value`` into ``apply_value`` must
# leave the angle unchanged (within float tolerance).


def test_slope_compute_value_returns_rise_at_reference_run():
    from bonsai.bim.module.model.roof import _ROOF_SLOPE_REFERENCE_RUN

    cfg = _get_config("angle")
    # 30° slope → rise = tan(30°) * 1m ≈ 0.5774 m
    props = SimpleNamespace(angle=math.radians(30))
    assert cfg.compute_value(props) == pytest.approx(math.tan(math.radians(30)) * _ROOF_SLOPE_REFERENCE_RUN)


def test_slope_apply_value_sets_angle_from_rise():
    from bonsai.bim.module.model.roof import _ROOF_SLOPE_REFERENCE_RUN

    cfg = _get_config("angle")
    props = SimpleNamespace(angle=0.0)
    cfg.apply_value(props, 0.5)
    assert props.angle == pytest.approx(math.atan2(0.5, _ROOF_SLOPE_REFERENCE_RUN))


def test_slope_roundtrip_preserves_angle():
    cfg = _get_config("angle")
    for deg in (5, 15, 30, 45, 60, 80):
        props = SimpleNamespace(angle=math.radians(deg))
        rise = cfg.compute_value(props)
        cfg.apply_value(props, rise)
        assert math.degrees(props.angle) == pytest.approx(deg, abs=1e-6)


def test_slope_apply_value_clamps_negative_to_zero():
    """A negative drag (rise < 0) must not produce a negative angle —
    ``atan2(-x, run)`` would yield a negative result, but ``apply_value``
    clamps to ``[0, pi/2 - 1e-3]`` so the roof never inverts."""
    cfg = _get_config("angle")
    props = SimpleNamespace(angle=math.radians(30))
    cfg.apply_value(props, -1.0)
    assert props.angle == 0.0


def test_slope_apply_value_clamps_at_near_vertical():
    """Slopes approaching 90° are clamped just below to avoid a vertical
    extrusion that would degenerate the bisect step in
    ``generate_hipped_roof_bmesh``."""
    from bonsai.bim.module.model.roof import _ROOF_MAX_SLOPE_ANGLE

    cfg = _get_config("angle")
    props = SimpleNamespace(angle=0.0)
    cfg.apply_value(props, 1e9)  # absurdly steep
    assert props.angle == pytest.approx(_ROOF_MAX_SLOPE_ANGLE)


# ----------------------------------------------------------------------------
# Cycle operator metadata
# ----------------------------------------------------------------------------
#
# ``CycleRoofGenerationMethod`` plugs into ``CycleTypeMixin`` so the
# HEIGHT ↔ ANGLE icon cycles through the two values. The mixin reads four
# class attributes to do its work; if any drift, the cycle no-ops or
# CANCELLED-loops in subtle ways. Pin them here.


def test_cycle_operator_class_metadata():
    from typing import get_args

    from bonsai import tool
    from bonsai.bim.module.model.roof import CycleRoofGenerationMethod

    assert CycleRoofGenerationMethod.bl_idname == "bim.cycle_roof_generation_method"
    assert CycleRoofGenerationMethod.element_checker == tool.Parametric.is_roof
    assert CycleRoofGenerationMethod.props_getter == tool.Model.get_roof_props
    assert CycleRoofGenerationMethod.type_attr == "generation_method"
    # The Literal resolves to ("HEIGHT", "ANGLE") — the mixin calls
    # ``get_args(type_literal)`` to enumerate the cycle.
    assert get_args(CycleRoofGenerationMethod.type_literal) == ("HEIGHT", "ANGLE")
    assert CycleRoofGenerationMethod.type_literal is tool.Model.RoofGenerationMethod


def test_cycle_operator_wired_on_gizmo_group():
    """The gizmo group's ``cycle_type_operator`` must match the bl_idname or
    the base class skips the cycle icon entirely (see gizmos.py:4987)."""
    from bonsai.bim.module.model.roof import CycleRoofGenerationMethod, GizmoRoofEdition

    assert GizmoRoofEdition.cycle_type_operator == CycleRoofGenerationMethod.bl_idname


def _cycle_stub_self(*, reverse: bool, props, element_is_target: bool = True):
    """Build a stub ``self`` for ``CycleTypeMixin._cycle_type``.

    ``bpy.types.Operator`` subclasses can't be ``__init__``-ed outside of
    Blender's registration path (``bpy_struct.__new__`` rejects a bare
    call). Calling the unbound mixin method with a stub ``self`` that
    mirrors the class attributes the method reads is the cleanest way to
    exercise the cycle logic without launching a registered operator
    instance.

    ``element_checker`` and ``props_getter`` are captured by the cycle
    operator at class-definition time, so global ``tool.*`` patches at
    test time can't intercept them — the stub injects callables directly
    instead. ``_resolve_target`` is bound from ``TypeAccessorBase`` so
    the cycle method's call into it dispatches against the stub
    attributes."""
    from types import MethodType

    from bonsai.bim.module.model.roof import CycleRoofGenerationMethod
    from bonsai.bim.parametric_lifecycle import TypeAccessorBase

    stub = SimpleNamespace(
        reverse=reverse,
        skip_element_check=False,
        element_checker=lambda _elem: element_is_target,
        props_getter=lambda _obj: props,
        type_literal=CycleRoofGenerationMethod.type_literal,
        type_attr=CycleRoofGenerationMethod.type_attr,
    )
    stub._resolve_target = MethodType(TypeAccessorBase._resolve_target, stub)
    return stub


def test_cycle_type_advances_forward():
    """``_cycle_type`` advances the prop value to the next item in the
    Literal. The stub injects ``element_checker`` / ``props_getter``
    directly so the method runs without a live IFC fixture."""
    from bonsai import tool
    from bonsai.bim import parametric_lifecycle as gizmo_module

    props = SimpleNamespace(generation_method="HEIGHT")
    context = SimpleNamespace(active_object=object())

    with patch.object(tool.Ifc, "get_entity", return_value=object()):
        result = gizmo_module.CycleTypeMixin._cycle_type(_cycle_stub_self(reverse=False, props=props), context)
    assert result == {"FINISHED"}
    assert props.generation_method == "ANGLE"


def test_cycle_type_reverse_walks_backward():
    """Shift+click sets ``reverse=True`` and walks the cycle in the other
    direction — from HEIGHT that means wrapping to ANGLE (the last item)."""
    from bonsai import tool
    from bonsai.bim import parametric_lifecycle as gizmo_module

    props = SimpleNamespace(generation_method="HEIGHT")
    context = SimpleNamespace(active_object=object())

    with patch.object(tool.Ifc, "get_entity", return_value=object()):
        gizmo_module.CycleTypeMixin._cycle_type(_cycle_stub_self(reverse=True, props=props), context)
    assert props.generation_method == "ANGLE"  # wrapped from HEIGHT backward


def test_cycle_type_cancels_when_active_is_not_a_roof():
    """Non-roof active object → CANCELLED, props untouched. Guards against
    a stray cycle click on a wall mutating ``wall.generation_method`` (a
    non-existent attr) and silently no-oping or AttributeError-ing later."""
    from bonsai import tool
    from bonsai.bim import parametric_lifecycle as gizmo_module

    props = SimpleNamespace(generation_method="HEIGHT")
    context = SimpleNamespace(active_object=object())

    with patch.object(tool.Ifc, "get_entity", return_value=object()):
        result = gizmo_module.CycleTypeMixin._cycle_type(
            _cycle_stub_self(reverse=False, props=props, element_is_target=False),
            context,
        )
    assert result == {"CANCELLED"}
    assert props.generation_method == "HEIGHT"


# ----------------------------------------------------------------------------
# _update_dimension_gizmo_positions — origin anchoring
# ----------------------------------------------------------------------------
#
# All three dimension gizmos anchor at the object's local origin. Their
# declared axes (height/slope +Z, thickness -Z) separate them in 3D so
# they don't visually collide despite sharing a position; height + slope
# are themselves mutually exclusive via visibility_condition on
# generation_method.


def test_override_positions_all_dimensions_at_object_origin():
    """The override calls ``set_dimension_gizmo_position`` with the
    object-local origin (0, 0, 0) for every dimension gizmo. Anchoring at
    the object origin keeps the gizmos tied to the object's matrix_world
    rather than to footprint geometry that may not be cached yet — fixes
    the first-click default-identity-matrix bug structurally."""
    from bonsai.bim.module.model.roof import GizmoRoofEdition

    calls: dict[str, tuple] = {}

    def record(attr_name, _mw, position, axis, _value=None):
        calls[attr_name] = (position, axis)

    stub = SimpleNamespace(set_dimension_gizmo_position=record)
    GizmoRoofEdition._update_dimension_gizmo_positions(stub, context=None, mw=None, props=None)

    assert set(calls) == {"height", "angle", "roof_thickness"}
    for name in ("height", "angle", "roof_thickness"):
        position, _axis = calls[name]
        assert position.xyz[:] == pytest.approx(
            (0.0, 0.0, 0.0)
        ), f"{name} anchored at {position.xyz[:]} instead of object origin"
    # Axes split the three handles along Z+ (height/slope) vs Z- (thickness)
    # so they don't visually collide despite sharing the anchor point.
    assert calls["height"][1] == (0, 0, 1)
    assert calls["angle"][1] == (0, 0, 1)
    assert calls["roof_thickness"][1] == (0, 0, -1)


# ----------------------------------------------------------------------------
# Registration smoke test
# ----------------------------------------------------------------------------
#
# Pattern 4 from _shared/bonsai-test-patterns.md: assert the operator is
# actually registered as ``bim.cycle_roof_generation_method``. Catches
# ``bl_idname`` typos and missing-from-``classes``-tuple regressions at
# test time rather than at user-click time (the failure mode otherwise is
# a silent no-op on the cycle icon, because the gizmo base class skips the
# icon entirely if its ``cycle_type_operator`` resolves to nothing).


def test_cycle_operator_is_registered_under_bim_namespace():
    assert hasattr(bpy.ops.bim, "cycle_roof_generation_method")
