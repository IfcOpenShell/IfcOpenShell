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
    def __init__(self, file, identification="APTR", name="Aperture Science"):
        """Adds a new organisation

        Organisations are the main way to identify manufacturers, suppliers, and
        other actors who do not have a single representative or must not have
        any personally identifiable information.

        :param identification: The short code identifying the organisation.
            Sometimes used in drawing naming schemes. Otherise used as a
            canonicalised way of computers to identify the organisation. Like
            their stock name.
        :type identification: str, optional
        :param name: The legal name of the organisation
        :type name: str, optional
        :return: The newly created IfcOrganization
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            organisation = ifcopenshell.api.run("owner.add_organisation", model,
                identification="AWB", name="Architects Without Ballpens")
        """
        self.file = file
        self.settings = {"identification": identification, "name": name}

    def execute(self):
        data = {"Name": self.settings["name"]}
        if self.file.schema == "IFC2X3":
            data["Id"] = self.settings["identification"]
        else:
            data["Identification"] = self.settings["identification"]
        return self.file.create_entity("IfcOrganization", **data)
