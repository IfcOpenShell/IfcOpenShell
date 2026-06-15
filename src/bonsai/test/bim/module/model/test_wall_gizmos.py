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

"""Unit tests for the poll() preconditions of wall billboarding gizmo groups.

These tests patch ``tool.Blender`` / ``tool.Ifc`` / ``tool.Model`` so the poll
logic can be exercised without a real IFC fixture. Each test pins one of the
gates ``poll()`` walks, so any silent regression in the gate order or in the
LAYER3-active / LAYER2-other contract is caught by a dedicated assertion."""

from types import SimpleNamespace
from unittest.mock import patch

import bpy
import pytest

pytestmark = pytest.mark.wall


class _Obj:
    """Hashable, name-bearing stand-in for a ``bpy.types.Object`` selection
    slot. ``SimpleNamespace`` defines ``__eq__`` (and so ``__hash__ = None``)
    which makes it unusable inside the ``set()`` that
    ``get_selected_objects()`` returns; a plain class falls back to
    identity-based hashing and works inside both ``set`` and ``list``."""

    def __init__(self, name: str) -> None:
        self.name = name


def _make_context(active, selected):
    """Build a minimal ``context`` stub with the two attributes ``poll()`` reads."""
    return SimpleNamespace(active_object=active, selected_objects=list(selected))


def _patch_tools(
    prefs_on, selected, active_element, other_element, active_usage, other_usage, other_is_path_connectable=None
):
    """Return a stack of patches that simulate one selection / IFC state for poll().

    ``prefs.gizmos.draw_gizmos_in_3d_viewport`` is the top-level toggle. The
    selection set, the IFC entity lookup, the usage-type lookup, and the
    path-connectable-wall predicate are stubbed so the test only depends on
    the predicate ordering in poll()."""
    prefs = SimpleNamespace(gizmos=SimpleNamespace(draw_gizmos_in_3d_viewport=prefs_on))

    entity_map = {}
    usage_map = {}
    # active_element/other_element are matched by object identity from the selected set
    if len(selected) == 2:
        entity_map[id(selected[0])] = active_element
        entity_map[id(selected[1])] = other_element
        usage_map[id(active_element)] = active_usage
        usage_map[id(other_element)] = other_usage

    if other_is_path_connectable is None:
        other_is_path_connectable = other_usage == "LAYER2"

    def get_entity(obj):
        return entity_map.get(id(obj))

    def get_usage_type(element):
        return usage_map.get(id(element))

    def is_path_connectable_wall(element):
        return element is other_element and other_is_path_connectable

    from bonsai import tool

    return [
        patch.object(tool.Blender, "get_addon_preferences", return_value=prefs),
        patch.object(tool.Blender, "get_selected_objects", return_value=set(selected)),
        patch.object(tool.Ifc, "get_entity", side_effect=get_entity),
        patch.object(tool.Model, "get_usage_type", side_effect=get_usage_type),
        patch.object(tool.Parametric, "is_path_connectable_wall", side_effect=is_path_connectable_wall),
        # The array-child filter is pinned by its own test file; stub it here
        # so these poll tests stay focused on the count / layer-usage gates
        # and don't have to scaffold the memoization cache key.
        patch.object(tool.Blender.Modifier, "any_selected_is_array_child", return_value=False),
    ]


def _run_poll(
    prefs_on,
    active_is_in_selected,
    len_override,
    active_usage,
    other_usage,
    active_has_entity=True,
    other_is_path_connectable=None,
):
    from bonsai.bim.module.model.wall import GizmoWallExtendVertically

    slab_obj = _Obj("slab")
    wall_obj = _Obj("wall")
    active = slab_obj if active_is_in_selected else _Obj("active_extra")
    if len_override is None:
        selected = [slab_obj, wall_obj]
    else:
        selected = [_Obj(f"obj_{i}") for i in range(len_override)]
        if active_is_in_selected and selected:
            active = selected[0]

    slab_element = object() if active_has_entity else None
    wall_element = object()

    patches = _patch_tools(
        prefs_on,
        selected,
        slab_element,
        wall_element,
        active_usage,
        other_usage,
        other_is_path_connectable=other_is_path_connectable,
    )
    for p in patches:
        p.start()
    try:
        return GizmoWallExtendVertically.poll(_make_context(active, selected))
    finally:
        for p in patches:
            p.stop()


