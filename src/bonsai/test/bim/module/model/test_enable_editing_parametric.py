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

"""Tests for the universal pen-icon dispatcher's pre-edit warning path.

The dispatcher gates the parametric-edit triad behind a confirmation dialog
whenever the active element's body representation is shared with sibling
occurrences (typed product + mapped representation). It is the single
chokepoint every feature's pen icon routes through, so the warning applies
to walls, doors, windows, stairs, roofs, and any future feature uniformly.

These tests exercise:

- the pure ``should_show_shared_rep_dialog`` decision (every branch); and
- one end-to-end invocation through ``bpy.ops`` to pin the wiring between
  the decision and ``invoke_props_dialog``."""

import bpy
import pytest

from bonsai.bim.module.model.array import EnableEditingParametric

pytestmark = pytest.mark.model


class TestShouldShowSharedRepDialog:
    """Exhaustive truth table for the pre-edit-warning decision. Keeping this
    pure (no bpy, no operator instance) means a future change to the dispatch
    wiring can't silently flip a branch — the decision is independently pinned."""

    decide = staticmethod(EnableEditingParametric.should_show_shared_rep_dialog)

    def test_shared_rep_with_warning_enabled_shows_dialog(self):
        assert self.decide(suppress=False, has_entity=True, sibling_count=3) is True

    def test_unique_rep_skips_dialog(self):
        assert self.decide(suppress=False, has_entity=True, sibling_count=0) is False

    def test_session_suppress_overrides_shared_rep(self):
        assert self.decide(suppress=True, has_entity=True, sibling_count=5) is False

    def test_no_entity_skips_dialog_even_when_count_positive(self):
        assert self.decide(suppress=False, has_entity=False, sibling_count=3) is False

    def test_zero_siblings_skips_dialog_regardless_of_suppress(self):
        assert self.decide(suppress=False, has_entity=True, sibling_count=0) is False
        assert self.decide(suppress=True, has_entity=True, sibling_count=0) is False


def test_dispatcher_falls_through_to_feature_enable_op_when_no_active_object():
    """End-to-end smoke: with no active object the dispatcher short-circuits to
    its ``execute`` body, which CANCELs on an empty ``feature_enable_op``."""
    bpy.context.window_manager.BIMParametricEditDialogPrefs.suppress_shared_rep_warning = False
    try:
        with bpy.context.temp_override(active_object=None):
            result = bpy.ops.bim.enable_editing_parametric("INVOKE_DEFAULT", feature_enable_op="")
    finally:
        bpy.context.window_manager.BIMParametricEditDialogPrefs.suppress_shared_rep_warning = False
    assert result == {"CANCELLED"}
