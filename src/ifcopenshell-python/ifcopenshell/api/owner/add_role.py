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


def add_role(
    file: ifcopenshell.file, assigned_object: ifcopenshell.entity_instance, role: str = "ARCHITECT"
) -> ifcopenshell.entity_instance:
    """Adds and assigns a new role

    People and organisations must play one or more roles on a project. Roles
    include architects, engineers, subcontractors, clients, manufacturers,
    etc. Typically these roles and their corresponding responsibilities will
    be outlined in contractual documents.

    This function will both add and assign the role to the person or
    organisation.

    :param assigned_object: The IfcPerson or IfcOrganization the role should
        be assigned to.
    :param role: The type of role, taken from the IFC documentation for
        IfcActorRole, or a custom name. Defaults to "ARCHITECT".
    :return: The newly created IfcActorRole

    Example:

    .. code:: python

        organisation = ifcopenshell.api.owner.add_organisation(model,
            identification="AWB", name="Architects Without Ballpens")
        ifcopenshell.api.owner.add_role(model, assigned_object=organisation, role="ARCHITECT")
    """
    element = file.create_entity("IfcActorRole", Role="ARCHITECT")
    if role:
        try:
            element.Role = role
        except:
            element.Role = "USERDEFINED"
            element.UserDefinedRole = role
    roles = list(assigned_object.Roles) if assigned_object.Roles else []
    roles.append(element)
    assigned_object.Roles = roles
    return element
