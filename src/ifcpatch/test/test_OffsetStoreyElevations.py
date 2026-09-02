# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

# This file was generated with the assistance of an AI coding tool.

import numpy as np
import pytest

import ifcopenshell.api.aggregate
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.unit

import ifcpatch
import test.bootstrap


class TestOffsetStoreyElevations(test.bootstrap.IFC4):
    def test_run(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[site], relating_object=project)
        storey = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[storey], relating_object=site)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=storey, matrix=np.eye(4))
        ifcpatch.execute({"file": self.file, "recipe": "OffsetStoreyElevations", "arguments": [5]})
        assert storey.ObjectPlacement.RelativePlacement.Location.Coordinates == (0.0, 0.0, 5.0)
        assert storey.Elevation == 5.0

    def test_raises_on_missing_project(self):
        with pytest.raises(ValueError):
            ifcpatch.execute({"file": self.file, "recipe": "OffsetStoreyElevations", "arguments": [5]})


class TestOffsetStoreyElevationsIFC2X3(test.bootstrap.IFC2X3, TestOffsetStoreyElevations):
    pass
