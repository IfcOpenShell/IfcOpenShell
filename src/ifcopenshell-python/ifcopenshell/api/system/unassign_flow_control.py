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


def unassign_flow_control(
    file: ifcopenshell.file,
    relating_flow_element: ifcopenshell.entity_instance,
    related_flow_control: ifcopenshell.entity_instance,
) -> None:
    """Unassigns flow control element from the flow element.

    :param related_flow_control: IfcDistributionControlElement controling the
        flow element
    :type related_flow_control: ifcopenshell.entity_instance
    :param relating_flow_element: The IfcDistributionFlowElement that is being controlled
    :type relating_flow_element: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # assign control to the flow element
        flow_element = file.createIfcFlowSegment()
        flow_control = file.createIfcController()
        relation = ifcopenshell.api.run(
            "system.assign_flow_control", file,
            relating_control=flow_control, related_object=flow_element
        )

        # und unassign it
        ifcopenshell.api.run("system.unassign_flow_control", file,
            relating_control=flow_control, related_object=flow_element
        )
    """

    settings = {
        "relating_flow_element": relating_flow_element,
        "related_flow_control": related_flow_control,
    }

    if not settings["related_flow_control"].AssignedToFlowElement:
        return
    assignment = settings["related_flow_control"].AssignedToFlowElement[0]
    if assignment.RelatingFlowElement != settings["relating_flow_element"]:
        return
    if len(assignment.RelatedControlElements) == 1:
        history = assignment.OwnerHistory
        file.remove(assignment)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
        return
    related_flow_controls = list(assignment.RelatedControlElements)
    related_flow_controls.remove(settings["related_flow_control"])
    assignment.RelatedControlElements = related_flow_controls
    ifcopenshell.api.run("owner.update_owner_history", file, **{"element": assignment})
