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


def get_ports(element):
    results = []
    for rel in getattr(element, "IsNestedBy", []) or []:
        results.extend([o for o in rel.RelatedObjects if o.is_a("IfcDistributionPort")])
    # IFC2X3 only, deprecated in IFC4
    for rel in getattr(element, "HasPorts", []) or []:
        results.append(rel.RelatingPort)
    return results


def get_connected_port(port):
    for rel in port.ConnectedTo:
        return rel.RelatedPort
    for rel in port.ConnectedFrom:
        return rel.RelatingPort


def get_connected_to(element):
    results = []
    for port in ifcopenshell.util.system.get_ports(element):
        for relConnectsPort in port.ConnectedTo:
            for disPort in [relConnectsPort.RelatedPort,relConnectsPort.RelatingPort]:
                if hasattr(disPort,"Nests"):
                    for relNest in disPort.Nests:
                        if relNest.RelatingObject != element:
                            results.append(relNest.RelatingObject)
                # IFC2X3 only, deprecated in IFC4
                elif hasattr(disPort,"ContainedIn"):
                    for relConPortToElement in disPort.ContainedIn:
                        if relConPortToElement.RelatedElement != element:
                            results.append(relConPortToElement.RelatedElement)
    return(results)


def get_connected_from(element):
    results = []
    for port in ifcopenshell.util.system.get_ports(element):
        for relConnectsPort in port.ConnectedFrom:
            for disPort in [relConnectsPort.RelatedPort,relConnectsPort.RelatingPort]:
                if hasattr(disPort,"Nests"):
                    for relNest in disPort.Nests:
                        if relNest.RelatingObject != element:
                            results.append(relNest.RelatingObject)
                # IFC2X3 only, deprecated in IFC4
                elif hasattr(disPort,"ContainedIn"):
                    for relConPortToElement in disPort.ContainedIn:
                        if relConPortToElement.RelatedElement != element:
                            results.append(relConPortToElement.RelatedElement)
    return(results)