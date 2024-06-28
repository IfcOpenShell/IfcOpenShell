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


class TestAddAddress(test.bootstrap.IFC4):
    def test_adding_to_a_person(self):
        person = self.file.createIfcPerson()
        postal = ifcopenshell.api.owner.add_address(self.file, assigned_object=person, ifc_class="IfcPostalAddress")
        telecom = ifcopenshell.api.owner.add_address(self.file, assigned_object=person, ifc_class="IfcTelecomAddress")
        assert postal.is_a("IfcPostalAddress")
        assert telecom.is_a("IfcTelecomAddress")
        assert postal.Purpose == telecom.Purpose == "OFFICE"
        assert postal in person.Addresses
        assert telecom in person.Addresses

    def test_adding_to_a_organisation(self):
        organisation = self.file.createIfcOrganization()
        postal = ifcopenshell.api.owner.add_address(
            self.file, assigned_object=organisation, ifc_class="IfcPostalAddress"
        )
        telecom = ifcopenshell.api.owner.add_address(
            self.file, assigned_object=organisation, ifc_class="IfcTelecomAddress"
        )
        assert postal.is_a("IfcPostalAddress")
        assert telecom.is_a("IfcTelecomAddress")
        assert postal.Purpose == telecom.Purpose == "OFFICE"
        assert postal in organisation.Addresses
        assert telecom in organisation.Addresses


class TestAddAddressIFC2X3(test.bootstrap.IFC2X3, TestAddAddress):
    pass
