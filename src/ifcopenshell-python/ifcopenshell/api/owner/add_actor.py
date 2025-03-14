# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api.root
from typing import Literal


ACTOR_TYPE = Literal["IfcActor", "IfcOccupant"]


def add_actor(
    file: ifcopenshell.file,
    actor: ifcopenshell.entity_instance,
    ifc_class: ACTOR_TYPE = "IfcActor",
) -> ifcopenshell.entity_instance:
    """Adds a new actor

    An actor is a person or an organisation who has a responsibility or role
    to play in a project. Actor roles include design consultants,
    architects, engineers, cost planners, suppliers, manufacturers,
    warrantors, owners, subcontractors, etc.

    Actors may either be project actors, who are responsible for the
    delivery of the project, or occupants, who are responsible for the
    consumption of the project.

    Identifying and managing actors is critical for asset management, and
    identifying liability for legal submissions.

    :param actor: Most commonly, an IfcOrganization (in compliance with GDPR
        requirements for non personally identifiable information), or an
        IfcPerson if it is a sole individual, or an IfcPersonAndOrganization
        if a specific person is liable within an organisation and must be
        legally nominated.
    :param ifc_class: Either "IfcActor" or "IfcOccupant".
    :return: The newly created IfcActor or IfcOccupant

    Example:

    .. code:: python

        # Setup an organisation with a single role
        organisation = ifcopenshell.api.owner.add_organisation(model,
            identification="AWB", name="Architects Without Ballpens")
        role = ifcopenshell.api.owner.add_role(model, assigned_object=organisation, role="ARCHITECT")

        # Assign that organisation to a newly created actor
        actor = ifcopenshell.api.owner.add_actor(model, actor=organisation)
    """
    ifc_class = ifc_class or "IfcActor"
    actor_ = ifcopenshell.api.root.create_entity(file, ifc_class=ifc_class)
    actor_.TheActor = actor
    return actor_
