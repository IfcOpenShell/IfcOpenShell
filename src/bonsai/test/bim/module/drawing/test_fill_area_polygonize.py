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

"""Regression test for CreateDrawing's SHAPELY fill-area shapely guard.

shapely.union_all returns a scalar LineString (no .geoms) instead of a
MultiLineString when the boundary lines collapse to one connected piece,
which used to crash the SVG fill-area pass with AttributeError."""

import pytest
import shapely

pytestmark = pytest.mark.drawing


def test_single_boundary_line_yields_no_fill_polygons():
    from bonsai.bim.module.drawing.operator import polygonize_boundary_lines

    single_line = [shapely.LineString([[0.0, 0.0], [120.0, 0.0]])]
    result = polygonize_boundary_lines(single_line)
    assert list(result.geoms) == []


def test_closed_loop_still_yields_a_polygon():
    closed_loop = [
        shapely.LineString([[0, 0], [5, 0]]),
        shapely.LineString([[5, 0], [5, 3]]),
        shapely.LineString([[5, 3], [0, 3]]),
        shapely.LineString([[0, 3], [0, 0]]),
    ]
    from bonsai.bim.module.drawing.operator import polygonize_boundary_lines

    result = polygonize_boundary_lines(closed_loop)
    assert len(list(result.geoms)) == 1
