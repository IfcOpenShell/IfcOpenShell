# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.


import blenderbim.core.owner as subject
from test.core.bootstrap import ifc, blender, person_editor, role_editor, address_editor, organisation_editor, owner


class TestAddPerson:
    def test_run(self, ifc):
        ifc.run("owner.add_person").should_be_called().will_return("person")
        assert subject.add_person(ifc) == "person"


class TestRemovePerson:
    def test_run(self, ifc):
        ifc.run("owner.remove_person", person="person").should_be_called()
        subject.remove_person(ifc, person="person")


class TestEnableEditingPerson:
    def test_run(self, person_editor):
        person_editor.set_person("person").should_be_called()
        person_editor.import_attributes().should_be_called()
        subject.enable_editing_person(person_editor, person="person")


class TestDisableEditingPerson:
    def test_run(self, person_editor):
        person_editor.clear_person().should_be_called()
        subject.disable_editing_person(person_editor)


class TestEditPerson:
    def test_run(self, ifc, person_editor):
        person_editor.get_person().should_be_called().will_return("person")
        person_editor.export_attributes().should_be_called().will_return("attributes")
        ifc.run("owner.edit_person", person="person", attributes="attributes").should_be_called()
        person_editor.clear_person().should_be_called()
        subject.edit_person(ifc, person_editor)


class TestAddPersonAttribute:
    def test_run(self, person_editor):
        person_editor.add_attribute("name").should_be_called()
        subject.add_person_attribute(person_editor, name="name")


class TestRemovePersonAttribute:
    def test_run(self, person_editor):
        person_editor.remove_attribute("name", "id").should_be_called()
        subject.remove_person_attribute(person_editor, name="name", id="id")


class TestAddRole:
    def test_run(self, ifc):
        ifc.run("owner.add_role", assigned_object="parent").should_be_called().will_return("role")
        assert subject.add_role(ifc, parent="parent") == "role"


class TestRemoveRole:
    def test_run(self, ifc):
        ifc.run("owner.remove_role", role="role").should_be_called()
        subject.remove_role(ifc, role="role")


class TestEnableEditingRole:
    def test_run(self, role_editor):
        role_editor.set_role("role").should_be_called()
        role_editor.import_attributes().should_be_called()
        subject.enable_editing_role(role_editor, role="role")


class TestDisableEditingRole:
    def test_run(self, role_editor):
        role_editor.clear_role().should_be_called()
        subject.disable_editing_role(role_editor)


class TestEditRole:
    def test_run(self, ifc, role_editor):
        role_editor.export_attributes().should_be_called().will_return("attributes")
        role_editor.get_role().should_be_called().will_return("role")
        ifc.run("owner.edit_role", role="role", attributes="attributes").should_be_called()
        role_editor.clear_role().should_be_called()
        subject.edit_role(ifc, role_editor)


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
    def test_run(self, address_editor):
        address_editor.set_address("address").should_be_called()
        address_editor.import_attributes().should_be_called()
        subject.enable_editing_address(address_editor, address="address")


class TestDisableEditingAddress:
    def test_run(self, address_editor):
        address_editor.clear_address().should_be_called()
        subject.disable_editing_address(address_editor)


class TestEditAddress:
    def test_run(self, ifc, address_editor):
        address_editor.get_address().should_be_called().will_return("address")
        address_editor.export_attributes().should_be_called().will_return("attributes")
        ifc.run("owner.edit_address", address="address", attributes="attributes").should_be_called()
        address_editor.clear_address().should_be_called()
        subject.edit_address(ifc, address_editor)


class TestAddAddressAttribute:
    def test_run(self, address_editor):
        address_editor.add_attribute("name").should_be_called()
        subject.add_address_attribute(address_editor, name="name")


class TestRemoveAddressAttribute:
    def test_run(self, address_editor):
        address_editor.remove_attribute("name", "id").should_be_called()
        subject.remove_address_attribute(address_editor, name="name", id="id")


class TestAddOrganisation:
    def test_run(self, ifc):
        ifc.run("owner.add_organisation").should_be_called().will_return("organisation")
        assert subject.add_organisation(ifc) == "organisation"


class TestRemoveOrganisation:
    def test_run(self, ifc):
        ifc.run("owner.remove_organisation", organisation="organisation").should_be_called()
        subject.remove_organisation(ifc, organisation="organisation")


class TestEnableEditingOrganisation:
    def test_run(self, organisation_editor):
        organisation_editor.set_organisation("organisation").should_be_called()
        organisation_editor.import_attributes().should_be_called()
        subject.enable_editing_organisation(organisation_editor, organisation="organisation")


class TestDisableEditingOrganisation:
    def test_run(self, organisation_editor):
        organisation_editor.clear_organisation().should_be_called()
        subject.disable_editing_organisation(organisation_editor)


class TestEditOrganisation:
    def test_run(self, ifc, organisation_editor):
        organisation_editor.get_organisation().should_be_called().will_return("organisation")
        organisation_editor.export_attributes().should_be_called().will_return("attributes")
        ifc.run("owner.edit_organisation", organisation="organisation", attributes="attributes").should_be_called()
        organisation_editor.clear_organisation().should_be_called()
        subject.edit_organisation(ifc, organisation_editor)


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