def test_poll_accepts_layer3_active_with_layer2_other():
    assert (
        _run_poll(
            prefs_on=True, active_is_in_selected=True, len_override=None, active_usage="LAYER3", other_usage="LAYER2"
        )
        is True
    )


def test_poll_rejects_when_gizmo_toggle_off():
    assert (
        _run_poll(
            prefs_on=False, active_is_in_selected=True, len_override=None, active_usage="LAYER3", other_usage="LAYER2"
        )
        is False
    )


def test_poll_rejects_when_selection_count_is_not_two():
    assert (
        _run_poll(
            prefs_on=True, active_is_in_selected=True, len_override=3, active_usage="LAYER3", other_usage="LAYER2"
        )
        is False
    )
    assert (
        _run_poll(
            prefs_on=True, active_is_in_selected=True, len_override=1, active_usage="LAYER3", other_usage="LAYER2"
        )
        is False
    )


def test_poll_rejects_when_active_has_no_ifc_entity():
    assert (
        _run_poll(
            prefs_on=True,
            active_is_in_selected=True,
            len_override=None,
            active_usage="LAYER3",
            other_usage="LAYER2",
            active_has_entity=False,
        )
        is False
    )


def test_poll_rejects_when_active_is_not_layer3():
    # A LAYER2 active (wall) must NOT trigger this gizmo — the wall-join gizmo
    # owns that case, and extend_walls_to_underside expects the slab to be active.
    assert (
        _run_poll(
            prefs_on=True, active_is_in_selected=True, len_override=None, active_usage="LAYER2", other_usage="LAYER2"
        )
        is False
    )
    # Active with no usage at all (generic mesh, e.g. an opening blocker) is also rejected.
    assert (
        _run_poll(prefs_on=True, active_is_in_selected=True, len_override=None, active_usage=None, other_usage="LAYER2")
        is False
    )


def test_poll_rejects_when_other_is_not_layer2_wall():
    assert (
        _run_poll(
            prefs_on=True, active_is_in_selected=True, len_override=None, active_usage="LAYER3", other_usage="LAYER3"
        )
        is False
    )
    assert (
        _run_poll(prefs_on=True, active_is_in_selected=True, len_override=None, active_usage="LAYER3", other_usage=None)
        is False
    )


def test_poll_accepts_fillet_corner_wall_partner():
    # Fillet-corner walls carry no LAYER2 usage by spec but the extend-to-
    # underside operator handles them just like a parametric LAYER2 wall —
    # the gizmo must surface for the slab + fillet-corner selection too.
    assert (
        _run_poll(
            prefs_on=True,
            active_is_in_selected=True,
            len_override=None,
            active_usage="LAYER3",
            other_usage=None,
            other_is_path_connectable=True,
        )
        is True
    )


# ----------------------------------------------------------------------------
# _iter_path_connections — IfcRelConnectsPathElements inverse-graph walk
# ----------------------------------------------------------------------------
#
# Normalises both ConnectedTo and ConnectedFrom orientations to (other, self_ct,
# other_ct) so callers always read "self first" regardless of which side of the
# rel this wall was authored on. Non-wall partners and malformed (None) refs are
# filtered out so per-frame gizmo positioning survives partial IFC state.


def _make_path_rel(relating, related, relating_ct, related_ct, kind="IfcRelConnectsPathElements"):
    """Build a stub IfcRelConnectsPathElements for inverse-walk tests."""
    return SimpleNamespace(
        is_a=lambda name, _k=kind: name == _k,
        RelatingElement=relating,
        RelatedElement=related,
        RelatingConnectionType=relating_ct,
        RelatedConnectionType=related_ct,
    )


def _run_iter_path_connections(elem, *, partner_predicate=lambda _e: True):
    from bonsai import tool
    from bonsai.bim.module.model.wall import _iter_path_connections

    with patch.object(tool.Parametric, "is_path_connectable_wall", side_effect=partner_predicate):
        return _iter_path_connections(elem)


def test_iter_path_connections_empty_inverses_yields_nothing():
    elem = SimpleNamespace(ConnectedTo=[], ConnectedFrom=[])
    assert _run_iter_path_connections(elem) == []


