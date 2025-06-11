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


import ifcopenshell.util.system
from typing import Optional, Union, Literal

group_types: dict[str, tuple[str, ...]] = {
    "IfcZone": ("IfcZone", "IfcSpace", "IfcSpatialZone"),
    "IfcBuiltSystem": (
        "IfcBuiltElement",
        "IfcFurnishingElement",
        "IfcElementAssembly",
        "IfcTransportElement",
    ),
    "IfcBuildingSystem": (
        "IfcBuildingElement",
        "IfcFurnishingElement",
        "IfcElementAssembly",
        "IfcTransportElement",
    ),
    "IfcDistributionSystem": ("IfcDistributionElement",),
    "IfcStructuralAnalysisModel": ("IfcStructuralMember", "IfcStructuralConnection"),
    "IfcSystem": ("IfcProduct",),
    "IfcGroup": ("IfcObjectDefinition",),
}
# Subclasses.
group_types["IfcDistributionCircuit"] = group_types["IfcDistributionSystem"]
# Replaced by IfcDistributionCircuit in IFC4, though it wasn't limited to IfcDistributionElements:
# "Usage of IfcElectricalCircuit is as for the supertype IfcSystem".
group_types["IfcElectricalCircuit"] = group_types["IfcSystem"]


FLOW_DIRECTION = Literal["SINK", "SOURCE", "SOURCEANDSINK", "NOTEDEFINED"]


def is_assignable(product: ifcopenshell.entity_instance, system: ifcopenshell.entity_instance) -> bool:
    for assignable in group_types.get(system.is_a(), ()):
        if product.is_a(assignable):
            return True
    return False


def get_system_elements(system: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    results = []
    for rel in system.IsGroupedBy:
        results.extend(rel.RelatedObjects)
    return results


def get_element_systems(element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    results = []
    for rel in element.HasAssignments:
        if not rel.is_a("IfcRelAssignsToGroup"):
            continue
        group = rel.RelatingGroup
        if not group.is_a("IfcSystem") or group.is_a() in ("IfcStructuralAnalysisModel", "IfcZone"):
            continue
        results.append(group)
    return results


def get_element_zones(element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    results = []
    for rel in element.HasAssignments:
        if not rel.is_a("IfcRelAssignsToGroup"):
            continue
        group = rel.RelatingGroup
        if not group.is_a("IfcZone"):
            continue
        results.append(group)
    return results


def get_ports(
    element: ifcopenshell.entity_instance, flow_direction: Optional[FLOW_DIRECTION] = None
) -> list[ifcopenshell.entity_instance]:
    results = []
    for rel in getattr(element, "IsNestedBy", []) or []:
        for port in rel.RelatedObjects:
            if not port.is_a("IfcDistributionPort"):
                continue
            if flow_direction and port.FlowDirection != flow_direction:
                continue
            results.append(port)
    # IFC2X3 only, deprecated in IFC4
    for rel in getattr(element, "HasPorts", []) or []:
        port = rel.RelatingPort
        if flow_direction and port.FlowDirection != flow_direction:
            continue
        results.append(port)
    return results


def get_connected_port(port: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    for rel in port.ConnectedTo:
        return rel.RelatedPort
    for rel in port.ConnectedFrom:
        return rel.RelatingPort


def get_port_element(port: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    if hasattr(port, "Nests"):
        for rel in port.Nests:
            return rel.RelatingObject
    # IFC2X3 only, deprecated in IFC4
    elif hasattr(port, "ContainedIn"):
        for rel in port.ContainedIn:
            return rel.RelatedElement


def get_connected_to(
    element: ifcopenshell.entity_instance, flow_direction: Optional[FLOW_DIRECTION] = None
) -> list[ifcopenshell.entity_instance]:
    results = []
    for port in ifcopenshell.util.system.get_ports(element, flow_direction=flow_direction):
        for rel in port.ConnectedTo:
            for other_port in [rel.RelatedPort, rel.RelatingPort]:
                if other_port == port:
                    continue
                other_element = get_port_element(other_port)
                if other_element:
                    results.append(other_element)
    return results


def get_connected_from(
    element: ifcopenshell.entity_instance, flow_direction: Optional[FLOW_DIRECTION] = None
) -> list[ifcopenshell.entity_instance]:
    results = []
    for port in ifcopenshell.util.system.get_ports(element, flow_direction=flow_direction):
        for rel in port.ConnectedFrom:
            for other_port in [rel.RelatedPort, rel.RelatingPort]:
                if other_port == port:
                    continue
                other_element = get_port_element(other_port)
                if other_element:
                    results.append(other_element)
    return results
