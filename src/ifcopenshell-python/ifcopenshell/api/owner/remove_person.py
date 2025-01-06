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

import ifcopenshell.api.root
import ifcopenshell.api.owner


def remove_person(file: ifcopenshell.file, person: ifcopenshell.entity_instance) -> None:
    """Remove an person

    All roles and addresses assigned to the person will also be
    removed.
    In IFC2X3 will also remove related inventories if `person` was
    the only responsile person for them.

    :param person: The IfcPerson to remove
    :type person: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        ifcopenshell.api.owner.add_person(model,
            identification="bobthebuilder", family_name="Thebuilder", given_name="Bob")
        ifcopenshell.api.owner.remove_person(model, person=person)
    """
    settings = {"person": person}

    for role in settings["person"].Roles or []:
        if len(file.get_inverse(role)) == 1:
            ifcopenshell.api.owner.remove_role(file, role=role)
    for address in settings["person"].Addresses or []:
        if len(file.get_inverse(address)) == 1:
            ifcopenshell.api.owner.remove_address(file, address=address)
    for inverse in file.get_inverse(settings["person"]):
        if inverse.is_a("IfcWorkControl"):
            if inverse.Creators == (settings["person"],):
                inverse.Creators = None
        elif inverse.is_a("IfcInventory"):
            if inverse.ResponsiblePersons == (settings["person"],):
                # in IFC2X3 ResponsiblePersons is not optional and without it IfcInventory is not valid
                if file.schema == "IFC2X3":
                    ifcopenshell.api.root.remove_product(file, product=inverse)
        elif inverse.is_a("IfcDocumentInformation"):
            if inverse.Editors == (settings["person"],):
                inverse.Editors = None
        elif inverse.is_a("IfcPersonAndOrganization"):
            ifcopenshell.api.owner.remove_person_and_organisation(file, person_and_organisation=inverse)
        elif inverse.is_a("IfcActor"):
            ifcopenshell.api.root.remove_product(file, product=inverse)
        elif inverse.is_a("IfcResourceLevelRelationship"):
            if inverse.RelatedResourceObjects == (settings["person"],):
                file.remove(inverse)
    file.remove(settings["person"])
