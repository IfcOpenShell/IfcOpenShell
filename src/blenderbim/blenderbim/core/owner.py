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


def add_person(ifc):
    return ifc.run("owner.add_person")


def remove_person(ifc, person=None):
    ifc.run("owner.remove_person", person=person)


def enable_editing_person(person_editor, person=None):
    person_editor.set_person(person)
    person_editor.import_attributes()


def disable_editing_person(person_editor):
    person_editor.clear_person()


def edit_person(ifc, person_editor):
    ifc.run("owner.edit_person", person=person_editor.get_person(), attributes=person_editor.export_attributes())
    disable_editing_person(person_editor)


def add_person_attribute(person_editor, name=None):
    person_editor.add_attribute(name)


def remove_person_attribute(person_editor, name=None, id=None):
    person_editor.remove_attribute(name, id)


def add_role(ifc, parent=None):
    return ifc.run("owner.add_role", assigned_object=parent)


def remove_role(ifc, role=None):
    ifc.run("owner.remove_role", role=role)


def enable_editing_role(role_editor, role=None):
    role_editor.set_role(role)
    role_editor.import_attributes()


def disable_editing_role(role_editor):
    role_editor.clear_role()


def edit_role(ifc, role_editor):
    ifc.run("owner.edit_role", role=role_editor.get_role(), attributes=role_editor.export_attributes())
    role_editor.clear_role()


def add_address(ifc, parent=None, ifc_class="IfcPostalAddress"):
    return ifc.run("owner.add_address", assigned_object=parent, ifc_class=ifc_class)


def remove_address(ifc, address=None):
    ifc.run("owner.remove_address", address=address)


def enable_editing_address(address_editor, address=None):
    address_editor.set_address(address)
    address_editor.import_attributes()


def disable_editing_address(address_editor):
    address_editor.clear_address()


def edit_address(ifc, address_editor):
    address = address_editor.get_address()
    ifc.run("owner.edit_address", address=address, attributes=address_editor.export_attributes())
    address_editor.clear_address()


def add_address_attribute(address_editor, name=None):
    address_editor.add_attribute(name)


def remove_address_attribute(address_editor, name=None, id=None):
    address_editor.remove_attribute(name, id)


def add_organisation(ifc):
    return ifc.run("owner.add_organisation")


def remove_organisation(ifc, organisation=None):
    ifc.run("owner.remove_organisation", organisation=organisation)


def enable_editing_organisation(organisation_editor, organisation=None):
    organisation_editor.set_organisation(organisation)
    organisation_editor.import_attributes()


def disable_editing_organisation(organisation_editor):
    organisation_editor.clear_organisation()


def edit_organisation(ifc, organisation_editor):
    organisation = organisation_editor.get_organisation()
    ifc.run("owner.edit_organisation", organisation=organisation, attributes=organisation_editor.export_attributes())
    organisation_editor.clear_organisation()


def add_person_and_organisation(ifc, person=None, organisation=None):
    return ifc.run("owner.add_person_and_organisation", person=person, organisation=organisation)


def remove_person_and_organisation(ifc, owner, person_and_organisation):
    if owner.get_user() == person_and_organisation:
        owner.clear_user()
    ifc.run("owner.remove_person_and_organisation", person_and_organisation=person_and_organisation)


def set_user(owner, user=None):
    owner.set_user(user)


def get_user(owner):
    return owner.get_user()
