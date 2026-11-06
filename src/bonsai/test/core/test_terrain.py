# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Ryan Schultz
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

import bonsai.core.terrain as subject
from test.core.bootstrap import terrain  # ruff: ignore[unused-import]


class TestGenerateContours:
    def test_run(self, terrain):
        levels = [(4, "z4", "polylines4"), (5, "z5", "polylines5")]
        terrain.get_contour_levels("element", 0.5).should_be_called().will_return(levels)
        terrain.set_contour_settings("element", 0.5, 5).should_be_called()
        terrain.get_contours("element").should_be_called().will_return([])
        terrain.create_contour("element", 2.0, "z4", "polylines4", False).should_be_called()
        terrain.create_contour("element", 2.5, "z5", "polylines5", True).should_be_called()
        assert subject.generate_contours(terrain, "element", interval=0.5, index_interval=5) == 2

    def test_existing_contours_are_reused_by_elevation_and_stale_ones_removed(self, terrain):
        levels = [(4, "z4", "polylines4"), (5, "z5", "polylines5")]
        terrain.get_contour_levels("element", 0.5).should_be_called().will_return(levels)
        terrain.set_contour_settings("element", 0.5, 5).should_be_called()
        terrain.get_contours("element").should_be_called().will_return(["at2", "at9", "unknown"])
        terrain.get_contour_elevation("at2").should_be_called().will_return(2.0000000001)
        terrain.get_contour_elevation("at9").should_be_called().will_return(9.0)
        terrain.get_contour_elevation("unknown").should_be_called().will_return(None)
        terrain.remove_contour("unknown").should_be_called()
        terrain.update_contour("at2", "element", 2.0, "z4", "polylines4", False).should_be_called()
        terrain.create_contour("element", 2.5, "z5", "polylines5", True).should_be_called()
        terrain.remove_contour("at9").should_be_called()
        subject.generate_contours(terrain, "element", interval=0.5, index_interval=5)

    def test_no_index_contours_when_index_interval_is_zero(self, terrain):
        terrain.get_contour_levels("element", 1.0).should_be_called().will_return([(0, "z0", "polylines0")])
        terrain.set_contour_settings("element", 1.0, 0).should_be_called()
        terrain.get_contours("element").should_be_called().will_return([])
        terrain.create_contour("element", 0.0, "z0", "polylines0", False).should_be_called()
        subject.generate_contours(terrain, "element", interval=1.0, index_interval=0)


class TestUpdateContours:
    def test_run(self, terrain):
        terrain.get_contour_settings("element").should_be_called().will_return((2.0, 5))
        terrain.get_contour_levels("element", 2.0).should_be_called().will_return([])
        terrain.set_contour_settings("element", 2.0, 5).should_be_called()
        terrain.get_contours("element").should_be_called().will_return([])
        assert subject.update_contours(terrain, "element") == 0

    def test_nothing_happens_without_saved_settings(self, terrain):
        terrain.get_contour_settings("element").should_be_called().will_return(None)
        assert subject.update_contours(terrain, "element") == 0


class TestRemoveContours:
    def test_run(self, terrain):
        terrain.get_contours("element").should_be_called().will_return(["a", "b"])
        terrain.remove_contour("a").should_be_called()
        terrain.remove_contour("b").should_be_called()
        terrain.remove_contour_settings("element").should_be_called()
        subject.remove_contours(terrain, "element")


class TestLabelContours:
    def test_run(self, terrain):
        terrain.get_contours("element").should_be_called().will_return(["contour"])
        terrain.get_contour_labels("contour", "drawing").should_be_called().will_return(["moved", "generated"])
        terrain.is_label_moved("moved").should_be_called().will_return(True)
        terrain.is_label_moved("generated").should_be_called().will_return(False)
        terrain.remove_contour_label("generated").should_be_called()
        terrain.get_label_template("element").should_be_called().will_return("template")
        terrain.get_label_placements("element", "drawing", "type", 15.0, ["moved"]).should_be_called().will_return(
            [("contour", "matrix1"), ("contour", "matrix2")]
        )
        terrain.create_contour_label("drawing", "contour", "matrix1", "type", "template").should_be_called()
        terrain.create_contour_label("drawing", "contour", "matrix2", "type", "template").should_be_called()
        assert subject.label_contours(terrain, "element", "drawing", relating_type="type", spacing=15.0) == 2
