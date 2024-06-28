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


class TestRemoveAddress(test.bootstrap.IFC4):
    def test_removing_an_address(self):
        postal = self.file.createIfcPostalAddress()
        telecom = self.file.createIfcTelecomAddress()
        ifcopenshell.api.owner.remove_address(self.file, address=postal)
        ifcopenshell.api.owner.remove_address(self.file, address=telecom)
        assert len(self.file.by_type("IfcAddress")) == 0

    def test_ensuring_organisation_cardinality_is_valid(self):
        address = self.file.createIfcPostalAddress()
        organisation = self.file.createIfcOrganization()
        organisation.Addresses = [address]
        ifcopenshell.api.owner.remove_address(self.file, address=address)
        assert organisation.Addresses is None

    def test_ensuring_person_cardinality_is_valid(self):
        address = self.file.createIfcPostalAddress()
        person = self.file.createIfcPerson()
        person.Addresses = [address]
        ifcopenshell.api.owner.remove_address(self.file, address=address)
        assert person.Addresses is None


class TestRemoveAddressIFC2X3(test.bootstrap.IFC2X3, TestRemoveAddress):
    pass
