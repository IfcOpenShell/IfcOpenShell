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
    def __init__(self, file, identification="HSeldon", family_name="Seldon", given_name="Hari"):
        """Adds a new person

        Persons are used to identify a legal or liable representative of an
        organisation or point of contact.

        :param identification: The computer readable unique identification of
            the person. For example, their username in a CDE or alias.
        :type identification: str, optional
        :param family_name: The family name
        :type family_name: str, optional
        :param given_name: The given name
        :type given_name: str, optional
        :return: The newly created IfcPerson
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            ifcopenshell.api.run("owner.add_person", model,
                identification="bobthebuilder", family_name="Thebuilder", given_name="Bob")
        """
        self.file = file
        self.settings = {
            "identification": identification,
            "family_name": family_name,
            "given_name": given_name,
        }

    def execute(self):
        data = {"FamilyName": self.settings["family_name"], "GivenName": self.settings["given_name"]}
        if self.file.schema == "IFC2X3":
            data["Id"] = self.settings["identification"]
        else:
            data["Identification"] = self.settings["identification"]
        return self.file.create_entity("IfcPerson", **data)
