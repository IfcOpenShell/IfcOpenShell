# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.


import bonsai.core.owner as subject
from test.core.bootstrap import ifc, owner


class TestAddPerson:
    def test_run(self, ifc):
        ifc.run("owner.add_person").should_be_called().will_return("person")
        assert subject.add_person(ifc) == "person"


class TestRemovePerson:
    def test_run(self, ifc):
        ifc.run("owner.remove_person", person="person").should_be_called()
        subject.remove_person(ifc, person="person")


class TestEnableEditingPerson:
    def test_run(self, owner):
        owner.set_person("person").should_be_called()
        owner.import_person_attributes().should_be_called()
        subject.enable_editing_person(owner, person="person")


class TestDisableEditingPerson:
    def test_run(self, owner):
        owner.clear_person().should_be_called()
        subject.disable_editing_person(owner)


class TestEditPerson:
    def test_run(self, ifc, owner):
        owner.get_person().should_be_called().will_return("person")
        owner.export_person_attributes().should_be_called().will_return("attributes")
        ifc.run("owner.edit_person", person="person", attributes="attributes").should_be_called()
        owner.clear_person().should_be_called()
        subject.edit_person(ifc, owner)


class TestAddPersonAttribute:
    def test_run(self, owner):
        owner.add_person_attribute("name").should_be_called()
        subject.add_person_attribute(owner, name="name")


class TestRemovePersonAttribute:
    def test_run(self, owner):
        owner.remove_person_attribute("name", "id").should_be_called()
        subject.remove_person_attribute(owner, name="name", id="id")


class TestAddRole:
    def test_run(self, ifc):
        ifc.run("owner.add_role", assigned_object="parent").should_be_called().will_return("role")
        assert subject.add_role(ifc, parent="parent") == "role"


class TestRemoveRole:
    def test_run(self, ifc):
        ifc.run("owner.remove_role", role="role").should_be_called()
        subject.remove_role(ifc, role="role")


class TestEnableEditingRole:
    def test_run(self, owner):
        owner.set_role("role").should_be_called()
        owner.import_role_attributes().should_be_called()
        subject.enable_editing_role(owner, role="role")


class TestDisableEditingRole:
    def test_run(self, owner):
        owner.clear_role().should_be_called()
        subject.disable_editing_role(owner)


class TestEditRole:
    def test_run(self, ifc, owner):
        owner.export_role_attributes().should_be_called().will_return("attributes")
        owner.get_role().should_be_called().will_return("role")
        ifc.run("owner.edit_role", role="role", attributes="attributes").should_be_called()
        owner.clear_role().should_be_called()
        subject.edit_role(ifc, owner)


class TestAddAddress:
    def test_run(self, ifc):
        ifc.run(
            "owner.add_address", assigned_object="parent", ifc_class="IfcPostalAddress"
        ).should_be_called().will_return("address")
        assert subject.add_address(ifc, parent="parent", ifc_class="IfcPostalAddress") == "address"


class TestRemoveAddress:
    def test_run(self, ifc):
        ifc.run("owner.remove_address", address="address").should_be_called()
        subject.remove_address(ifc, address="address")


class TestEnableEditingAddress:
    def test_run(self, owner):
        owner.set_address("address").should_be_called()
        owner.import_address_attributes().should_be_called()
        subject.enable_editing_address(owner, address="address")


class TestDisableEditingAddress:
    def test_run(self, owner):
        owner.clear_address().should_be_called()
        subject.disable_editing_address(owner)


class TestEditAddress:
    def test_run(self, ifc, owner):
        owner.get_address().should_be_called().will_return("address")
        owner.export_address_attributes().should_be_called().will_return("attributes")
        ifc.run("owner.edit_address", address="address", attributes="attributes").should_be_called()
        owner.clear_address().should_be_called()
        subject.edit_address(ifc, owner)


class TestAddAddressAttribute:
    def test_run(self, owner):
        owner.add_address_attribute("name").should_be_called()
        subject.add_address_attribute(owner, name="name")


class TestRemoveAddressAttribute:
    def test_run(self, owner):
        owner.remove_address_attribute("name", "id").should_be_called()
        subject.remove_address_attribute(owner, name="name", id="id")


class TestAddOrganisation:
    def test_run(self, ifc):
        ifc.run("owner.add_organisation").should_be_called().will_return("organisation")
        assert subject.add_organisation(ifc) == "organisation"


