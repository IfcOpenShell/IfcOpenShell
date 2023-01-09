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
    def __init__(self, file, assigned_object=None, role="ARCHITECT"):
        """Adds and assigns a new role

        People and organisations must play one or more roles on a project. Roles
        include architects, engineers, subcontractors, clients, manufacturers,
        etc. Typically these roles and their corresponding responsibilities will
        be outlined in contractual documents.

        This function will both add and assign the role to the person or
        organisation.

        :param assigned_object: The IfcPerson or IfcOrganization the role should
            be assigned to.
        :type assigned_object: ifcopenshell.entity_instance.entity_instance
        :param role: The type of role, taken from the IFC documentation for
            IfcActorRole, or a custom name.
        :type role: str, optional
        :return: The newly created IfcActorRole
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            organisation = ifcopenshell.api.run("owner.add_organisation", model,
                identification="AWB", name="Architects Without Ballpens")
            ifcopenshell.api.run("owner.add_role", model, assigned_object=organisation, role="ARCHITECT")
        """
        self.file = file
        self.settings = {"assigned_object": assigned_object, "role": role}

    def execute(self):
        element = self.file.createIfcActorRole("ARCHITECT")
        if self.settings["role"]:
            try:
                element.Role = self.settings["role"]
            except:
                element.Role = "USERDEFINED"
                element.UserDefinedRole = self.settings["role"]
        roles = list(self.settings["assigned_object"].Roles) if self.settings["assigned_object"].Roles else []
        roles.append(element)
        self.settings["assigned_object"].Roles = roles
        return element
