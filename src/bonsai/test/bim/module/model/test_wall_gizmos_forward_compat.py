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

"""Forward-compat AST contracts for wall gizmo internals.

Pins structural invariants that no per-call-site behavioural test can catch
on its own: the kind of "someone tidied the imports" regression that leaves
tests green but silently changes runtime semantics. Each contract names the
invariant it pins so a future revert tells the contributor exactly what the
rule is."""

import ast
import inspect
import textwrap

import pytest

pytestmark = pytest.mark.wall


def test_iter_path_connections_uses_path_connectable_predicate():
    """The partner filter must consult the looser ``is_path_connectable_wall``
    predicate, matching the host-side predicate used by the gizmo group's
    poll. Strict ``is_wall`` rejects fillet-corner walls (which have no
    LAYER2 usage by IFC spec), so a regression to ``is_wall`` would silently
    drop fillet partners from the connection list — visible to the user as
    "the corner looks unconnected from the adjacent wall's selection.\" """
    from bonsai.bim.module.model.wall import _iter_path_connections

    source = inspect.getsource(_iter_path_connections)
    tree = ast.parse(source)
    attr_names = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert "is_path_connectable_wall" in attr_names, (
        "_iter_path_connections must filter partners with is_path_connectable_wall — "
        "the same predicate the gizmo group's poll uses on the host wall. "
        "Symmetry between host and partner predicates is required for fillet "
        "corners (no LAYER2 usage) to surface as connected from their LAYER2 "
        "neighbours' perspective."
    )
    assert "is_wall" not in attr_names, (
        "_iter_path_connections must NOT call .is_wall on partner elements — "
        "that strict predicate drops fillet-corner walls. Use "
        "is_path_connectable_wall instead."
    )


def test_gizmo_wall_link_toggle_invokes_partner_bbox_helper():
    """The wall subclass must call draw_wall_partner_bbox when its hover
    state is active. Without this contract the partner-wall highlight
    silently regresses if someone "tidies" the draw() override away."""
    from bonsai.bim.module.model import wall as wall_module

    source = textwrap.dedent(inspect.getsource(wall_module.GizmoWallLinkToggle.draw))
    tree = ast.parse(source)
    attr_names = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    call_names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Attribute):
            call_names.add(node.func.attr)
        elif isinstance(node.func, ast.Name):
            call_names.add(node.func.id)

    assert "is_highlight" in attr_names, (
        "GizmoWallLinkToggle.draw must gate its highlight call on self.is_highlight — "
        "without it the partner outline would draw every frame, not just on hover."
    )
    assert "draw_wall_partner_bbox" in call_names, (
        "GizmoWallLinkToggle.draw must call draw_wall_partner_bbox to render the "
        "partner outline. The shared composite in decorator.py is the canonical "
        "trigger for this feature; replacing it with an ad-hoc draw call would "
        "drift from the array-children bbox styling."
    )


def test_every_wall_gizmo_group_resolves_get_decoration_colors():
    """Any wall ``GizmoGroup`` whose ``setup()`` reads decoration colours via
    ``self.get_decoration_colors()`` must inherit from a mixin that supplies
    it (``gizmo.BaseParametricGizmoGroup`` or ``gizmo.BillboardingGizmoGroupMixin``).
    Without the mixin the call AttributeErrors inside ``setup()``, Blender
    logs the failure and skips the rest of ``setup()``, and every later
    ``draw_prepare()`` blows up on whichever attribute the truncated setup
    failed to assign — a silent, runtime-only regression that no other test
    catches."""
    import bpy

    from bonsai.bim.module.model import wall as wall_module

    offenders: list[str] = []
    for name in dir(wall_module):
        cls = getattr(wall_module, name)
        if not inspect.isclass(cls):
            continue
        if inspect.getmodule(cls) is not wall_module:
            continue
        if not issubclass(cls, bpy.types.GizmoGroup):
            continue
        setup = cls.__dict__.get("setup")
        if setup is None:
            continue
        try:
            src = inspect.getsource(setup)
        except (OSError, TypeError):
            continue
        if "self.get_decoration_colors()" not in src:
            continue
        if not hasattr(cls, "get_decoration_colors"):
            offenders.append(cls.__name__)

    assert not offenders, (
        f"GizmoGroup subclasses {offenders} call self.get_decoration_colors() in "
        "setup() but inherit from no class that provides it. Add "
        "gizmo.BillboardingGizmoGroupMixin (or gizmo.BaseParametricGizmoGroup) to "
        "the class bases — both define get_decoration_colors and are the canonical "
        "wall-gizmo mixins."
    )


