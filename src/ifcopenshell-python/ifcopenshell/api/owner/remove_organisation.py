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
    def __init__(self, file, organisation=None):
        """Remove an organisation

        All roles and addresses assigned to the organisation will also be
        removed.

        :param organisation: The IfcOrganization to remove
        :type organisation: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            organisation = ifcopenshell.api.run("owner.add_organisation", model,
                identification="AWB", name="Architects Without Ballpens")
            ifcopenshell.api.run("owner.remove_organisation", model, organisation=organisation)
        """
        self.file = file
        self.settings = {"organisation": organisation}

    def execute(self):
        for role in self.settings["organisation"].Roles or []:
            if len(self.file.get_inverse(role)) == 1:
                ifcopenshell.api.run("owner.remove_role", self.file, role=role)
        for address in self.settings["organisation"].Addresses or []:
            if len(self.file.get_inverse(address)) == 1:
                ifcopenshell.api.run("owner.remove_address", self.file, address=address)
        for inverse in self.file.get_inverse(self.settings["organisation"]):
            if inverse.is_a("IfcOrganizationRelationship"):
                if inverse.RelatingOrganization == self.settings["organisation"]:
                    self.file.remove(inverse)
                elif inverse.RelatedOrganizations == (self.settings["organisation"],):
                    self.file.remove(inverse)
            elif inverse.is_a("IfcDocumentInformation"):
                if inverse.Editors == (self.settings["organisation"],):
                    inverse.Editors = None
            elif inverse.is_a("IfcPersonAndOrganization"):
                ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=inverse)
            elif inverse.is_a("IfcActor"):
                ifcopenshell.api.run("root.remove_product", self.file, product=inverse)
            elif inverse.is_a("IfcResourceLevelRelationship") and not inverse.is_a("IfcOrganizationRelationship"):
                if inverse.RelatedResourceObjects == (self.settings["organisation"],):
                    self.file.remove(inverse)
            elif inverse.is_a("IfcApplication"):
                ifcopenshell.api.run("owner.remove_application", self.file, application=inverse)

        self.file.remove(self.settings["organisation"])
