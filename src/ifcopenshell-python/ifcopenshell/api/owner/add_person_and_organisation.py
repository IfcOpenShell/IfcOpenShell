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
import ifcopenshell


def add_person_and_organisation(
    file: ifcopenshell.file,
    person: ifcopenshell.entity_instance,
    organisation: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:
    """Adds a paired person and organisation

    A person and an organisation may be paired to create a representative
    belonging to a company.

    :param person: The IfcPerson being the representative of the
        organisation.
    :param organisation: The IfcOrganization it
    :return: The newly created IfcPersonAndOrganization

    Example:

    .. code:: python

        person = ifcopenshell.api.owner.add_person(model,
            identification="lecorbycorbycorb", family_name="Curbosiar", given_name="Le")
        organisation = ifcopenshell.api.owner.add_organisation(model,
            identification="AWB", name="Architects Without Ballpens")

        ifcopenshell.api.owner.add_person_and_organisation(model,
            person=person, organisation=organisation)
    """
    return file.create_entity("IfcPersonAndOrganization", person, organisation)
