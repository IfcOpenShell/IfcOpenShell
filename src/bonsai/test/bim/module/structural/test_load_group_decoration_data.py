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

import ifcopenshell
import ifcopenshell.guid

import bonsai.tool as tool
from bonsai.bim.module.structural.data import LoadGroupDecorationData
from test.bim.bootstrap import NewFile


class TestExternalReactionGroupWithoutLoadGroup(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        group = ifc.createIfcStructuralResultGroup(
            GlobalId=ifcopenshell.guid.new(), Name="Results", TheoryType="FIRST_ORDER_THEORY", IsLinear=False
        )
        ifc.createIfcStructuralAnalysisModel(
            GlobalId=ifcopenshell.guid.new(), Name="Model", PredefinedType="LOADING_3D", HasResults=[group]
        )
        tool.Structural.get_structural_props().activity_type = "External Reaction"
        items = LoadGroupDecorationData.load_groups_to_show()
        assert [name for _, name, _ in items] == ["Results "]
