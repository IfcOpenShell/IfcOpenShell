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

import bonsai.core.misc as subject
from test.core.bootstrap import misc, ifc


class TestResizeToStorey:
    def test_run(self, misc, ifc):
        misc.get_object_storey("obj").should_be_called().will_return("storey")
        misc.get_storey_elevation_in_si("storey").should_be_called().will_return("elevation")
        misc.get_storey_height_in_si("storey", 1).should_be_called().will_return("height")
        misc.set_object_origin_to_bottom("obj").should_be_called()
        misc.move_object_to_elevation("obj", "elevation").should_be_called()
        misc.scale_object_to_height("obj", "height").should_be_called()
        ifc.edit("obj").should_be_called()
        subject.resize_to_storey(misc, ifc, obj="obj", total_storeys=1)

    def test_doing_nothing_when_the_object_has_no_storey(self, misc, ifc):
        misc.get_object_storey("obj").should_be_called().will_return(None)
        subject.resize_to_storey(misc, ifc, obj="obj", total_storeys=1)

    def test_doing_nothing_when_the_storey_has_no_height(self, misc, ifc):
        misc.get_object_storey("obj").should_be_called().will_return("storey")
        misc.get_storey_height_in_si("storey", 1).should_be_called().will_return(None)
        subject.resize_to_storey(misc, ifc, obj="obj", total_storeys=1)
