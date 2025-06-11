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
import ifcopenshell.api.owner
import ifcopenshell.guid
from typing import Union


def assign_flow_control(
    file: ifcopenshell.file,
    relating_flow_element: ifcopenshell.entity_instance,
    related_flow_control: ifcopenshell.entity_instance,
) -> Union[ifcopenshell.entity_instance, None]:
    """Assigns to the flow element control element that either sense or control
    some aspect of the flow element.

    Note that control can be assigned only to the one flow element.

    :param related_flow_control: IfcDistributionControlElement
        which may be used to impart control on the flow element
    :param relating_flow_element: The IfcDistributionFlowElement that is being controlled / sensed
    :return: Matching or newly created IfcRelFlowControlElements. If control
        is already assigned to some other element method will return None.

    Example:

    .. code:: python

        flow_element = model.createIfcFlowSegment()
        flow_control = model.createIfcController()
        relation = ifcopenshell.api.system.assign_flow_control(
            model, related_flow_control=flow_control, relating_flow_element=flow_element
        )
    """
    if related_flow_control.AssignedToFlowElement:
        # only 1 control per 1 flow element is possible
        assignment = related_flow_control.AssignedToFlowElement[0]
        if assignment.RelatingFlowElement == relating_flow_element:
            return assignment
        # return None if this control is already assigned to another flow element
        return

    if relating_flow_element.HasControlElements:
        assignment = relating_flow_element.HasControlElements[0]
        if related_flow_control in assignment.RelatedControlElements:
            return assignment

        related_flow_controls = set(assignment.RelatedControlElements)
        related_flow_controls.add(related_flow_control)
        assignment.RelatedControlElements = list(related_flow_controls)
        ifcopenshell.api.owner.update_owner_history(file, element=assignment)
        return assignment

    assignment = file.create_entity(
        "IfcRelFlowControlElements",
        **{
            "GlobalId": ifcopenshell.guid.new(),
            "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
            "RelatedControlElements": [related_flow_control],
            "RelatingFlowElement": relating_flow_element,
        },
    )
    return assignment
