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
import ifcopenshell.api
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, relating_flow_element=None, related_flow_control=None):
        """Unassigns flow control element from the flow element.

        :param related_flow_control: IfcDistributionControlElement controling the
            flow element
        :type related_flow_control: ifcopenshell.entity_instance.entity_instance
        :param relating_flow_element: The IfcDistributionFlowElement that is being controlled
        :type relating_flow_element: ifcopenshell.entity_instance.entity_instance
        :return: If the control still is related to other objects, the
            IfcRelFlowControlElements is returned, otherwise None.
        :rtype: ifcopenshell.entity_instance.entity_instance, None

        Example:

        .. code:: python

            # assign control to the flow element
            flow_element = self.file.createIfcFlowSegment()
            flow_control = self.file.createIfcController()
            relation = ifcopenshell.api.run(
                "system.assign_flow_control", self.file,
                relating_control=flow_control, related_object=flow_element
            )

            # und unassign it
            ifcopenshell.api.run("system.unassign_flow_control", self.file,
                relating_control=flow_control, related_object=flow_element
            )
        """

        self.file = file
        self.settings = {
            "relating_flow_element": relating_flow_element,
            "related_flow_control": related_flow_control,
        }

    def execute(self):
        if not self.settings["related_flow_control"].AssignedToFlowElement:
            return
        assignment = self.settings["related_flow_control"].AssignedToFlowElement[0]
        if assignment.RelatingFlowElement != self.settings["relating_flow_element"]:
            return
        if len(assignment.RelatedControlElements) == 1:
            history = assignment.OwnerHistory
            self.file.remove(assignment)
            if history:
                ifcopenshell.util.element.remove_deep2(self.file, history)
            return
        related_flow_controls = list(assignment.RelatedControlElements)
        related_flow_controls.remove(self.settings["related_flow_control"])
        assignment.RelatedControlElements = related_flow_controls
        ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": assignment})
        return assignment
