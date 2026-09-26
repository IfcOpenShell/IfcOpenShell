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
#
# This file was generated with the assistance of an AI coding tool.

import pytest

import bonsai
import bonsai.core.covering as subject
import bonsai.core.tool
from test.core.bootstrap import Prophecy, ifc, root, spatial

# NOTE: The Prophecy mocking framework serialises call arguments as JSON,
# which means shapely geometry objects cannot be passed through mocked
# calls.  We use the plain integer 42 as a serialisable stand-in for the
# polygon return value; the test verifies the unpack behaviour (that the
# polygon-like scalar 42 reaches set_covering_representation_from_polygon
# instead of the tuple (42, []) which old code would have passed).


@pytest.fixture
def covering():
    prophet = Prophecy(bonsai.core.tool.Covering)
    yield prophet
    prophet.verify()


class TestAddInstanceFlooringCoveringFromCursor:
    def test_run(self, ifc, root, spatial):
        root.get_default_container().should_be_called().will_return("container")
        spatial.get_active_obj().should_be_called().will_return(None)
        spatial.get_selected_objects().should_be_called().will_return([])
        spatial.get_relating_type_id().should_be_called().will_return(0)
        spatial.get_x_y_z_h_mat_from_cursor().should_be_called().will_return((0, 0, 0, 3, None))

        spatial.get_space_polygon_from_context_visible_objects(0, 0).should_be_called().will_return((42, []))
        spatial.create_object("Covering").should_be_called().will_return("mock_obj")
        spatial.set_obj_origin_to_cursor_position_and_zero_elevation("mock_obj").should_be_called()
        spatial.translate_obj_to_z_location("mock_obj", 0).should_be_called()
        spatial.assign_type_to_obj("mock_obj").should_be_called()
        spatial.set_covering_representation_from_polygon("mock_obj", 42, polygon_is_si=True).should_be_called()

        subject.add_instance_flooring_covering_from_cursor(ifc, root, spatial)

    def test_raises_when_no_default_container(self, ifc, root, spatial):
        root.get_default_container().should_be_called().will_return(None)
        with pytest.raises(subject.NoDefaultContainer):
            subject.add_instance_flooring_covering_from_cursor(ifc, root, spatial)


class TestAddInstanceCeilingCoveringFromCursor:
    def test_run(self, ifc, root, covering, spatial):
        root.get_default_container().should_be_called().will_return("container")
        spatial.get_active_obj().should_be_called().will_return(None)
        spatial.get_selected_objects().should_be_called().will_return([])
        spatial.get_relating_type_id().should_be_called().will_return(0)
        covering.get_z_from_ceiling_height().should_be_called().will_return(3.0)
        spatial.get_x_y_z_h_mat_from_cursor().should_be_called().will_return((0, 0, 0, 3, None))

        spatial.get_space_polygon_from_context_visible_objects(0, 0).should_be_called().will_return((42, []))
        spatial.create_object("Covering").should_be_called().will_return("mock_obj")
        spatial.set_obj_origin_to_cursor_position_and_zero_elevation("mock_obj").should_be_called()
        spatial.translate_obj_to_z_location("mock_obj", 3.0).should_be_called()
        spatial.assign_type_to_obj("mock_obj").should_be_called()
        spatial.set_covering_representation_from_polygon("mock_obj", 42, polygon_is_si=True).should_be_called()

        subject.add_instance_ceiling_covering_from_cursor(ifc, root, covering, spatial)

    def test_raises_when_no_default_container(self, ifc, root, covering, spatial):
        root.get_default_container().should_be_called().will_return(None)
        with pytest.raises(subject.NoDefaultContainer):
            subject.add_instance_ceiling_covering_from_cursor(ifc, root, covering, spatial)


class TestRegenSelectedCoveringObject:
    def test_run(self, root, spatial):
        root.get_default_container().should_be_called().will_return("container")
        spatial.get_active_obj().should_be_called().will_return("active")
        spatial.get_selected_objects().should_be_called().will_return(["active"])
        spatial.get_x_y_z_h_mat_from_obj("active").should_be_called().will_return((2, 3, 1, 3, None))

        spatial.get_space_polygon_from_context_visible_objects(2, 3).should_be_called().will_return((42, []))
        spatial.set_covering_representation_from_polygon("active", 42, polygon_is_si=True).should_be_called()

        subject.regen_selected_covering_object(root, spatial)

    def test_raises_when_no_default_container(self, root, spatial):
        root.get_default_container().should_be_called().will_return(None)
        with pytest.raises(subject.NoDefaultContainer):
            subject.regen_selected_covering_object(root, spatial)

    def test_raises_when_no_active_selected(self, root, spatial):
        root.get_default_container().should_be_called().will_return("container")
        spatial.get_active_obj().should_be_called().will_return(None)
        spatial.get_selected_objects().should_be_called().will_return([])
        with pytest.raises(AssertionError):
            subject.regen_selected_covering_object(root, spatial)
