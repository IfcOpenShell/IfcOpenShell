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


class TestAddApplication(test.bootstrap.IFC4):
    def test_adding_the_ifcopenshell_application(self):
        application = ifcopenshell.api.owner.add_application(self.file)
        developer = application.ApplicationDeveloper
        assert application.Version == ifcopenshell.version
        assert application.ApplicationFullName == "IfcOpenShell"
        assert application.ApplicationIdentifier == "IfcOpenShell"
        assert developer.is_a("IfcOrganization")
        # 0 IfcOrganization Identification(>IFC2X3) / Id (IFC2X3)
        assert developer[0] == "IfcOpenShell"
        assert developer.Name == "IfcOpenShell"
        assert (
            developer.Description
            == "IfcOpenShell is an open source software library that helps users and software developers to work with IFC data."
        )
        assert developer.Roles[0].Role == "USERDEFINED"
        assert developer.Roles[0].UserDefinedRole == "CONTRIBUTOR"
        assert developer.Addresses[0].is_a("IfcTelecomAddress")
        assert developer.Addresses[0].Purpose == "USERDEFINED"
        assert developer.Addresses[0].UserDefinedPurpose == "WEBPAGE"
        assert developer.Addresses[0].WWWHomePageURL == "https://ifcopenshell.org"


class TestAddApplicationIFC2X3(test.bootstrap.IFC2X3, TestAddApplication):
    pass
