# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.api.aggregate
import ifcopenshell.api.geometry
import ifcopenshell.api.root

import ifcpatch
import test.bootstrap


class TestOffsetStoreyElevations(test.bootstrap.IFC4):
    def test_run(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        storey = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey")
        ifcopenshell.api.aggregate.assign_object(self.file, relating_object=project, products=[site])
        ifcopenshell.api.aggregate.assign_object(self.file, relating_object=site, products=[storey])
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=storey, matrix=np.eye(4))

        ifcpatch.execute({"file": self.file, "recipe": "OffsetStoreyElevations", "arguments": [5]})

        assert storey.Elevation == 5
        assert storey.ObjectPlacement.RelativePlacement.Location.Coordinates[2] == 5

    def test_skips_storey_without_object_placement_instead_of_crashing(self):
        # Regression test: a storey with no ObjectPlacement (common when a
        # storey is authored without geometry) used to raise
        # AttributeError: 'NoneType' object has no attribute
        # 'RelativePlacement', aborting the whole patch.
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        storey_with_placement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey")
        storey_without_placement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey")
        ifcopenshell.api.aggregate.assign_object(self.file, relating_object=project, products=[site])
        ifcopenshell.api.aggregate.assign_object(
            self.file, relating_object=site, products=[storey_with_placement, storey_without_placement]
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=storey_with_placement, matrix=np.eye(4))
        assert storey_without_placement.ObjectPlacement is None

        ifcpatch.execute({"file": self.file, "recipe": "OffsetStoreyElevations", "arguments": [5]})

        assert storey_with_placement.Elevation == 5
        assert storey_without_placement.ObjectPlacement is None


class TestOffsetStoreyElevationsIFC2X3(test.bootstrap.IFC2X3, TestOffsetStoreyElevations):
    pass
