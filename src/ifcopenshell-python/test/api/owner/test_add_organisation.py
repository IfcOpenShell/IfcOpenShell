# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api.owner


class TestAddOrganisation(test.bootstrap.IFC4):
    def test_adding_an_organisation(self):
        org = ifcopenshell.api.owner.add_organisation(self.file, identification="Id", name="Name")
        # 0 IfcOrganization Identification(>IFC2X3) / Id (IFC2X3)
        assert org[0] == "Id"
        assert org.Name == "Name"


class TestAddOrganisationIFC2X3(test.bootstrap.IFC2X3, TestAddOrganisation):
    pass
