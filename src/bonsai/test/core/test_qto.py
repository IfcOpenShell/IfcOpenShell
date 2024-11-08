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

import bonsai.core.qto as subject
from test.core.bootstrap import qto


class TestCalculateCircleRadius:
    def test_run(self, qto):
        qto.get_radius_of_selected_vertices("obj").should_be_called().will_return("radius")
        qto.set_qto_result("radius").should_be_called()
        assert subject.calculate_circle_radius(qto, obj="obj") == "radius"
