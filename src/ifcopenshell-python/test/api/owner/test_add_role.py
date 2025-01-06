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


class TestAddRole(test.bootstrap.IFC4):
    def test_adding_a_role_to_a_person(self):
        person = self.file.createIfcPerson()
        role = ifcopenshell.api.owner.add_role(self.file, assigned_object=person)
        assert role.is_a("IfcActorRole")
        assert role.Role == "ARCHITECT"
        assert person.Roles == (role,)

    def test_adding_a_role_to_an_organisation(self):
        organisation = self.file.createIfcOrganization()
        role = ifcopenshell.api.owner.add_role(self.file, assigned_object=organisation)
        assert role.is_a("IfcActorRole")
        assert role.Role == "ARCHITECT"
        assert organisation.Roles == (role,)


class TestAddRoleIFC2X3(test.bootstrap.IFC2X3, TestAddRole):
    pass
