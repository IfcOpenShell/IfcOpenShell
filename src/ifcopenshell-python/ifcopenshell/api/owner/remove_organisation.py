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


def remove_organisation(file: ifcopenshell.file, organisation: ifcopenshell.entity_instance) -> None:
    """Remove an organisation

    All roles and addresses assigned to the organisation will also be
    removed.

    :param organisation: The IfcOrganization to remove
    :return: None

    Example:

    .. code:: python

        organisation = ifcopenshell.api.owner.add_organisation(model,
            identification="AWB", name="Architects Without Ballpens")
        ifcopenshell.api.owner.remove_organisation(model, organisation=organisation)
    """
    for role in organisation.Roles or []:
        if (file.get_total_inverses(role)) == 1:
            ifcopenshell.api.owner.remove_role(file, role=role)
    for address in organisation.Addresses or []:
        if (file.get_total_inverses(address)) == 1:
            ifcopenshell.api.owner.remove_address(file, address=address)
    for inverse in file.get_inverse(organisation):
        if inverse.is_a("IfcOrganizationRelationship"):
            if inverse.RelatingOrganization == organisation:
                file.remove(inverse)
            elif inverse.RelatedOrganizations == (organisation,):
                file.remove(inverse)
        elif inverse.is_a("IfcDocumentInformation"):
            if inverse.Editors == (organisation,):
                inverse.Editors = None
        elif inverse.is_a("IfcPersonAndOrganization"):
            ifcopenshell.api.owner.remove_person_and_organisation(file, person_and_organisation=inverse)
        elif inverse.is_a("IfcActor"):
            ifcopenshell.api.root.remove_product(file, product=inverse)
        elif inverse.is_a("IfcResourceLevelRelationship") and not inverse.is_a("IfcOrganizationRelationship"):
            if inverse.RelatedResourceObjects == (organisation,):
                file.remove(inverse)
        elif inverse.is_a("IfcApplication"):
            ifcopenshell.api.owner.remove_application(file, application=inverse)

    file.remove(organisation)
