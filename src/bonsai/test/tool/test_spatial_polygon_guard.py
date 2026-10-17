# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

# This file was generated with the assistance of an AI coding tool.

from unittest import mock

import shapely

from bonsai.tool.spatial import Spatial as subject
from test.bim.bootstrap import NewFile


class TestGetSpacePolygonFromContextVisibleObjects(NewFile):
    def test_boundary_lines_collapsing_to_one_piece_returns_no_polygons_found(self):
        single_line = [shapely.LineString([(0.0, 0.0), (5.0, 0.0)])]
        with mock.patch.object(subject, "get_boundary_lines_from_context_visible_objects", return_value=single_line):
            result = subject.get_space_polygon_from_context_visible_objects(1.0, 1.0)
        assert result == "NO POLYGONS FOUND"
