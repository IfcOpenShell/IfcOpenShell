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
import ifcopenshell.api


class Usecase:
    def __init__(self, file, actor=None, ifc_class="IfcActor"):
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
        :type actor: ifcopenshell.entity_instance.entity_instance
        :param ifc_class: Either "IfcActor" or "IfcOccupant".
        :type ifc_class: str, optional
        :return: The newly created IfcActor or IfcOccupant
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Setup an organisation with a single role
            organisation = ifcopenshell.api.run("owner.add_organisation", model,
                identification="AWB", name="Architects Without Ballpens")
            role = ifcopenshell.api.run("owner.add_role", model, assigned_object=organisation, role="ARCHITECT")

            # Assign that organisation to a newly created actor
            actor = ifcopenshell.api.run("owner.add_actor", model, actor=organisation)
        """
        self.file = file
        self.settings = {"actor": actor, "ifc_class": ifc_class or "IfcActor"}

    def execute(self):
        actor = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=self.settings["ifc_class"])
        actor.TheActor = self.settings["actor"]
        return actor
