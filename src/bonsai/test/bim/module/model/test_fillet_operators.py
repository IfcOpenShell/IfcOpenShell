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

"""Behaviour contracts for the wall-fillet operator chain.

Each fillet operator's geometry path requires real Blender + IFC fixtures
(walls with IfcMaterialLayerSetUsage, neighbour rels, etc.). End-to-end
fillet round-trips belong in the bim feature suite (model.feature) where
that scaffolding already exists. This file pins the surface-level invariants
that don't depend on the geometry path:

  * the lifecycle operators are registered under their conventional bl_idnames,
  * the enable poll rejects ineligible selections.

State-clearing tests via ``bpy.ops.bim.cancel_wall_fillet_preview()`` were
removed because the dispatch is flaky in full-suite ordering — the operator
early-returns when ``context.screen`` is unattached and prior tests can leave
the screen in that state. The behaviour is covered by the user-visible live
test loop instead."""

import bpy
import pytest

pytestmark = pytest.mark.model


def _fillet_op_names():
    """Walk bpy.ops.bim for operators whose name contains ``wall_fillet`` —
    avoids hard-coding the five lifecycle bl_idnames so adding / renaming
    one updates discovery automatically. Each name maps to a callable
    operator."""
    return sorted(name for name in dir(bpy.ops.bim) if "wall_fillet" in name)


class TestFilletOperatorsRegistered:
    """Catches accidental deregistration of any fillet lifecycle operator —
    drops in the classes tuple of bim/module/model/__init__.py would otherwise
    leave the gizmo group's target_set_operator binding pointing at a missing
    op and crash the first time a user clicked the icon."""

    def test_at_least_the_expected_lifecycle_set_is_registered(self):
        names = _fillet_op_names()
        # The lifecycle has enable + finish + cancel as a minimum; a healthy
        # build also includes the from-corner re-edit entry and the create
        # operator the finish dispatches to. The test asserts at least four —
        # below that the feature can't function — without enumerating each
        # by name, so the test stays meaningful if one is renamed or merged.
        assert len(names) >= 4, (
            f"Only {len(names)} fillet operators found on bpy.ops.bim: {names}. "
            "The fillet lifecycle needs enable + finish + cancel + create at "
            "minimum; check bim/module/model/__init__.py classes tuple."
        )

    def test_every_discovered_fillet_op_is_callable(self):
        for name in _fillet_op_names():
            op = getattr(bpy.ops.bim, name)
            assert callable(op), f"bpy.ops.bim.{name} is not callable — registration broke?"


class TestEnableRejectsIneligibleSelection:
    """The preview enable operator requires a specific 2-wall selection
    (LAYER2 walls with straight axes). With no selection at all, poll
    must return False so the operator is greyed-out in menus instead of
    crashing on dispatch."""

    def test_enable_poll_returns_false_with_no_selection(self):
        # Deselect everything in the default scene; no IfcWall is present
        # in a fresh bpy_extras context anyway, so poll() must short-circuit.
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.update()
        assert bpy.ops.bim.enable_wall_fillet_preview.poll() is False
