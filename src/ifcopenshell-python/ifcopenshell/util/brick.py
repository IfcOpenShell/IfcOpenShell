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


cwd = os.path.dirname(os.path.realpath(__file__))

ifc4_to_brick_map = {}

with open(os.path.join(cwd, "ifc4_to_brick.json")) as f:
    ifc4_to_brick_map = json.load(f)


def get_brick_type(element):
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
    # We choose equipment as a generic fallback
    return f"https://brickschema.org/schema/Brick#Equipment"


def get_brick_elements(ifc_file):
    elements = set(ifc_file.by_type("IfcDistributionElement"))
    elements = elements.difference(ifc_file.by_type("IfcFlowSegment"))
    elements = elements.difference(ifc_file.by_type("IfcFlowFitting"))
    return elements
