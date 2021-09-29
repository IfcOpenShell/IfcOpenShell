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

import test.bim.bootstrap


class TestAddPerson(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        When I press "bim.add_person"
        Then nothing interesting happens
        """


class TestRemovePerson(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        When I press "bim.remove_person(person={person})"
        Then nothing interesting happens
        """


class TestAddPersonAttribute(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        When I press "bim.add_person_attribute(name='MiddleNames')"
        And I press "bim.add_person_attribute(name='PrefixTitles')"
        And I press "bim.add_person_attribute(name='SuffixTitles')"
        Then nothing interesting happens
        """


class TestRemovePersonAttribute(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        When I press "bim.add_person_attribute(name='MiddleNames')"
        And I press "bim.remove_person_attribute(name='MiddleNames', id=0)"
        And I press "bim.add_person_attribute(name='PrefixTitles')"
        And I press "bim.remove_person_attribute(name='PrefixTitles', id=0)"
        And I press "bim.add_person_attribute(name='SuffixTitles')"
        And I press "bim.remove_person_attribute(name='SuffixTitles', id=0)"
        Then nothing interesting happens
        """


class TestEnableEditingPerson(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        When I press "bim.enable_editing_person(person={person})"
        Then "scene.BIMOwnerProperties.active_person_id" is "{person}"
        """


class TestDisableEditingPerson(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        And I press "bim.enable_editing_person(person={person})"
        When I press "bim.disable_editing_person"
        Then "scene.BIMOwnerProperties.active_person_id" is "0"
        """


class TestEditPerson(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        And I press "bim.enable_editing_person(person={person})"
        When I press "bim.edit_person"
        Then "scene.BIMOwnerProperties.active_person_id" is "0"
        """


class TestAddRole(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        When I press "bim.add_role(parent={person})"
        Then nothing interesting happens
        """


class TestRemoveRole(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        And I press "bim.add_role(parent={person})"
        And the variable "role" is "{ifc}.by_type('IfcActorRole')[0].id()"
        When I press "bim.remove_role(role={role})"
        Then nothing interesting happens
        """


class TestEnableEditingRole(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        And I press "bim.add_role(parent={person})"
        And the variable "role" is "{ifc}.by_type('IfcActorRole')[0].id()"
        When I press "bim.enable_editing_role(role={role})"
        Then nothing interesting happens
        """


class TestDisableEditingRole(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        And I press "bim.add_role(parent={person})"
        And the variable "role" is "{ifc}.by_type('IfcActorRole')[0].id()"
        And I press "bim.enable_editing_role(role={role})"
        When I press "bim.disable_editing_role()"
        Then nothing interesting happens
        """


class TestEditRole(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        And I press "bim.add_role(parent={person})"
        And the variable "role" is "{ifc}.by_type('IfcActorRole')[0].id()"
        And I press "bim.enable_editing_role(role={role})"
        When I press "bim.edit_role()"
        Then nothing interesting happens
        """


class TestAddAddress(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        When I press "bim.add_address(parent={person}, ifc_class='IfcPostalAddress')"
        Then nothing interesting happens
        """


class TestAddAddressAttribute(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        And I press "bim.add_address(parent={person}, ifc_class='IfcPostalAddress')"
        And the variable "address" is "{ifc}.by_type('IfcPostalAddress')[0].id()"
        And I press "bim.enable_editing_address(address={address})"
        When I press "bim.add_address_attribute(name='AddressLines')"
        Then nothing interesting happens
        """


class TestRemoveAddressAttribute(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        And I press "bim.add_address(parent={person}, ifc_class='IfcPostalAddress')"
        And the variable "address" is "{ifc}.by_type('IfcPostalAddress')[0].id()"
        And I press "bim.enable_editing_address(address={address})"
        And I press "bim.add_address_attribute(name='AddressLines')"
        When I press "bim.remove_address_attribute(name='AddressLines', id=0)"
        Then nothing interesting happens
        """


class TestRemoveAddress(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        And I press "bim.add_address(parent={person}, ifc_class='IfcPostalAddress')"
        And the variable "address" is "{ifc}.by_type('IfcPostalAddress')[0].id()"
        When I press "bim.remove_address(address={address})"
        Then nothing interesting happens
        """


class TestEnableEditingAddress(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        And I press "bim.add_address(parent={person}, ifc_class='IfcPostalAddress')"
        And the variable "address" is "{ifc}.by_type('IfcPostalAddress')[0].id()"
        When I press "bim.enable_editing_address(address={address})"
        Then nothing interesting happens
        """


class TestDisableEditingAddress(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        And I press "bim.add_address(parent={person}, ifc_class='IfcPostalAddress')"
        And the variable "address" is "{ifc}.by_type('IfcPostalAddress')[0].id()"
        And I press "bim.enable_editing_address(address={address})"
        When I press "bim.disable_editing_address()"
        Then nothing interesting happens
        """


class TestEditAddress(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_run(self):
        return """
        Given an empty IFC project
        And I press "bim.add_person"
        And the variable "person" is "{ifc}.by_type('IfcPerson')[0].id()"
        And I press "bim.add_address(parent={person}, ifc_class='IfcPostalAddress')"
        And the variable "address" is "{ifc}.by_type('IfcPostalAddress')[0].id()"
        And I press "bim.enable_editing_address(address={address})"
        When I press "bim.edit_address()"
        Then nothing interesting happens
        """