def test_host_add_opening_accepts_fillet_corner_active():
    """``is_supported_host`` (the gate ``GizmoHostAddOpening.poll`` dispatches
    through) must classify walls via ``is_path_connectable_wall``, not the
    strict ``is_wall`` predicate. Fillet-corner walls carry no LAYER2 usage
    by IFC spec, so the strict predicate rejects them and the add-opening
    icon never surfaces over a curved corner — symmetry with the join /
    unjoin / extend wall gizmos (all of which already poll on the looser
    predicate) is required for the user to drop openings into fillet
    corners at all."""
    from bonsai.bim.module.model.host_add_opening_gizmo import is_supported_host

    source = textwrap.dedent(inspect.getsource(is_supported_host))
    tree = ast.parse(source)
    attr_names = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert "is_path_connectable_wall" in attr_names, (
        "is_supported_host must gate walls on tool.Parametric.is_path_connectable_wall. "
        "The strict is_wall predicate hides the add-opening gizmo over every "
        "fillet-corner wall."
    )
    assert "is_wall" not in attr_names, (
        "is_supported_host must NOT call .is_wall — that strict predicate drops "
        "fillet-corner walls. Use is_path_connectable_wall instead, matching the "
        "host gate every other wall-state gizmo group uses."
    )


def test_join_intersection_uses_l_and_t_glyphs():
    """``GizmoWallJoinIntersection.setup`` must bind the join icon to the L
    glyph (``VIEW3D_GT_wall_corner``) and the extend-to icon to the T glyph
    (``VIEW3D_GT_wall_tee``). The L / T pair makes the corner-join vs
    extend-into-side distinction read at a glance — a regression to the
    arrow-merge glyph for both icons makes them visually indistinguishable
    once they're stacked at the same XY."""
    from bonsai.bim.module.model.wall import GizmoWallJoinIntersection

    source = textwrap.dedent(inspect.getsource(GizmoWallJoinIntersection.setup))
    assert '"VIEW3D_GT_wall_corner"' in source, (
        "GizmoWallJoinIntersection.setup must bind join_icon to VIEW3D_GT_wall_corner "
        "(the L glyph). The arrow-merge glyph (VIEW3D_GT_merge) is the collinear-merge "
        "case and was visually ambiguous with the extend-to icon when both were stacked."
    )
    assert '"VIEW3D_GT_wall_tee"' in source, (
        "GizmoWallJoinIntersection.setup must bind extend_to_wall_icon to "
        "VIEW3D_GT_wall_tee (the T glyph). The arrow-extend glyph was visually "
        "ambiguous with the join icon when both were stacked."
    )


def test_join_intersection_stacks_along_screen_up_in_both_states():
    """``GizmoWallJoinIntersection.position_gizmos`` must route both the
    joined (unjoin + fillet) and the intersecting (join + extend + fillet)
    states through ``_stack_at`` so the icons stay individually clickable
    in any view, including top / plan view where world-Z separation
    collapses to zero on screen. A regression that re-introduces a
    per-state ``billboarded_at(corner, ...)`` write outside ``_stack_at``
    silently flattens the stack back onto one screen pixel."""
    from bonsai.bim.module.model.wall import GizmoWallJoinIntersection

    source = textwrap.dedent(inspect.getsource(GizmoWallJoinIntersection.position_gizmos))
    tree = ast.parse(source)
    call_names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Attribute):
            call_names.add(node.func.attr)
        elif isinstance(node.func, ast.Name):
            call_names.add(node.func.id)

    assert "_stack_at" in call_names, (
        "GizmoWallJoinIntersection.position_gizmos must call self._stack_at to "
        "lay icons along screen-up at the wall-top anchor. Direct "
        "billboarded_at writes for the join/unjoin/extend/fillet icons bypass "
        "the stacking contract and re-introduce the top-view collapse bug."
    )


