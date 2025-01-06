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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool
    from ifcopenshell.api.owner.add_address import ADDRESS_TYPE
    from ifcopenshell.api.owner.add_actor import ACTOR_TYPE


def add_person(ifc: tool.Ifc) -> ifcopenshell.entity_instance:
    return ifc.run("owner.add_person")


def remove_person(ifc: tool.Ifc, person: ifcopenshell.entity_instance) -> None:
    ifc.run("owner.remove_person", person=person)


def enable_editing_person(owner: tool.Owner, person: ifcopenshell.entity_instance) -> None:
    owner.set_person(person)
    owner.import_person_attributes()


def disable_editing_person(owner: tool.Owner) -> None:
    owner.clear_person()


def edit_person(ifc: tool.Ifc, owner: tool.Owner) -> None:
    ifc.run("owner.edit_person", person=owner.get_person(), attributes=owner.export_person_attributes())
    disable_editing_person(owner)


def add_person_attribute(owner: tool.Owner, name: str) -> None:
    owner.add_person_attribute(name)


def remove_person_attribute(owner: tool.Owner, name: str, id: int) -> None:
    owner.remove_person_attribute(name, id)


def add_role(ifc: tool.Ifc, parent: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    return ifc.run("owner.add_role", assigned_object=parent)


def remove_role(ifc: tool.Ifc, role: ifcopenshell.entity_instance) -> None:
    ifc.run("owner.remove_role", role=role)


def enable_editing_role(owner: tool.Owner, role: ifcopenshell.entity_instance) -> None:
    owner.set_role(role)
    owner.import_role_attributes()


def disable_editing_role(owner: tool.Owner) -> None:
    owner.clear_role()


def edit_role(ifc: tool.Ifc, owner: tool.Owner) -> None:
    ifc.run("owner.edit_role", role=owner.get_role(), attributes=owner.export_role_attributes())
    owner.clear_role()


def add_address(
    ifc: tool.Ifc, parent: ifcopenshell.entity_instance, ifc_class: ADDRESS_TYPE = "IfcPostalAddress"
) -> ifcopenshell.entity_instance:
    return ifc.run("owner.add_address", assigned_object=parent, ifc_class=ifc_class)


def remove_address(ifc: tool.Ifc, address: ifcopenshell.entity_instance) -> None:
    ifc.run("owner.remove_address", address=address)


def enable_editing_address(owner: tool.Owner, address: ifcopenshell.entity_instance) -> None:
    owner.set_address(address)
    owner.import_address_attributes()


def disable_editing_address(owner: tool.Owner) -> None:
    owner.clear_address()


def edit_address(ifc: tool.Ifc, owner: tool.Owner) -> None:
    address = owner.get_address()
    ifc.run("owner.edit_address", address=address, attributes=owner.export_address_attributes())
    owner.clear_address()


def add_address_attribute(owner: tool.Owner, name: str) -> None:
    owner.add_address_attribute(name)


def remove_address_attribute(owner: tool.Owner, name: str, id: int) -> None:
    owner.remove_address_attribute(name, id)


def add_organisation(ifc: tool.Ifc) -> ifcopenshell.entity_instance:
    return ifc.run("owner.add_organisation")


def remove_organisation(ifc: tool.Ifc, organisation: ifcopenshell.entity_instance) -> None:
    ifc.run("owner.remove_organisation", organisation=organisation)


def enable_editing_organisation(owner: tool.Owner, organisation: ifcopenshell.entity_instance) -> None:
    owner.set_organisation(organisation)
    owner.import_organisation_attributes()


def disable_editing_organisation(owner: tool.Owner) -> None:
    owner.clear_organisation()


def edit_organisation(ifc: tool.Ifc, owner: tool.Owner) -> None:
    organisation = owner.get_organisation()
    ifc.run("owner.edit_organisation", organisation=organisation, attributes=owner.export_organisation_attributes())
    owner.clear_organisation()


def add_person_and_organisation(
    ifc: tool.Ifc, person: ifcopenshell.entity_instance, organisation: ifcopenshell.entity_instance
) -> ifcopenshell.entity_instance:
    return ifc.run("owner.add_person_and_organisation", person=person, organisation=organisation)


def remove_person_and_organisation(
    ifc: tool.Ifc, owner: tool.Owner, person_and_organisation: ifcopenshell.entity_instance
) -> None:
    if owner.get_user() == person_and_organisation:
        owner.clear_user()
    ifc.run("owner.remove_person_and_organisation", person_and_organisation=person_and_organisation)


def set_user(owner: tool.Owner, user: ifcopenshell.entity_instance) -> None:
    owner.set_user(user)


def get_user(owner: tool.Owner) -> Union[ifcopenshell.entity_instance, None]:
    return owner.get_user()


def clear_user(owner: tool.Owner) -> None:
    owner.clear_user()


def add_actor(
    ifc: tool.Ifc, ifc_class: ACTOR_TYPE, actor: ifcopenshell.entity_instance
) -> ifcopenshell.entity_instance:
    return ifc.run("owner.add_actor", ifc_class=ifc_class, actor=actor)


def remove_actor(ifc: tool.Ifc, actor: ifcopenshell.entity_instance) -> None:
    ifc.run("owner.remove_actor", actor=actor)


def enable_editing_actor(owner: tool.Owner, actor: ifcopenshell.entity_instance) -> None:
    owner.set_actor(actor)
    owner.import_actor_attributes(actor)


def disable_editing_actor(owner: tool.Owner) -> None:
    owner.clear_actor()


def edit_actor(ifc: tool.Ifc, owner: tool.Owner) -> None:
    ifc.run("owner.edit_actor", actor=owner.get_actor(), attributes=owner.export_actor_attributes())
    disable_editing_actor(owner)


def assign_actor(ifc: tool.Ifc, actor: ifcopenshell.entity_instance, element: ifcopenshell.entity_instance) -> None:
    ifc.run("owner.assign_actor", relating_actor=actor, related_object=element)


def unassign_actor(ifc: tool.Ifc, actor: ifcopenshell.entity_instance, element: ifcopenshell.entity_instance) -> None:
    ifc.run("owner.unassign_actor", relating_actor=actor, related_object=element)
