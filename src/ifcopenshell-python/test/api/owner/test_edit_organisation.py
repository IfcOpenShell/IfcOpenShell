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


class TestEditOrganisation(test.bootstrap.IFC4):
    def test_editing_a_organisation(self):
        organisation = self.file.createIfcOrganization()
        attributes = {
            "Identification" if self.file.schema != "IFC2X3" else "Id": "Identification",
            "Name": "Name",
            "Description": "Description",
        }
        ifcopenshell.api.owner.edit_organisation(
            self.file,
            organisation=organisation,
            attributes=attributes,
        )
        for attr, value in attributes.items():
            assert getattr(organisation, attr) == value


class TestEditOrganisationIFC2X3(test.bootstrap.IFC2X3, TestEditOrganisation):
    pass


class TestEditOrganisationIFC4X3(test.bootstrap.IFC4X3, TestEditOrganisation):
    pass