def _get_wall_axis_callers_in(method) -> set[str]:
    """Return the set of attribute chains in ``method``'s source that resolve
    to ``tool.Model.get_wall_axis``. Empty set means the method does not read
    from the mesh-bound-box axis source."""
    source = textwrap.dedent(inspect.getsource(method))
    tree = ast.parse(source)
    offenders: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != "get_wall_axis":
            continue
        # Reconstruct the receiver chain to surface it in the assertion message.
        chain: list[str] = [func.attr]
        receiver = func.value
        while isinstance(receiver, ast.Attribute):
            chain.append(receiver.attr)
            receiver = receiver.value
        if isinstance(receiver, ast.Name):
            chain.append(receiver.id)
        offenders.add(".".join(reversed(chain)))
    return offenders


def _method_writes_ifc_axis(method) -> bool:
    """True iff ``method``'s body calls ``self.set_axis(...)`` — the only
    path that writes a wall's IFC reference line via
    ``ifcopenshell.api.geometry.assign_representation``. Methods that only
    read ``axis["base"]`` / ``axis["side"]`` for layer-polygon work (slab
    clipping, opening snap) never call ``set_axis`` and are not under this
    rule."""
    source = textwrap.dedent(inspect.getsource(method))
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "set_axis":
            return True
    return False


def test_dumb_wall_joiner_axis_writers_read_ifc_reference_line():
    """Any ``DumbWallJoiner`` method that writes the IFC reference line
    (via ``self.set_axis`` → ``ifcopenshell.api.geometry.assign_representation``)
    must read its input axis from the IFC reference line too — not from
    ``tool.Model.get_wall_axis``, whose X-extent comes from ``obj.bound_box``
    (the Body mesh AABB). The bound-box axis drifts past or short of the
    IFC reference line at mitred / butt-jointed walls and at walls with end
    openings; mixing it on input with the IFC axis on output produces
    non-colinear sub-axes that compound through chained extend/split/join
    edits.

    The IFC-anchored helper is ``tool.Wall.get_world_reference_line`` for
    world-space endpoints, or ``ifcopenshell.util.representation.get_reference_line``
    for local-SI endpoints.

    Joiner methods that only read layer-polygon base/side (e.g. ``clip``
    for slab intersection) are exempt — they need the body footprint, not
    the axis, and never call ``set_axis``."""
    from bonsai.bim.module.model.wall import DumbWallJoiner

    offenders: dict[str, set[str]] = {}
    for name, method in inspect.getmembers(DumbWallJoiner, predicate=inspect.isfunction):
        if not _method_writes_ifc_axis(method):
            continue
        bad_calls = _get_wall_axis_callers_in(method)
        if bad_calls:
            offenders[name] = bad_calls

    assert not offenders, (
        f"DumbWallJoiner methods that call self.set_axis must not read the "
        f"bound-box-derived axis: {offenders}. Use "
        "tool.Wall.get_world_reference_line for world-space endpoints, or "
        "ifcopenshell.util.representation.get_reference_line for local-SI "
        "endpoints. Mixing bound_box on input with IFC axis on output "
        "produces non-colinear sub-axes that compound through chained "
        "extend/split/join edits."
    )


def test_extend_walls_to_polyline_set_origin_uses_ifc_reference_line():
    """``ExtendWallsToPolylinePoint.set_origin`` seeds the polyline preview
    anchor at one of the wall's axis endpoints. The downstream operator
    (``DumbWallJoiner.extend``) projects the user's chosen target onto the
    IFC reference line; if the preview anchor comes from
    ``tool.Model.get_wall_axis`` (bound_box) the user sees the preview at
    one endpoint and the wall lands at a different one — the visible
    "extend falls short by a few cm/m" symptom."""
    from bonsai.bim.module.model.wall import ExtendWallsToPolylinePoint

    offenders = _get_wall_axis_callers_in(ExtendWallsToPolylinePoint.set_origin)

    assert not offenders, (
        f"ExtendWallsToPolylinePoint.set_origin must not read the bound-box-derived "
        f"axis: {offenders}. Use tool.Wall.get_world_reference_line so the preview "
        "anchor lands on the same IFC reference line the downstream extend operator "
        "projects onto."
    )


