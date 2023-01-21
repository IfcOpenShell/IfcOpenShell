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


class Usecase:
    def __init__(self, file, person=None, organisation=None):
        """Adds a paired person and organisation

        A person and an organisation may be paired to create a representative
        belonging to a company.

        :param person: The IfcPerson being the representative of the
            organisation.
        :type person: ifcopenshell.entity_instance.entity_instance
        :param organisation: The IfcOrganization itself.
        :type organisation: ifcopenshell.entity_instance.entity_instance
        :return: The newly created IfcPersonAndOrganization
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            person = ifcopenshell.api.run("owner.add_person", model,
                identification="lecorbycorbycorb", family_name="Curbosiar", given_name="Le")
            organisation = ifcopenshell.api.run("owner.add_organisation", model,
                identification="AWB", name="Architects Without Ballpens")

            ifcopenshell.api.run("owner.add_person_and_organisation", model,
                person=person, organisation=organisation)
        """
        self.file = file
        self.settings = {"person": person, "organisation": organisation}

    def execute(self):
        return self.file.createIfcPersonAndOrganization(self.settings["person"], self.settings["organisation"])
