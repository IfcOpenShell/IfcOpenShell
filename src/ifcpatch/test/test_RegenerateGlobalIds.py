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
import ifcopenshell.api
import ifcopenshell.api.root
import ifcopenshell.util.element
import test.bootstrap


class TestRegenerateGlobalIds(test.bootstrap.IFC4):
    def test_run(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        used_guids = {project.GlobalId, wall.GlobalId}
        ifcpatch.execute({"file": self.file, "recipe": "RegenerateGlobalIds", "arguments": [False]})
        new_guids = {project.GlobalId, wall.GlobalId}
        assert not new_guids.intersection(used_guids)

    def test_regenerate_guids_for_duplicates(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        wall1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall1.GlobalId = wall2.GlobalId
        used_guids = {project, wall1.GlobalId, wall2.GlobalId}

        ifcpatch.execute({"file": self.file, "recipe": "RegenerateGlobalIds", "arguments": [True]})
        new_guids = {project, wall1.GlobalId, wall2.GlobalId}
        assert len(new_guids) == 3
        assert len(new_guids.intersection(used_guids)) == 2


class TestRegenerateGlobalIdsIFC2X3(test.bootstrap.IFC2X3, TestRegenerateGlobalIds):
    pass
