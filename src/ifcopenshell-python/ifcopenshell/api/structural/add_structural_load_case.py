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
    def __init__(
        self, file, name="Unnamed", action_type="NOTDEFINED", action_source="NOTDEFINED"
    ):
        """Adds a new load case, which is a collection of related load groups

        :param name: The name of the load case
        :type name: str
        :param action_type: Choose from EXTRAORDINARY_A, PERMANENT_G,
            or VARIABLE_Q, taken from the Eurocode standard.
        :type action_type: str
        :param action_source: The source of the load case, such as DEAD_LOAD_G,
            LIVE_LOAD_Q, TRANSPORT, ICE, etc. For the full list consult
            IfcActionSourceTypeEnum in the IFC documentation.
        :type action_source: str
        :return: The new IfcStructuralLoadCase
        :rtype: ifcopenshell.entity_instance.entity_instance
        """
        self.file = file
        self.settings = {
            "name": name,
            "action_type": action_type,
            "action_source": action_source,
        }

    def execute(self):
        load_case = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcStructuralLoadCase",
            predefined_type="LOAD_CASE",
            name=self.settings["name"],
        )
        load_case.ActionType = self.settings["action_type"]
        load_case.ActionSource = self.settings["action_source"]
        return load_case