class TestRemoveOrganisation:
    def test_run(self, ifc):
        ifc.run("owner.remove_organisation", organisation="organisation").should_be_called()
        subject.remove_organisation(ifc, organisation="organisation")


class TestEnableEditingOrganisation:
    def test_run(self, owner):
        owner.set_organisation("organisation").should_be_called()
        owner.import_organisation_attributes().should_be_called()
        subject.enable_editing_organisation(owner, organisation="organisation")


class TestDisableEditingOrganisation:
    def test_run(self, owner):
        owner.clear_organisation().should_be_called()
        subject.disable_editing_organisation(owner)


class TestEditOrganisation:
    def test_run(self, ifc, owner):
        owner.get_organisation().should_be_called().will_return("organisation")
        owner.export_organisation_attributes().should_be_called().will_return("attributes")
        ifc.run("owner.edit_organisation", organisation="organisation", attributes="attributes").should_be_called()
        owner.clear_organisation().should_be_called()
        subject.edit_organisation(ifc, owner)


class TestAddPersonAndOrganisation:
    def test_run(self, ifc):
        ifc.run(
            "owner.add_person_and_organisation", person="person", organisation="organisation"
        ).should_be_called().will_return("person_and_organisation")
        assert (
            subject.add_person_and_organisation(ifc, person="person", organisation="organisation")
            == "person_and_organisation"
        )


class TestRemovePersonAndOrganisation:
    def test_run(self, ifc, owner):
        owner.get_user().should_be_called().will_return("user")
        ifc.run(
            "owner.remove_person_and_organisation", person_and_organisation="person_and_organisation"
        ).should_be_called()
        subject.remove_person_and_organisation(ifc, owner, person_and_organisation="person_and_organisation")

    def test_clearing_the_active_user_if_you_remove_it(self, ifc, owner):
        owner.get_user().should_be_called().will_return("user")
        owner.clear_user().should_be_called()
        ifc.run("owner.remove_person_and_organisation", person_and_organisation="user").should_be_called()
        subject.remove_person_and_organisation(ifc, owner, person_and_organisation="user")


class TestSetUser:
    def test_run(self, owner):
        owner.set_user("person_and_organisation").should_be_called()
        subject.set_user(owner, user="person_and_organisation")


class TestGetUser:
    def test_run(self, owner):
        owner.get_user().should_be_called().will_return("person_and_organisation")
        assert subject.get_user(owner) == "person_and_organisation"


class TestClearUser:
    def test_run(self, owner):
        owner.clear_user().should_be_called()
        subject.clear_user(owner)


class TestAddActor:
    def test_run(self, ifc):
        ifc.run("owner.add_actor", ifc_class="IfcActor", actor="person").should_be_called().will_return("actor")
        assert subject.add_actor(ifc, ifc_class="IfcActor", actor="person") == "actor"


class TestRemoveActor:
    def test_run(self, ifc):
        ifc.run("owner.remove_actor", actor="actor").should_be_called()
        subject.remove_actor(ifc, actor="actor")


class TestEnableEditingActor:
    def test_run(self, owner):
        owner.set_actor("actor").should_be_called()
        owner.import_actor_attributes("actor").should_be_called()
        subject.enable_editing_actor(owner, actor="actor")


class TestDisableEditingActor:
    def test_run(self, owner):
        owner.clear_actor().should_be_called()
        subject.disable_editing_actor(owner)


class TestEditActor:
    def test_run(self, ifc, owner):
        owner.get_actor().should_be_called().will_return("actor")
        owner.export_actor_attributes().should_be_called().will_return("attributes")
        ifc.run("owner.edit_actor", actor="actor", attributes="attributes").should_be_called()
        owner.clear_actor().should_be_called()
        subject.edit_actor(ifc, owner)


class TestAssignActor:
    def test_run(self, ifc, owner):
        ifc.run("owner.assign_actor", relating_actor="actor", related_object="element").should_be_called()
        subject.assign_actor(ifc, actor="actor", element="element")


class TestUnassignActor:
    def test_run(self, ifc, owner):
        ifc.run("owner.unassign_actor", relating_actor="actor", related_object="element").should_be_called()
        subject.unassign_actor(ifc, actor="actor", element="element")
