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

import pytest

import ifcopenshell.api.aggregate
import ifcopenshell.api.root

import ifcpatch
import test.bootstrap


class TestRemoveSiteRepresentation(test.bootstrap.IFC4):
    def test_run(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        site = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSite")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[site], relating_object=project)
        site.Representation = self.file.create_entity("IfcProductDefinitionShape", Representations=[])
        ifcpatch.execute({"file": self.file, "recipe": "RemoveSiteRepresentation", "arguments": []})
        assert site.Representation is None

    def test_raises_on_missing_project(self):
        with pytest.raises(ValueError):
            ifcpatch.execute({"file": self.file, "recipe": "RemoveSiteRepresentation", "arguments": []})


class TestRemoveSiteRepresentationIFC2X3(test.bootstrap.IFC2X3, TestRemoveSiteRepresentation):
    pass
