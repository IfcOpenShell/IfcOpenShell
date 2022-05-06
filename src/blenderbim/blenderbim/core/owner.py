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


def enable_editing_person(owner, person=None):
    owner.set_person(person)
    owner.import_person_attributes()


def disable_editing_person(owner):
    owner.clear_person()


def edit_person(ifc, owner):
    ifc.run("owner.edit_person", person=owner.get_person(), attributes=owner.export_person_attributes())
    disable_editing_person(owner)


def add_person_attribute(owner, name=None):
    owner.add_person_attribute(name)


def remove_person_attribute(owner, name=None, id=None):
    owner.remove_person_attribute(name, id)


def add_role(ifc, parent=None):
    return ifc.run("owner.add_role", assigned_object=parent)


def remove_role(ifc, role=None):
    ifc.run("owner.remove_role", role=role)


def enable_editing_role(owner, role=None):
    owner.set_role(role)
    owner.import_role_attributes()


def disable_editing_role(owner):
    owner.clear_role()


def edit_role(ifc, owner):
    ifc.run("owner.edit_role", role=owner.get_role(), attributes=owner.export_role_attributes())
    owner.clear_role()


def add_address(ifc, parent=None, ifc_class="IfcPostalAddress"):
    return ifc.run("owner.add_address", assigned_object=parent, ifc_class=ifc_class)


def remove_address(ifc, address=None):
    ifc.run("owner.remove_address", address=address)


def enable_editing_address(owner, address=None):
    owner.set_address(address)
    owner.import_address_attributes()


def disable_editing_address(owner):
    owner.clear_address()


def edit_address(ifc, owner):
    address = owner.get_address()
    ifc.run("owner.edit_address", address=address, attributes=owner.export_address_attributes())
    owner.clear_address()


def add_address_attribute(owner, name=None):
    owner.add_address_attribute(name)


def remove_address_attribute(owner, name=None, id=None):
    owner.remove_address_attribute(name, id)


def add_organisation(ifc):
    return ifc.run("owner.add_organisation")


def remove_organisation(ifc, organisation=None):
    ifc.run("owner.remove_organisation", organisation=organisation)


def enable_editing_organisation(owner, organisation=None):
    owner.set_organisation(organisation)
    owner.import_organisation_attributes()


def disable_editing_organisation(owner):
    owner.clear_organisation()


def edit_organisation(ifc, owner):
    organisation = owner.get_organisation()
    ifc.run("owner.edit_organisation", organisation=organisation, attributes=owner.export_organisation_attributes())
    owner.clear_organisation()


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


def clear_user(owner):
    owner.clear_user()


def add_actor(ifc, ifc_class=None, actor=None):
    return ifc.run("owner.add_actor", ifc_class=ifc_class, actor=actor)


def remove_actor(ifc, actor=None):
    ifc.run("owner.remove_actor", actor=actor)


def enable_editing_actor(owner, actor=None):
    owner.set_actor(actor)
    owner.import_actor_attributes(actor)


def disable_editing_actor(owner):
    owner.clear_actor()


def edit_actor(ifc, owner):
    ifc.run("owner.edit_actor", actor=owner.get_actor(), attributes=owner.export_actor_attributes())
    disable_editing_actor(owner)


def assign_actor(ifc, actor=None, element=None):
    ifc.run("owner.assign_actor", relating_actor=actor, related_object=element)


def unassign_actor(ifc, actor=None, element=None):
    ifc.run("owner.unassign_actor", relating_actor=actor, related_object=element)
