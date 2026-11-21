# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Bonsai Contributors
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.root

import ifcpatch
import test.bootstrap


class TestAssignConstituentFractionsIFC2X3(test.bootstrap.IFC2X3):
    def test_run_is_a_no_op_since_constituent_sets_do_not_exist_in_ifc2x3(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")

        ifcpatch.execute(
            {"input": "input.ifc", "file": self.file, "recipe": "AssignConstituentFractions", "arguments": []}
        )

        assert element.Name is None
