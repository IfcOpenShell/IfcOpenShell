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
import ifcopenshell.util.system
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        result = ifcopenshell.util.element.copy(self.file, self.settings["product"])
        self.copy_direct_attributes(result)
        self.copy_indirect_attributes(self.settings["product"], result)
        return result

    def copy_direct_attributes(self, to_element):
        self.remove_representations(to_element)
        self.copy_object_placements(to_element)

    def copy_indirect_attributes(self, from_element, to_element):
        for inverse in self.file.get_inverse(from_element):
            if inverse.is_a("IfcRelDefinesByProperties"):
                # Properties must not be shared between objects for convenience of authoring
                inverse = ifcopenshell.util.element.copy(self.file, inverse)
                inverse.RelatedObjects = [to_element]
                pset = ifcopenshell.util.element.copy_deep(self.file, inverse.RelatingPropertyDefinition)
                inverse.RelatingPropertyDefinition = pset
            elif inverse.is_a("IfcRelNests") and inverse.RelatingObject == from_element:
                ports = [e for e in inverse.RelatedObjects if e.is_a("IfcDistributionPort")]
                if ports:
                    new_ports = [ifcopenshell.api.run("root.copy_class", self.file, product=p) for p in ports]
                    inverse = ifcopenshell.util.element.copy(self.file, inverse)
                    inverse.RelatingObject = to_element
                    inverse.RelatedObjects = new_ports
                    for port in new_ports:
                        ifcopenshell.api.run("system.unassign_port", self.file, element=from_element, port=port)
                        matrix = ifcopenshell.util.placement.get_local_placement(port.ObjectPlacement)
                        ifcopenshell.api.run(
                            "geometry.edit_object_placement",
                            self.file,
                            product=port,
                            matrix=matrix,
                            is_si=False,
                            should_transform_children=False,
                        )
            elif inverse.is_a("IfcRelAggregates") and inverse.RelatingObject == from_element:
                continue
            elif inverse.is_a("IfcRelContainedInSpatialStructure") and inverse.RelatingStructure == from_element:
                continue
            elif inverse.is_a("IfcRelDefinesByType") and inverse.RelatingType == from_element:
                continue
            elif inverse.is_a("IfcRelVoidsElement") and inverse.RelatingBuildingElement == from_element:
                opening = inverse.RelatedOpeningElement
                # We don't copy filled openings, since there is no guarantee the filling is also copied
                if not opening.HasFillings:
                    new_opening = ifcopenshell.api.run("root.copy_class", self.file, product=opening)
                    new_opening.VoidsElements[0].RelatingBuildingElement = to_element
                    if new_opening.ObjectPlacement and new_opening.ObjectPlacement.is_a("IfcLocalPlacement"):
                        if to_element.ObjectPlacement:
                            new_opening.ObjectPlacement.PlacementRelTo = to_element.ObjectPlacement
                    # For now, we do copy opening representations
                    if opening.Representation:
                        new_opening.Representation = ifcopenshell.util.element.copy_deep(
                            self.file, opening.Representation, exclude=["IfcGeometricRepresentationContext"]
                        )
            elif inverse.is_a("IfcRelFillsElement"):
                continue
            elif inverse.is_a("IfcRelConnectsPathElements"):
                continue
            elif inverse.is_a("IfcRelAssociatesMaterial") and "Usage" in inverse.RelatingMaterial.is_a():
                inverse = ifcopenshell.util.element.copy(self.file, inverse)
                inverse.RelatingMaterial = ifcopenshell.util.element.copy(self.file, inverse.RelatingMaterial)
                inverse.RelatedObjects = [to_element]
            elif inverse.is_a("IfcRelAssociatesMaterial") and from_element.is_a("IfcTypeProduct"):
                inverse = ifcopenshell.util.element.copy(self.file, inverse)
                inverse.RelatingMaterial = ifcopenshell.util.element.copy(self.file, inverse.RelatingMaterial)
                inverse.RelatedObjects = [to_element]
            else:
                for i, value in enumerate(inverse):
                    if value == from_element:
                        new_inverse = ifcopenshell.util.element.copy(self.file, inverse)
                        new_inverse[i] = to_element
                    elif isinstance(value, (tuple, list)) and from_element in value:
                        new_value = list(value)
                        new_value.append(to_element)
                        inverse[i] = new_value

    def remove_representations(self, element):
        if element.is_a("IfcProduct"):
            element.Representation = None
        elif element.is_a("IfcTypeProduct"):
            element.RepresentationMaps = None

    def copy_object_placements(self, element):
        if not element.is_a("IfcProduct") or not element.ObjectPlacement:
            return
        element.ObjectPlacement = ifcopenshell.util.element.copy(self.file, element.ObjectPlacement)
        element.ObjectPlacement.RelativePlacement = ifcopenshell.util.element.copy_deep(
            self.file, element.ObjectPlacement.RelativePlacement
        )
