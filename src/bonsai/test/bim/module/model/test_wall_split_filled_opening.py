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

"""Pins two contracts in ``DumbWallJoiner.split``'s filled-opening branch:

1. Side classification reads the opening's axis-projected midpoint, not
   the filling's ``matrix_world.translation``. The filling origin is
   flip-fragile — flipping rotates the filler 180° + translates so the
   bbox stays visually in place, which would mis-classify a flipped door
   centred over the cut.
2. When the void straddles the cut and the filling moves to element2,
   the void copy for element1 is taken from the ORIGINAL opening (whose
   ``ObjectPlacement`` still references element1), not the rebound
   ``new_opening`` (whose ``PlacementRelTo`` was swapped to element2)."""

import inspect

import pytest

pytestmark = pytest.mark.wall


def _split_source():
    from bonsai.bim.module.model.wall import DumbWallJoiner

    return inspect.getsource(DumbWallJoiner.split)


def test_side_classification_uses_opening_midpoint_not_filling_origin():
    """Side classification must read the opening's axis-projected
    midpoint, not the filling's world translation — the latter shifts
    under flipping and would mis-classify a flipped door centred over
    the cut."""
    source = _split_source()
    assert "opening_midpoint" in source
    assert "filling_obj.matrix_world.translation" not in source


def test_void_copy_reads_from_original_opening_before_remove():
    """When the filling moves to element2 and the void straddles the
    cut, element1's pure-void copy must come from the original opening
    BEFORE the cleanup that destroys it — the rebound ``new_opening``
    references element2's frame and would shift the void to element1's
    origin in element2's local coords."""
    source = _split_source()
    branch_start = source.index("if opening_midpoint > cut_percentage:")
    branch = source[branch_start:]
    add_idx = branch.index("_add_void_copy(element1, opening)")
    remove_idx = branch.index("feature.remove_feature(tool.Ifc.get(), feature=opening)")
    assert add_idx < remove_idx
