# This file was generated with the assistance of an AI coding tool.
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

import bpy
import pytest

from test.bim.bootstrap import NewFile


class TestOperatorPollsWithoutInput(NewFile):
    @pytest.mark.parametrize(
        "operator",
        [
            "covetool_run_simple_analysis",
            "covetool_run_analysis",
            "visualise_diff",
            "select_diff_objects",
            "convert_cityjson2ifc",
            "find_cityjson_lod",
        ],
    )
    def test_run(self, operator):
        assert not getattr(bpy.ops.bim, operator).poll()
