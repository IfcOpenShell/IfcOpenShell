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

import os

import ifcopenshell.api.aggregate
import ifcopenshell.api.root

import ifcpatch
import test.bootstrap


class TestSplitByBuildingStorey(test.bootstrap.IFC4):
    def test_run_with_default_output_dir(self, tmp_path, monkeypatch):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[site], relating_object=project)
        storey = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey", name="Level1")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[storey], relating_object=site)

        monkeypatch.chdir(tmp_path)
        ifcpatch.execute({"file": self.file, "recipe": "SplitByBuildingStorey", "arguments": [None]})
        assert (tmp_path / "0-Level1.ifc").is_file()

    def test_run_with_explicit_output_dir(self, tmp_path):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[site], relating_object=project)
        storey = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey", name="Level1")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[storey], relating_object=site)

        output_dir = os.path.join(tmp_path, "out")
        ifcpatch.execute({"file": self.file, "recipe": "SplitByBuildingStorey", "arguments": [output_dir]})
        assert os.path.isfile(os.path.join(output_dir, "0-Level1.ifc"))


class TestSplitByBuildingStoreyIFC2X3(test.bootstrap.IFC2X3, TestSplitByBuildingStorey):
    pass
