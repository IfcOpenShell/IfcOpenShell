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

import types
from types import SimpleNamespace

import bmesh
import bpy
import pytest

from bonsai import tool
from bonsai.bim.module.drawing.gizmos import (
    BaseSchematicGizmoGroup,
    DimensionGizmoConfig,
)
from bonsai.bim.module.model.railing import GizmoRailingSchematic

pytestmark = pytest.mark.model


@pytest.fixture(autouse=True)
def _require_real_bpy():
    """Skip the file when ``bpy`` is mocked or absent.

    Without this guard, mis-routed test runs (e.g. ``pytest test/bim/...``
    invoked outside Blender) crash at module-collection time on the chain of
    ``bonsai.tool`` imports below, instead of producing a clean ``skipped``.
    """
    if not isinstance(bpy, types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


# ── Class shape ──────────────────────────────────────────────────────────────


def test_railing_schematic_inherits_base():
    """GizmoRailingSchematic plugs into the schematic framework, not the
    in-place dimension framework. If a future refactor breaks this lineage
    the schematic-specific machinery (sliders, draw handler) silently goes
    dormant."""
    assert issubclass(GizmoRailingSchematic, BaseSchematicGizmoGroup)


def test_railing_schematic_bl_idname_preserved():
    """``OBJECT_GGT_bim_railing_edition`` is the user-facing identifier and
    is referenced by keymaps and persistence. Preserve it across the class
    rename — see the migration note in the class docstring."""
    assert GizmoRailingSchematic.bl_idname == "OBJECT_GGT_bim_railing_edition"


def test_railing_schematic_props_getter_pairing():
    """``gizmo_pref_name = "railing"`` and ``props_getter = tool.Model.get_railing_props``
    are the pairing test_parametric_registry depends on. If either drifts,
    the addon-preferences gizmo toggle silently stops controlling this group."""
    assert GizmoRailingSchematic.gizmo_pref_name == "railing"
    assert GizmoRailingSchematic.props_getter == tool.Model.get_railing_props


def test_railing_schematic_disables_in_place_dimension_props():
    """The schematic owns the value-input surface — no in-place dimensions on the actual geometry."""
    assert GizmoRailingSchematic.dimension_gizmo_props == []


# ── Dimension configuration ─────────────────────────────────────────────────


def test_railing_schematic_has_six_dimensions():
    """One dimension per parametric property — three for each railing_type."""
    assert len(GizmoRailingSchematic.schematic_dimension_props) == 6


def test_railing_schematic_dimension_attr_names_complete():
    """The six bound attributes match the parametric properties that
    ``update_railing_modifier_bmesh`` reads when regenerating the live preview."""
    attr_names = {c.attr_name for c in GizmoRailingSchematic.schematic_dimension_props}
    assert attr_names == {
        "height",
        "thickness",
        "spacing",
        "railing_diameter",
        "clear_width",
        "support_spacing",
    }


def test_railing_schematic_dimensions_are_dimension_configs():
    """The dimension-line aesthetic depends on ``DimensionGizmoConfig`` (with
    arrows + label), not the abstract slider widget."""
    for config in GizmoRailingSchematic.schematic_dimension_props:
        assert isinstance(config, DimensionGizmoConfig)


def test_railing_schematic_dimensions_have_text_formatters():
    """Each dimension must format the label from the actual property value,
    not from the visually-scaled value the gizmo's getter returns. Without a
    formatter the label would show the schematic-scaled length, which is
    meaningless to the user."""
    for config in GizmoRailingSchematic.schematic_dimension_props:
        assert config.text_formatter is not None, f"{config.attr_name} missing text_formatter"


@pytest.mark.parametrize(
    "attr_name,railing_type,expected",
    [
        ("height", "FRAMELESS_PANEL", True),
        ("height", "WALL_MOUNTED_HANDRAIL", False),
        ("thickness", "FRAMELESS_PANEL", True),
        ("spacing", "FRAMELESS_PANEL", True),
        ("railing_diameter", "WALL_MOUNTED_HANDRAIL", True),
        ("railing_diameter", "FRAMELESS_PANEL", False),
        ("clear_width", "WALL_MOUNTED_HANDRAIL", True),
    ],
)
def test_railing_schematic_dimension_visibility_gated_by_railing_type(attr_name, railing_type, expected):
    """The two railing types are mutually exclusive — height/thickness/spacing
    belong to FRAMELESS_PANEL; railing_diameter/clear_width/support_spacing
    belong to WALL_MOUNTED_HANDRAIL. The visibility lambdas enforce that."""
    config = next(c for c in GizmoRailingSchematic.schematic_dimension_props if c.attr_name == attr_name)
    props = SimpleNamespace(railing_type=railing_type, use_manual_supports=False)
    assert config.visibility_condition(props) is expected


def test_railing_schematic_support_spacing_hidden_for_manual_supports():
    """``support_spacing`` only drives auto-positioned supports — when the
    user has switched to manual supports the dimension should disappear."""
    config = next(c for c in GizmoRailingSchematic.schematic_dimension_props if c.attr_name == "support_spacing")
    auto = SimpleNamespace(railing_type="WALL_MOUNTED_HANDRAIL", use_manual_supports=False)
    manual = SimpleNamespace(railing_type="WALL_MOUNTED_HANDRAIL", use_manual_supports=True)
    assert config.visibility_condition(auto) is True
    assert config.visibility_condition(manual) is False


# ── Fixed-length tag rendering ─────────────────────────────────────────────


def test_schematic_dim_visible_length_is_constant():
    """Every schematic dimension tag renders at the same width — the bar is a
    UI affordance, not a proportional measurement. The constant ratio keeps
    tiny (5 mm thickness) and huge (5 m height) values equally clickable; the
    real value lives in the dimension label.

    Regression guard: if value-proportional scaling is reintroduced, this
    contract breaks silently — small dimensions start collapsing into stacked
    arrows again.
    """
    cls = GizmoRailingSchematic
    ratio = cls.SCHEMATIC_DIM_VISIBLE_LENGTH_RATIO
    assert ratio > 0
    assert ratio <= 1.0  # bar must fit within the schematic box


def test_schematic_no_compute_schematic_scale_override():
    """The constant-length schematic must not reintroduce scale-based
    proportional sizing via a ``_compute_schematic_scale`` override."""
    assert "_compute_schematic_scale" not in GizmoRailingSchematic.__dict__


# ── Path-edit guard ─────────────────────────────────────────────────────────


def test_update_editing_gizmos_override_defined_on_subclass():
    """``GizmoRailingSchematic`` must own the override that hides the pen
    icon during path-edit. The parent's version shows the pen whenever
    ``is_editing`` is False, which includes path-edit; that would let the
    user open two editing modes at once."""
    assert "update_editing_gizmos" in GizmoRailingSchematic.__dict__


# ── Schematic mesh building ─────────────────────────────────────────────────


def test_build_schematic_mesh_frameless_panel_returns_bmesh_with_edges():
    """FRAMELESS_PANEL renders as two separated wireframe boxes — 8 corners
    per box × 2 = 16 verts; 12 edges per box × 2 = 24 edges. The visible
    gap between the two boxes is the "spacing" semantic made literal.

    The mesh proportions are fixed (independent of property values) so the
    dimension gizmos can anchor to known feature positions; the property
    values are shown through dimension labels, not the mesh size."""
    props = SimpleNamespace(
        railing_type="FRAMELESS_PANEL",
        height=1.0,
        thickness=0.05,
        spacing=0.5,
    )
    bm = GizmoRailingSchematic.build_schematic_mesh(props)
    try:
        assert isinstance(bm, bmesh.types.BMesh)
        assert len(bm.verts) == 16
        assert len(bm.edges) == 24
    finally:
        bm.free()


def test_build_schematic_mesh_wall_mounted_handrail_returns_bmesh_with_edges():
    """WALL_MOUNTED_HANDRAIL renders as three visual elements:

    - **Wall outline** — 4 corner verts, 4 edges (rectangle at z=0).
    - **Hex tube** — 12 verts (6 per ring × 2 ends), 18 edges
      (6 left ring + 6 right ring + 6 axial).
    - **L-brackets** at each rail end — 3 verts per bracket (rail centre,
      corner, wall attach) × 2 brackets = 6 verts; 2 edges per bracket
      (rail→corner, corner→wall) × 2 = 4 edges.

    Total: 22 verts, 26 edges.
    """
    props = SimpleNamespace(
        railing_type="WALL_MOUNTED_HANDRAIL",
        railing_diameter=0.05,
        clear_width=0.04,
        support_spacing=1.0,
    )
    bm = GizmoRailingSchematic.build_schematic_mesh(props)
    try:
        assert isinstance(bm, bmesh.types.BMesh)
        assert len(bm.verts) == 22
        assert len(bm.edges) == 26
    finally:
        bm.free()


def test_build_schematic_mesh_proportions_independent_of_props():
    """The mesh uses fixed proportions so dimension gizmo anchor points stay
    aligned with the geometry — extreme prop ratios don't change the mesh."""
    small = SimpleNamespace(railing_type="FRAMELESS_PANEL", height=0.01, thickness=0.005, spacing=0.05)
    large = SimpleNamespace(railing_type="FRAMELESS_PANEL", height=10.0, thickness=0.5, spacing=2.0)
    bm_small = GizmoRailingSchematic.build_schematic_mesh(small)
    bm_large = GizmoRailingSchematic.build_schematic_mesh(large)
    try:
        # Same vert count regardless of prop magnitude.
        assert len(bm_small.verts) == len(bm_large.verts)
        # Same bounding box in each axis (within floating-point noise).
        for axis in range(3):
            small_coords = [v.co[axis] for v in bm_small.verts]
            large_coords = [v.co[axis] for v in bm_large.verts]
            assert min(small_coords) == pytest.approx(min(large_coords))
            assert max(small_coords) == pytest.approx(max(large_coords))
    finally:
        bm_small.free()
        bm_large.free()


def test_build_schematic_mesh_panel_top_matches_height_frac():
    """The panel's top edge sits at exactly ``SCHEMATIC_MESH_HEIGHT_FRAC``,
    which is also where the ``thickness`` dimension anchors above the box.
    If this drifts, the dimension labels float disconnected from the mesh."""
    props = SimpleNamespace(railing_type="FRAMELESS_PANEL", height=1.0, thickness=0.05, spacing=0.3)
    bm = GizmoRailingSchematic.build_schematic_mesh(props)
    try:
        max_y = max(v.co.y for v in bm.verts)
        assert max_y == pytest.approx(GizmoRailingSchematic.SCHEMATIC_MESH_HEIGHT_FRAC)
    finally:
        bm.free()