def test_iter_path_connections_connected_to_orientation_is_self_first():
    # Self is the rel's RelatingElement → its connection type is RelatingConnectionType.
    self_elem = object()
    other = object()
    rel = _make_path_rel(relating=self_elem, related=other, relating_ct="ATEND", related_ct="ATSTART")
    elem = SimpleNamespace(ConnectedTo=[rel], ConnectedFrom=[])
    assert _run_iter_path_connections(elem) == [(other, "ATEND", "ATSTART")]


def test_iter_path_connections_connected_from_orientation_is_self_first():
    # Self is the rel's RelatedElement → its connection type is RelatedConnectionType.
    # The helper must FLIP the tuple so callers still see (other, self_ct, other_ct).
    self_elem = object()
    other = object()
    rel = _make_path_rel(relating=other, related=self_elem, relating_ct="ATSTART", related_ct="ATEND")
    elem = SimpleNamespace(ConnectedTo=[], ConnectedFrom=[rel])
    assert _run_iter_path_connections(elem) == [(other, "ATEND", "ATSTART")]


def test_iter_path_connections_skips_non_path_rels():
    # IfcRelAggregates, IfcRelContainedInSpatialStructure, etc. share the
    # ConnectedTo/ConnectedFrom inverse arrays — only IfcRelConnectsPathElements
    # carries the per-end connection-type semantics we care about.
    self_elem = object()
    other = object()
    non_path = _make_path_rel(
        relating=self_elem, related=other, relating_ct="ATSTART", related_ct="ATEND", kind="IfcRelAggregates"
    )
    path = _make_path_rel(relating=self_elem, related=other, relating_ct="ATEND", related_ct="ATSTART")
    elem = SimpleNamespace(ConnectedTo=[non_path, path], ConnectedFrom=[])
    assert _run_iter_path_connections(elem) == [(other, "ATEND", "ATSTART")]


def test_iter_path_connections_skips_non_wall_partners():
    # Walls may path-connect to non-wall elements (columns, beams). The single-
    # wall unjoin gizmo only surfaces wall-to-wall joins to match the existing
    # two-wall gizmo's scope.
    self_elem = object()
    wall_partner = object()
    non_wall_partner = object()
    rel_wall = _make_path_rel(relating=self_elem, related=wall_partner, relating_ct="ATEND", related_ct="ATSTART")
    rel_non_wall = _make_path_rel(
        relating=self_elem, related=non_wall_partner, relating_ct="ATEND", related_ct="ATSTART"
    )
    elem = SimpleNamespace(ConnectedTo=[rel_wall, rel_non_wall], ConnectedFrom=[])
    result = _run_iter_path_connections(elem, partner_predicate=lambda e: e is wall_partner)
    assert result == [(wall_partner, "ATEND", "ATSTART")]


def test_iter_path_connections_includes_fillet_corner_partner():
    # Fillet-corner walls carry no LAYER2 usage but are still valid path
    # partners. The enumeration must use the same predicate the gizmo group's
    # poll uses for the host wall — otherwise the corner is silently dropped
    # from the neighbour's connection list and looks unconnected from the
    # LAYER2 wall's perspective.
    self_elem = object()
    fillet_partner = object()
    rel = _make_path_rel(relating=self_elem, related=fillet_partner, relating_ct="ATEND", related_ct="ATSTART")
    elem = SimpleNamespace(ConnectedTo=[rel], ConnectedFrom=[])
    result = _run_iter_path_connections(elem, partner_predicate=lambda e: e is fillet_partner)
    assert result == [(fillet_partner, "ATEND", "ATSTART")]


def test_iter_path_connections_tolerates_none_partner_refs():
    # Malformed / partial IFC files can leave a rel's element ref unset.
    # Without a None guard, the partner predicate would receive None and
    # raise on `.is_a(...)` mid-frame, silently breaking the gizmo group.
    self_elem = object()
    other = object()
    rel_none = _make_path_rel(relating=self_elem, related=None, relating_ct="ATEND", related_ct="ATSTART")
    rel_ok = _make_path_rel(relating=self_elem, related=other, relating_ct="ATSTART", related_ct="ATEND")
    elem = SimpleNamespace(ConnectedTo=[rel_none, rel_ok], ConnectedFrom=[])
    assert _run_iter_path_connections(elem) == [(other, "ATSTART", "ATEND")]