def test_wall_toggle_openings_uses_idle_slots():
    """The wall's toggle_openings icon must be declared in
    ``GizmoWallEdition.idle_slots`` so the base class lays it out at the
    standard pen-row position. Routing it through ad-hoc setup helpers
    instead would re-introduce the X-collision with the array's first
    per-layer icon — the bug this contract was added to prevent."""
    from bonsai.bim.module.model.wall import GizmoWallEdition

    slot_names = {s.name for s in GizmoWallEdition.idle_slots}
    assert "toggle_openings" in slot_names, (
        "GizmoWallEdition.idle_slots must contain a slot named 'toggle_openings'. "
        "The base class derives its X position from the slot's tuple index so peer "
        "groups (GizmoArrayEdition's per-layer icons) can query a real layout edge "
        "via _idle_row_right_edge() instead of a hardcoded per-feature table."
    )


def test_no_pen_row_toggle_openings_helpers_remain():
    """The legacy ``setup_pen_row_toggle_openings_icon`` and
    ``update_pen_row_toggle_openings_icon`` helpers were removed once
    toggle_openings migrated into the ``idle_slots`` system. A re-introduced
    helper would shadow the slot-driven layout — features calling it would
    set up a second gizmo at a different X and the collision-prevention
    contract would silently regress.

    Walks the wall and roof modules (the historical callers) plus
    drawing/gizmos.py (the historical home) for any reference to either
    name."""
    import bonsai.bim.module.drawing.gizmos as gizmos_mod
    import bonsai.bim.module.model.roof as roof_mod
    import bonsai.bim.module.model.wall as wall_mod

    forbidden = ("setup_pen_row_toggle_openings_icon", "update_pen_row_toggle_openings_icon")
    for mod in (gizmos_mod, roof_mod, wall_mod):
        source = inspect.getsource(mod)
        for name in forbidden:
            assert name not in source, (
                f"{mod.__name__} still references {name!r}. The toggle_openings icon "
                f"is now declared via idle_slots; the ad-hoc helpers were removed to "
                f"prevent layout drift between feature groups."
            )


def test_array_idle_max_x_walks_registry_not_hardcoded_dict():
    """``GizmoArrayEdition._resolve_feature_idle_max_x`` must query peer
    parametric gizmo groups' ``_idle_row_right_edge`` rather than indexing
    a hardcoded per-feature ``_FEATURE_IDLE_MAX_X`` dict. The dict approach
    was the source of the toggle_openings ↔ array-layer-icon collision bug
    on arrayed walls (find_for_element returns 'array' first, shadowing the
    wall reservation)."""
    from bonsai.bim.module.model.array import GizmoArrayEdition

    assert not hasattr(GizmoArrayEdition, "_FEATURE_IDLE_MAX_X"), (
        "GizmoArrayEdition._FEATURE_IDLE_MAX_X was a hardcoded per-feature dict "
        "that shadowed peer groups' real idle rows for compound elements (arrayed "
        "walls). It was replaced by a registry walk via REGISTRY + "
        "_idle_row_right_edge() — re-introducing the dict would re-create the bug."
    )

    source = inspect.getsource(GizmoArrayEdition._resolve_feature_idle_max_x)
    assert "_idle_row_right_edge" in source, (
        "_resolve_feature_idle_max_x must call peer_cls._idle_row_right_edge() so "
        "the X position derives from each peer's actual declared idle_slots."
    )
    assert "REGISTRY" in source, (
        "_resolve_feature_idle_max_x must iterate BaseParametricGizmoGroup.REGISTRY "
        "to discover peer groups; find_for_element returns ONE entry and shadows "
        "compound-element memberships."
    )
