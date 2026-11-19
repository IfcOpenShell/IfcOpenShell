# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

from unittest.mock import patch

import ifcopenshell
import pytest

import bonsai.core.spatial
import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.geometry


class TestRefreshLinkedAggregateContainer(NewFile):
    def test_skips_assign_container_when_original_container_is_none(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.create_entity("IfcWall")
        assert ifcopenshell.util.element.get_aggregate(wall) is None

        original_data = {
            1: {
                0: {
                    "Name": "Wall_01",
                    "Aggregate_Index": 0,
                    "Assignment": [],
                    "Container": None,
                }
            }
        }
        container = original_data[1][0]["Container"]

        with patch.object(bonsai.core.spatial, "assign_container") as mock_assign:
            if container and not ifcopenshell.util.element.get_aggregate(wall):
                bonsai.core.spatial.assign_container(
                    tool.Ifc,
                    tool.Collector,
                    tool.Spatial,
                    container=container,
                    objs=[],
                )

        mock_assign.assert_not_called()
