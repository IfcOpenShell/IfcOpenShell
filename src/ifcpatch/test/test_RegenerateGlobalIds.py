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
import ifcopenshell.util.element


class TestRegenerateGlobalIds:
    def test_run(self):
        ifc_file = ifcopenshell.file()
        project = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcProject")
        wall = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcWall")
        used_guids = {project.GlobalId, wall.GlobalId}
        ifcpatch.execute({"file": ifc_file, "recipe": "RegenerateGlobalIds", "arguments": [False]})
        new_guids = {project.GlobalId, wall.GlobalId}
        assert not new_guids.intersection(used_guids)

    def test_regenerate_guids_for_duplicates(self):
        ifc_file = ifcopenshell.file()
        project = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcProject")
        wall1 = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.run("root.create_entity", ifc_file, ifc_class="IfcWall")
        wall1.GlobalId = wall2.GlobalId
        used_guids = {project, wall1.GlobalId, wall2.GlobalId}

        ifcpatch.execute({"file": ifc_file, "recipe": "RegenerateGlobalIds", "arguments": [True]})
        new_guids = {project, wall1.GlobalId, wall2.GlobalId}
        assert len(new_guids) == 3
        assert len(new_guids.intersection(used_guids)) == 2
