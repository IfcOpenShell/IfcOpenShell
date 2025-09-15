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
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.util.element
import ifcopenshell.util.geolocation
import ifcopenshell.util.placement
import ifcpatch
import numpy as np


class TestSetFalseOrigin(test.bootstrap.IFC4):
    def test_run(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model3d = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d
        )
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        # ifcopenshell.api.georeference.add_georeferencing(self.file)
        # ifcopenshell.api.georeference.edit_georeferencing(self.file)
        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[site], relating_object=project)
        ifcopenshell.api.spatial.assign_container(self.file, products=[wall], relating_structure=site)
        m = np.eye(4)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=site, matrix=m)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall, matrix=m)
        ifcpatch.execute(
            {
                "file": self.file,
                "recipe": "SetFalseOrigin",
                "arguments": ["EPSG:1234", 5, 0, 0, 1000, 2000, 3000, 0, 0, True],
            }
        )
        if self.file.schema == "IFC2X3":
            assert (
                ifcopenshell.util.element.get_pset(self.file.by_type("IfcProject")[0], "ePSet_ProjectedCRS", "Name")
                == "EPSG:1234"
            )
        else:
            assert self.file.by_type("IfcProjectedCRS")[0].Name == "EPSG:1234"
        assert ifcopenshell.util.geolocation.auto_xyz2enh(self.file, 0, 0, 0) == (1000, 2000, 3000)
        m = ifcopenshell.util.placement.get_local_placement(site.ObjectPlacement)
        assert np.allclose(m, np.eye(4))
        m = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
        m2 = np.eye(4)
        m2[0][3] = -5
        assert np.allclose(m, m2)


class TestSetFalseOriginIFC2X3(test.bootstrap.IFC2X3, TestSetFalseOrigin):
    pass
