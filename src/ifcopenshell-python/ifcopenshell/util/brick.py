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

import os
import json
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.classification
from typing import Union


cwd = os.path.dirname(os.path.realpath(__file__))

ifc4_to_brick_map = {}

with open(os.path.join(cwd, "ifc4_to_brick.json")) as f:
    ifc4_to_brick_map = json.load(f)


def get_brick_type(element: ifcopenshell.entity_instance) -> Union[str, None]:
    references = ifcopenshell.util.classification.get_references(element)
    for reference in references:
        system = ifcopenshell.util.classification.get_classification(reference)
        if system.Name == "Brick":
            return reference.Location
    result = None
    predefined_type = ifcopenshell.util.element.get_predefined_type(element)
    if predefined_type:
        result = ifc4_to_brick_map.get(f"{element.is_a()}.{predefined_type}", None)
    if not result:
        result = ifc4_to_brick_map.get(element.is_a(), None)
    if not result:
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type:
            ifc_type_class = element_type.is_a().replace("Type", "")
            result = ifc4_to_brick_map.get(f"{ifc_type_class}.{predefined_type}", None)
            if not result:
                result = ifc4_to_brick_map.get(ifc_type_class, None)
    if result:
        return f"https://brickschema.org/schema/Brick#{result}"
    # Generic fallback
    if element.is_a("IfcDistributionElement"):
        return f"https://brickschema.org/schema/Brick#Equipment"
    elif element.is_a("IfcSpatialElement") or element.is_a("IfcSpatialStructureElement"):
        return f"https://brickschema.org/schema/Brick#Location"
    elif element.is_a("IfcSystem"):
        return f"https://brickschema.org/schema/Brick#System"


def get_element_feeds(element: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
    current_element = element
    processed_elements = set()
    downstream_equipment: set[ifcopenshell.entity_instance] = set()

    # A queue is a list of branches. A branch is a list of elements in
    # sequence, each one connecting to another element. An element in a
    # branch may have a child queue. The queue and child queues are
    # acyclic.

    def extend_branch(element, branch, predecessor=None):
        processed_elements.add(element)
        branch_element = {"element": element, "children": [], "predecessor": predecessor}
        branch.append(branch_element)

        connected = {
            e
            for e in ifcopenshell.util.system.get_connected_to(element, flow_direction="SOURCE")
            if e not in processed_elements
        }
        connected.update(
            [
                e
                for e in ifcopenshell.util.system.get_connected_from(element, flow_direction="SOURCE")
                if e not in processed_elements
            ]
        )

        for connected_element in connected:
            if connected_element.is_a("IfcFlowFitting") or connected_element.is_a("IfcFlowSegment"):
                branch_element["children"].append(extend_branch(connected_element, [], element))
            else:
                downstream_equipment.add(connected_element)

        return branch

    extended_branch = extend_branch(current_element, [])
    return downstream_equipment