def test_iter_path_connections_walks_both_inverses_in_order():
    # A wall can sit on both sides of different path rels (e.g. authored once
    # as the RelatingElement, once as the RelatedElement). The helper walks
    # ConnectedTo first, then ConnectedFrom — pinning the order so callers can
    # depend on it for icon-slot allocation.
    self_elem = object()
    p1 = object()
    p2 = object()
    rel_to = _make_path_rel(relating=self_elem, related=p1, relating_ct="ATSTART", related_ct="ATSTART")
    rel_from = _make_path_rel(relating=p2, related=self_elem, relating_ct="ATEND", related_ct="ATEND")
    elem = SimpleNamespace(ConnectedTo=[rel_to], ConnectedFrom=[rel_from])
    assert _run_iter_path_connections(elem) == [(p1, "ATSTART", "ATSTART"), (p2, "ATEND", "ATEND")]


# ----------------------------------------------------------------------------
# _perpendicular_wall_params — clamping + side detection for the
# "add perpendicular wall at cursor" gizmo and its operator.
# ----------------------------------------------------------------------------
#
# Pure scalar math. The dead-zone is ``CURSOR_STACK_OFFSET`` — inside it the
# on-axis split / extend-X icons own the click and this helper returns None.


def _wall_consts():
    from bonsai.bim.module.model.wall import GizmoWallEdition

    return GizmoWallEdition.CURSOR_STACK_OFFSET


def _run_perp_params(cursor_x, cursor_y, anchor_x=0.0, length=5.0):
    from bonsai.bim.module.model.wall import _perpendicular_wall_params

    return _perpendicular_wall_params(cursor_x, cursor_y, anchor_x, length)


def test_perpendicular_params_on_axis_returns_none():
    assert _run_perp_params(cursor_x=2.0, cursor_y=0.0) is None


def test_perpendicular_params_at_dead_zone_boundary_returns_none():
    # Inclusive boundary: at exactly the threshold the on-axis icons still own
    # the click; the gizmo only takes over strictly past the dead zone.
    threshold = _wall_consts()
    assert _run_perp_params(cursor_x=2.0, cursor_y=threshold) is None
    assert _run_perp_params(cursor_x=2.0, cursor_y=-threshold) is None


def test_perpendicular_params_just_past_dead_zone_returns_params():
    threshold = _wall_consts()
    result = _run_perp_params(cursor_x=2.0, cursor_y=threshold + 0.01)
    assert result is not None
    clamped_x, length, side = result
    assert clamped_x == pytest.approx(2.0)
    assert length == pytest.approx(threshold + 0.01)
    assert side == 1.0


def test_perpendicular_params_negative_y_flips_side_sign():
    result = _run_perp_params(cursor_x=2.0, cursor_y=-1.5)
    assert result is not None
    _, length, side = result
    # Length is always positive — the side sign carries the direction so the
    # operator can pick the +90° vs -90° rotation without sign-flipping length.
    assert length == pytest.approx(1.5)
    assert side == -1.0


def test_perpendicular_params_clamps_low_when_cursor_left_of_wall():
    result = _run_perp_params(cursor_x=-2.0, cursor_y=1.5, anchor_x=0.0, length=5.0)
    assert result is not None
    clamped_x, _length, _side = result
    assert clamped_x == pytest.approx(0.0)


def test_perpendicular_params_clamps_high_when_cursor_right_of_wall():
    result = _run_perp_params(cursor_x=10.0, cursor_y=1.5, anchor_x=0.0, length=5.0)
    assert result is not None
    clamped_x, _length, _side = result
    assert clamped_x == pytest.approx(5.0)


def test_perpendicular_params_respects_nonzero_anchor_x():
    # Non-zero anchor_x shifts the wall span; clamping must follow.
    result = _run_perp_params(cursor_x=0.5, cursor_y=1.5, anchor_x=2.0, length=5.0)
    assert result is not None
    clamped_x, _length, _side = result
    assert clamped_x == pytest.approx(2.0)

    result = _run_perp_params(cursor_x=10.0, cursor_y=1.5, anchor_x=2.0, length=5.0)
    assert result is not None
    clamped_x, _length, _side = result
    assert clamped_x == pytest.approx(7.0)


def test_perpendicular_params_in_range_passes_cursor_x_through():
    result = _run_perp_params(cursor_x=3.0, cursor_y=1.5, anchor_x=0.0, length=5.0)
    assert result is not None
    clamped_x, length, side = result
    assert clamped_x == pytest.approx(3.0)
    assert length == pytest.approx(1.5)
    assert side == 1.0
