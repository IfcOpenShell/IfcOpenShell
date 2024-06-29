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

import ifcpatch
import ifcopenshell
import ifcopenshell.api.georeference
import ifcopenshell.util.placement
import test.bootstrap
import tempfile
import numpy as np
from pathlib import Path
from typing import Optional


class TestMergeProject(test.bootstrap.IFC4):
    def setup_project(self, ifc_file: Optional[ifcopenshell.file] = None):
        prefix = None if ifc_file else "MILLI"
        if ifc_file is None:
            ifc_file = ifcopenshell.file(schema=self.file.schema)

        ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcProject")
        unit = ifcopenshell.api.run("unit.add_si_unit", ifc_file, unit_type="LENGTHUNIT", prefix=prefix)
        ifcopenshell.api.run("unit.assign_unit", ifc_file, units=[unit])
        model = ifcopenshell.api.context.add_context(ifc_file, "Model")
        ifcopenshell.api.context.add_context(ifc_file, "Model", "Body", "MODEL_VIEW", parent=model)

        matrix = np.eye(4)
        matrix[:, 3] = (1, 2, 3, 1)
        wall = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcWall")
        ifcopenshell.api.run("geometry.edit_object_placement", ifc_file, product=wall, matrix=matrix, is_si=True)
        return ifc_file

    def test_run(self):
        self.file = self.setup_project(self.file)
        second_file = self.setup_project()
        temp_path = Path(tempfile.gettempdir()) / "second.ifc"
        second_file.write(temp_path)
        output = ifcpatch.execute({"file": self.file, "recipe": "MergeProject", "arguments": [str(temp_path)]})

        assert self.file == output
        assert len(output.by_type("IfcWall")) == 2
        wall1, wall2 = output.by_type("IfcWall")

        # test that units are converted
        placement1 = ifcopenshell.util.placement.get_local_placement(wall1.ObjectPlacement)
        placement2 = ifcopenshell.util.placement.get_local_placement(wall2.ObjectPlacement)
        to_tuple = lambda arr: tuple(map(tuple, arr))
        matrix = np.eye(4)
        matrix[:, 3] = (1, 2, 3, 1)
        assert to_tuple(placement1) == to_tuple(placement2) == to_tuple(matrix)

    def test_reusing_geometric_contexts(self):
        self.file = self.setup_project(self.file)
        second_file = self.setup_project()
        output = ifcpatch.execute({"file": self.file, "recipe": "MergeProject", "arguments": [second_file]})
        assert len(output.by_type("IfcGeometricRepresentationContext")) == 2

    def test_using_the_georeferencing_of_the_original_project(self):
        if self.file.schema == "IFC2X3":
            return
        self.file = self.setup_project(self.file)
        second_file = self.setup_project()
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.add_georeferencing(second_file)
        output = ifcpatch.execute({"file": self.file, "recipe": "MergeProject", "arguments": [second_file]})
        assert len(output.by_type("IfcProjectedCRS")) == 1
        assert len(output.by_type("IfcMapConversion")) == 1

    def test_shifting_the_source_project_to_match_the_original_project_origin(self):
        self.file = self.setup_project(self.file)
        second_file = self.setup_project()
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file, coordinate_operation={"Eastings": 10, "Northings": 20}, projected_crs={"Name": "EPSG:1234"}
        )
        ifcopenshell.api.georeference.add_georeferencing(second_file)
        ifcopenshell.api.georeference.edit_georeferencing(
            second_file, coordinate_operation={"Eastings": 30000, "Northings": 40000}, projected_crs={"Name": "EPSG:0"}
        )

        # Original file is in meters
        wall1 = self.file.by_type("IfcWall")[0]
        m1 = ifcopenshell.util.placement.get_local_placement(wall1.ObjectPlacement)
        assert np.allclose(m1[:, 3], (1, 2, 3, 1))
        global_m1 = ifcopenshell.util.geolocation.auto_local2global(self.file, m1, should_return_in_map_units=False)
        assert np.allclose(global_m1[:, 3], (11, 22, 3, 1))

        # Second file is in millimeters with a different false origin
        wall1 = second_file.by_type("IfcWall")[0]
        m1 = ifcopenshell.util.placement.get_local_placement(wall1.ObjectPlacement)
        assert np.allclose(m1[:, 3], (1000, 2000, 3000, 1))
        global_m1 = ifcopenshell.util.geolocation.auto_local2global(second_file, m1, should_return_in_map_units=False)
        assert np.allclose(global_m1[:, 3], (31000, 42000, 3000, 1))

        output = ifcpatch.execute({"file": self.file, "recipe": "MergeProject", "arguments": [second_file]})

        # In the future we may use proj to support reprojection from different CRSes. For now... nope!
        if self.file.schema != "IFC2X3":
            assert output.by_type("IfcProjectedCRS")[0].Name == "EPSG:1234"

        # The results should be in meters with the false origin of the original file
        params = ifcopenshell.util.geolocation.get_helmert_transformation_parameters(output)
        assert params.e == 10
        assert params.n == 20
        wall1, wall2 = output.by_type("IfcWall")
        m1 = ifcopenshell.util.placement.get_local_placement(wall1.ObjectPlacement)
        m2 = ifcopenshell.util.placement.get_local_placement(wall2.ObjectPlacement)
        assert np.allclose(m1[:, 3], (1, 2, 3, 1))
        assert np.allclose(m2[:, 3], (21, 22, 3, 1))


class TestMergeProjectIFC2X3(test.bootstrap.IFC2X3, TestMergeProject):
    pass
