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

import ifcopenshell.api


class Usecase:
    def __init__(self, file, actor=None):
        """Removes an actor

        :param actor: The IfcActor to remove.
        :type actor: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Setup an organisation with a single role
            organisation = ifcopenshell.api.run("owner.add_organisation", model,
                identification="AWB", name="Architects Without Ballpens")
            role = ifcopenshell.api.run("owner.add_role", model, assigned_object=organisation)
            ifcopenshell.api.run("owner.edit_role", model, role=role, attributes={"Role": "ARCHITECT"})

            # Assign that organisation to a newly created actor
            actor = ifcopenshell.api.run("owner.add_actor", model, actor=organisation)

            # Actually we need ballpens on this project
            ifcopenshell.api.run("owner.remove_actor", model, actor=actor)
        """
        self.file = file
        self.settings = {"actor": actor}

    def execute(self):
        self.file.remove(self.settings["actor"])
