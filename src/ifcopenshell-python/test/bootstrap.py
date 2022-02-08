# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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

import pytest
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.owner.settings


class IFC4:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.file = ifcopenshell.api.run("project.create_file")
        ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
        ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]


class IFC2X3:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.file = ifcopenshell.api.run("project.create_file", version="IFC2X3")
        ifcopenshell.api.owner.settings.get_user = lambda ifc: ifc.createIfcPersonAndOrganization()
        ifcopenshell.api.owner.settings.get_application = lambda ifc: ifc.createIfcApplication()
