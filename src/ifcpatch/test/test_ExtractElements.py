# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import os
import pytest
import ifcpatch
import ifcopenshell


class TestExtractElements:
    def test_getting_the_psets_of_a_product_as_a_dictionary(self):
        ifc = ifcopenshell.open(os.path.join(os.getcwd(), "test", "files", "basic.ifc"))
        output = ifcpatch.execute({"input": ifc, "recipe": "ExtractElements", "arguments": [".IfcWall"]})
        assert output.by_type("IfcWall")
        assert not output.by_type("IfcSlab")
