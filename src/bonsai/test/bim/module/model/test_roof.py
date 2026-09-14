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

"""Regression test for the hipped roof footprint shapely guard.

A degenerate footprint (too few connected edges to close a polygon) used
to crash deep inside shapely with AttributeError or ValueError.
generate_hipped_roof_bmesh now raises a clear, user-facing ValueError
instead."""

import bmesh
import pytest

pytestmark = pytest.mark.model


def test_degenerate_footprint_raises_clear_error():
    from bonsai.bim.module.model.roof import generate_hipped_roof_bmesh

    bm = bmesh.new()
    try:
        v1 = bm.verts.new((0.0, 0.0, 0.0))
        v2 = bm.verts.new((5.0, 0.0, 0.0))
        bm.edges.new((v1, v2))

        with pytest.raises(ValueError, match="closed polygon"):
            generate_hipped_roof_bmesh(bm)
    finally:
        bm.free()
