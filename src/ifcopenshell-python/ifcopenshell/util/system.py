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
    from blenderbim.bim.ifc import IfcStore
    ifcSchema = IfcStore.get_file().schema
    results = []
    if ifcSchema == "IFC4":
        for port in ifcopenshell.util.system.get_ports(element):
            for relConnectsPort in port.ConnectedTo:
                for relNest in relConnectsPort.RelatedPort.Nests:
                    results.extend(relNest.RelatingObject)
    elif ifcSchema == "IFC2X3":
        for port in element.HasPorts:
            for relConnectsPort in port.RelatingPort.ConnectedTo:
                results.extend([r.RelatedElement for r in relConnectsPort.RelatedPort.ContainedIn if r.RelatedElement != element])
    return results

def get_connected_from(element):
    from blenderbim.bim.ifc import IfcStore
    ifcSchema = IfcStore.get_file().schema
    results = []
    if ifcSchema == "IFC4":
        for port in ifcopenshell.util.system.get_ports(element):
            for relConnectsPort in port.ConnectedFrom:
                for relNest in relConnectsPort.RelatedPort.Nests:
                    results.extend(relNest.RelatingObject)
    elif ifcSchema == "IFC2X3":
        for port in element.HasPorts:
            for relConnectsPort in port.RelatingPort.ConnectedFrom:
                results.extend([r.RelatedElement for r in relConnectsPort.RelatingPort.ContainedIn if r.RelatedElement != element])
    return results