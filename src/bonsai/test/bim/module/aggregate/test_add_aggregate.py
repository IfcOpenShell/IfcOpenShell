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

import bpy
import pytest

from test.bim.bootstrap import NewFile


class TestAddAggregate(NewFile):
    def test_adding_a_storey_to_an_element_assembly_reports_an_error_instead_of_raising(self):
        bpy.ops.bim.create_project()
        storey = bpy.data.objects["IfcBuildingStorey/My Storey"]
        bpy.context.view_layer.objects.active = storey
        storey.select_set(True)
        with pytest.raises(RuntimeError, match="Cannot aggregate IfcBuildingStorey/My Storey to"):
            bpy.ops.bim.add_aggregate(ifc_class="IfcElementAssembly", aggregate_name="Assembly")
