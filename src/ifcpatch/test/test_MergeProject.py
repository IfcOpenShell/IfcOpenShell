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
import ifcopenshell.api
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

        project = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcProject")
        unit = ifcopenshell.api.run("unit.add_si_unit", ifc_file, unit_type="LENGTHUNIT", prefix=prefix)
        ifcopenshell.api.run("unit.assign_unit", ifc_file, units=[unit])

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

        assert len(output.by_type("IfcWall")) == 2
        wall1, wall2 = output.by_type("IfcWall")

        # test that units are converted
        placement1 = ifcopenshell.util.placement.get_local_placement(wall1.ObjectPlacement)
        placement2 = ifcopenshell.util.placement.get_local_placement(wall2.ObjectPlacement)
        to_tuple = lambda arr: tuple(map(tuple, arr))
        matrix = np.eye(4)
        matrix[:, 3] = (1, 2, 3, 1)
        assert to_tuple(placement1) == to_tuple(placement2) == to_tuple(matrix)


class TestMergeProjectIFC2X3(test.bootstrap.IFC2X3, TestMergeProject):
    pass
