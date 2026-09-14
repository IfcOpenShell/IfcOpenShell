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

"""No-polygon covering creation should raise, not silently do nothing.

Without an enclosing polygon at the cursor, the three covering-from-cursor
core functions used to just ``return`` after computing ``space_polygon``,
leaving the user with no error and no created object. See NoPolygonFound.
"""

import pytest

import bonsai.core.covering as subject
from test.core.bootstrap import covering, ifc, root, spatial


class TestAddInstanceFlooringCoveringFromCursorNoPolygon:
    def test_raises_no_polygon_found(self, ifc, root, spatial):
        root.get_default_container().should_be_called().will_return("container")
        spatial.get_active_obj().should_be_called().will_return(None)
        spatial.get_selected_objects().should_be_called().will_return([])
        spatial.get_relating_type_id().should_be_called().will_return(None)
        spatial.get_x_y_z_h_mat_from_cursor().should_be_called().will_return((1, 2, 3, 4, "mat"))
        spatial.get_space_polygon_from_context_visible_objects(1, 2).should_be_called().will_return("NO POLYGONS FOUND")
        with pytest.raises(subject.NoPolygonFound):
            subject.add_instance_flooring_covering_from_cursor(ifc, root, spatial)


class TestAddInstanceCeilingCoveringFromCursorNoPolygon:
    def test_raises_no_polygon_found(self, ifc, root, covering, spatial):
        root.get_default_container().should_be_called().will_return("container")
        spatial.get_active_obj().should_be_called().will_return(None)
        spatial.get_selected_objects().should_be_called().will_return([])
        spatial.get_relating_type_id().should_be_called().will_return(None)
        spatial.get_x_y_z_h_mat_from_cursor().should_be_called().will_return((1, 2, 3, 4, "mat"))
        covering.get_z_from_ceiling_height().should_be_called().will_return(2.5)
        spatial.get_space_polygon_from_context_visible_objects(1, 2).should_be_called().will_return(
            "NO POLYGON FOR POINT"
        )
        with pytest.raises(subject.NoPolygonFound):
            subject.add_instance_ceiling_covering_from_cursor(ifc, root, covering, spatial)


class TestRegenSelectedCoveringObjectNoPolygon:
    def test_raises_no_polygon_found(self, root, spatial):
        root.get_default_container().should_be_called().will_return("container")
        spatial.get_active_obj().should_be_called().will_return("active_obj")
        spatial.get_selected_objects().should_be_called().will_return(["active_obj"])
        spatial.get_x_y_z_h_mat_from_obj("active_obj").should_be_called().will_return((1, 2, 3, 4, "mat"))
        spatial.get_space_polygon_from_context_visible_objects(1, 2).should_be_called().will_return("NO POLYGONS FOUND")
        with pytest.raises(subject.NoPolygonFound):
            subject.regen_selected_covering_object(root, spatial)
