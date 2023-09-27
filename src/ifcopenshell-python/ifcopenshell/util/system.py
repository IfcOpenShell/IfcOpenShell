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


import ifcopenshell.util

group_types = {
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


def is_assignable(product, system) -> bool:
    for assignable in group_types.get(system.is_a(), ()):
        if product.is_a(assignable):
            return True
    return False


def get_system_elements(system):
    results = []
    for rel in system.IsGroupedBy:
        results.extend(rel.RelatedObjects)
    return results


def get_element_systems(element):
    results = []
    for rel in element.HasAssignments:
        if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.is_a() in (
            "IfcSystem",
            "IfcDistributionSystem",
            "IfcBuildingSystem",
            "IfcZone",
        ):
            results.append(rel.RelatingGroup)
    return results


def get_ports(element, flow_direction=None):
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


def get_connected_port(port):
    for rel in port.ConnectedTo:
        return rel.RelatedPort
    for rel in port.ConnectedFrom:
        return rel.RelatingPort


def get_port_element(port):
    if hasattr(port, "Nests"):
        for rel in port.Nests:
            return rel.RelatingObject
    # IFC2X3 only, deprecated in IFC4
    elif hasattr(port, "ContainedIn"):
        for rel in port.ContainedIn:
            return rel.RelatedElement


def get_connected_to(element, flow_direction=None):
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


def get_connected_from(element, flow_direction=None):
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
