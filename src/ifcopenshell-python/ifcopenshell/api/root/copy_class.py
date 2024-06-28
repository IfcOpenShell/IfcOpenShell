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
import ifcopenshell.api.root
import ifcopenshell.api.system
import ifcopenshell.api.geometry
import ifcopenshell.util.system
import ifcopenshell.util.element
import ifcopenshell.util.placement


def copy_class(file: ifcopenshell.file, product: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """Copies a product

    The following relationships are also duplicated:

    * The copy will have the same object placement coordinates as the
      original.
    * The copy will have duplicated property sets, properties, and quantities
    * The copy will have all nested distribution ports copied too
    * The copy will be part of the same aggregate
    * The copy will be contained in the same spatial structure
    * The copy, if it is an occurrence, will have the same type
    * Voids are duplicated too
    * The copy will have the same material as the original. Parametric
      material set usages will be copied.
    * The copy will be part of the same groups as the original.

    Be warned that:

    * Representations are _not_ copied. Copying representations is an
      expensive operation so for now the user is responsible for handling
      representations.
    * Filled voids are not copied, as there is no guarantee that the filling
      will also be copied.
    * Path connectivity is not copied, as there is no guarantee that the
      connections are still valid.

    :param product: The IfcProduct to copy.
    :type param: ifcopenshell.entity_instance
    :return: The copied product
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # We have a wall
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # And now we have two
        wall_copy = ifcopenshell.api.root.copy_class(model, product=wall)
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {"product": product}
    return usecase.execute()


class Usecase:
    def execute(self):
        result = ifcopenshell.util.element.copy(self.file, self.settings["product"])
        self.copy_direct_attributes(result)
        self.copy_indirect_attributes(self.settings["product"], result)
        return result

    def copy_direct_attributes(self, to_element):
        self.remove_representations(to_element)
        self.copy_object_placements(to_element)
        self.copy_psets(to_element)

    def copy_indirect_attributes(self, from_element, to_element):
        for inverse in self.file.get_inverse(from_element):
            if inverse.is_a("IfcRelDefinesByProperties"):
                # Properties must not be shared between objects for convenience of authoring
                inverse = ifcopenshell.util.element.copy(self.file, inverse)
                inverse.RelatedObjects = [to_element]
                pset = ifcopenshell.util.element.copy_deep(self.file, inverse.RelatingPropertyDefinition)
                inverse.RelatingPropertyDefinition = pset
            elif (
                inverse.is_a("IfcRelNests")
                and inverse.RelatingObject == from_element
                or inverse.is_a("IfcRelConnectsPortToElement")
                and inverse.RelatedElement == from_element
            ):
                # IfcRelConnectsPortToElement was used in IFC2X3
                if inverse.is_a("IfcRelNests"):
                    ports = [e for e in inverse.RelatedObjects if e.is_a("IfcDistributionPort")]
                else:  # IfcRelConnectsPortToElement
                    ports = [inverse.RelatingPort]
                if not ports:
                    continue
                new_ports = [ifcopenshell.api.root.copy_class(self.file, product=p) for p in ports]
                inverse = ifcopenshell.util.element.copy(self.file, inverse)

                if inverse.is_a("IfcRelNests"):
                    inverse.RelatingObject = to_element
                    inverse.RelatedObjects = new_ports
                else:
                    inverse.RelatedElement = to_element
                    inverse.RelatingPort = new_ports[0]

                for port in new_ports:
                    ifcopenshell.api.system.unassign_port(self.file, element=from_element, port=port)
                    ifcopenshell.api.system.disconnect_port(self.file, port=port)
                    matrix = ifcopenshell.util.placement.get_local_placement(port.ObjectPlacement)
                    ifcopenshell.api.geometry.edit_object_placement(
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
                if not opening.is_a("IfcOpeningElement") or not opening.HasFillings:
                    new_opening = ifcopenshell.api.root.copy_class(self.file, product=opening)
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
            elif inverse.is_a("IfcRelAssociatesMaterial") and "Set" in inverse.RelatingMaterial.is_a():
                inverse = ifcopenshell.util.element.copy(self.file, inverse)
                inverse.RelatingMaterial = ifcopenshell.util.element.copy_deep(
                    self.file, inverse.RelatingMaterial, exclude=["IfcMaterial"]
                )
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

    def copy_psets(self, element):
        if not element.is_a("IfcTypeObject") or not element.HasPropertySets:
            return
        element.HasPropertySets = [
            ifcopenshell.util.element.copy_deep(self.file, pset) for pset in element.HasPropertySets
        ]
