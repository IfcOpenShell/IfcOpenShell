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

import ifcopenshell.api


class Usecase:
    def __init__(self, file, person_and_organisation=None):
        """Removes a person and organisation

        Note that the underlying person and organisation is not removed, only
        the "person and organisation" group.

        :param person_and_organisation: The IfcPersonAndOrganization to remove.
        :type person_and_organisation: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            person = ifcopenshell.api.run("owner.add_person", model,
                identification="lecorbycorbycorb", family_name="Curbosiar", given_name="Le")
            organisation = ifcopenshell.api.run("owner.add_organisation", model,
                identification="AWB", name="Architects Without Ballpens")

            user = ifcopenshell.api.run("owner.add_person_and_organisation", model,
                person=person, organisation=organisation)

            ifcopenshell.api.run("owner.remove_person_and_organisation", model, person_and_organisation=user)
        """
        self.file = file
        self.settings = {"person_and_organisation": person_and_organisation}

    def execute(self):
        for inverse in self.file.get_inverse(self.settings["person_and_organisation"]):
            if inverse.is_a("IfcDocumentInformation"):
                if inverse.Editors == (self.settings["person_and_organisation"],):
                    inverse.Editors = None
            elif inverse.is_a("IfcActor"):
                ifcopenshell.api.run("root.remove_product", self.file, product=inverse)
            elif inverse.is_a("IfcResourceLevelRelationship"):
                if inverse.RelatedResourceObjects == (self.settings["person_and_organisation"],):
                    self.file.remove(inverse)
            elif inverse.is_a("IfcOwnerHistory"):
                self.file.remove(inverse)
        self.file.remove(self.settings["person_and_organisation"])
