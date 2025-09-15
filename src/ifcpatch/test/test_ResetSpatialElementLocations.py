# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Dion Moult <dion@thinkmoult.com>
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

import test.bootstrap
import ifcopenshell.api
import ifcopenshell.api.aggregate
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.placement
import ifcpatch
import numpy as np


class TestResetSpatialElementLocations(test.bootstrap.IFC4):
    def test_run(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[site], relating_object=project)
        m = np.eye(4)
        m[0][3] = 42.0
        m[2][3] = 42.0
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=site, matrix=m)
        ifcpatch.execute(
            {"file": self.file, "recipe": "ResetSpatialElementLocations", "arguments": ["IfcBuilding", False]}
        )
        m2 = ifcopenshell.util.placement.get_local_placement(site.ObjectPlacement)
        assert np.allclose(m, m2)
        ifcpatch.execute({"file": self.file, "recipe": "ResetSpatialElementLocations", "arguments": ["IfcSite", False]})
        m2 = ifcopenshell.util.placement.get_local_placement(site.ObjectPlacement)
        assert np.allclose(m2, np.eye(4))
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=site, matrix=m)
        ifcpatch.execute({"file": self.file, "recipe": "ResetSpatialElementLocations", "arguments": ["", False]})
        m2 = ifcopenshell.util.placement.get_local_placement(site.ObjectPlacement)
        assert np.allclose(m2, np.eye(4))

        m = np.eye(4)
        m2 = np.eye(4)
        m[0][3] = 42.0
        m[1][3] = 42.0
        m[2][3] = m2[2][3] = 42.0
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=site, matrix=m)
        ifcpatch.execute({"file": self.file, "recipe": "ResetSpatialElementLocations", "arguments": ["", True]})
        m = ifcopenshell.util.placement.get_local_placement(site.ObjectPlacement)
        assert np.allclose(m, m2)


class TestResetSpatialElementLocationsIFC2X3(test.bootstrap.IFC2X3, TestResetSpatialElementLocations):
    pass
