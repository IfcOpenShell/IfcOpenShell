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

import ifcopenshell.api.type
import ifcopenshell.api.grid
import ifcopenshell.api.feature
import ifcopenshell.api.root
import ifcopenshell.api.pset
import ifcopenshell.api.boundary
import ifcopenshell.api.material
import ifcopenshell.api.geometry
import ifcopenshell.util.element


def remove_product(file: ifcopenshell.file, product: ifcopenshell.entity_instance) -> None:
    """Removes a product

    This is effectively a smart delete function that not only removes a
    product, but also all of its relationships. It is always recommended to
    use this function to prevent orphaned data in your IFC model.

    This is intended to be used for removing:

    - IfcAnnotation
    - IfcElement
    - IfcElementType
    - IfcSpatialElement
    - IfcSpatialElementType

    For example, geometric representations are removed. Placement
    coordinates are also removed. Properties are removed. Material, type,
    containment, aggregation, and nesting relationships are removed (but
    naturally, the materials, types, containers, etc themselves remain).

    :param product: The element to remove.
    :return: None

    Example:

    .. code:: python

        # We have a wall.
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # No we don't.
        ifcopenshell.api.root.remove_product(model, product=wall)
    """
    representations: list[ifcopenshell.entity_instance] = []
    if product.is_a("IfcProduct"):
        if product.Representation:
            representations = product.Representation.Representations or []
        else:
            representations = []

        # remove object placements
        object_placement = product.ObjectPlacement
        if object_placement:
            if file.get_total_inverses(object_placement) == 1:
                product.ObjectPlacement = None  # remove the inverse for remove_deep2 to work
                ifcopenshell.util.element.remove_deep2(file, object_placement)

    elif product.is_a("IfcTypeProduct"):
        representations = [rm.MappedRepresentation for rm in product.RepresentationMaps or []]

        # remove psets
        psets = product.HasPropertySets or []
        for pset in psets:
            if file.get_total_inverses(pset) != 1:
                continue
            ifcopenshell.api.pset.remove_pset(file, product=product, pset=pset)

    for representation in representations:
        ifcopenshell.api.geometry.unassign_representation(file, product=product, representation=representation)
        ifcopenshell.api.geometry.remove_representation(file, representation=representation)
    for opening in getattr(product, "HasOpenings", []) or []:
        ifcopenshell.api.feature.remove_feature(file, feature=opening.RelatedOpeningElement)

    if product.is_a("IfcGrid"):
        for axis in product.UAxes + product.VAxes + (product.WAxes or ()):
            ifcopenshell.api.grid.remove_grid_axis(file, axis=axis)

    def element_exists(element_id):
        try:
            file.by_id(element_id)
            return True
        except RuntimeError:
            return False

    # TODO: remove object placement and other relationships
    for inverse_id in [i.id() for i in file.get_inverse(product)]:
        try:
            inverse = file.by_id(inverse_id)
        except:
            continue
        if inverse.is_a("IfcRelDefinesByProperties"):
            ifcopenshell.api.pset.remove_pset(file, product=product, pset=inverse.RelatingPropertyDefinition)
        elif inverse.is_a("IfcRelAssociatesMaterial"):
            ifcopenshell.api.material.unassign_material(file, products=[product])
        elif inverse.is_a("IfcRelDefinesByType"):
            if inverse.RelatingType == product:
                ifcopenshell.api.type.unassign_type(file, related_objects=inverse.RelatedObjects)
            else:
                ifcopenshell.api.type.unassign_type(file, related_objects=[product])
        elif inverse.is_a("IfcRelSpaceBoundary"):
            ifcopenshell.api.boundary.remove_boundary(file, boundary=inverse)
        elif inverse.is_a("IfcRelFillsElement"):
            history = inverse.OwnerHistory
            file.remove(inverse)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelVoidsElement"):
            history = inverse.OwnerHistory
            file.remove(inverse)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelServicesBuildings"):
            history = inverse.OwnerHistory
            file.remove(inverse)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelNests"):
            if inverse.RelatingObject == product:
                inverse_id = inverse.id()
                for subelement in inverse.RelatedObjects:
                    if subelement.is_a("IfcDistributionPort"):
                        ifcopenshell.api.root.remove_product(file, product=subelement)
                # IfcRelNests could have been already deleted after removing one of the products
                if element_exists(inverse_id):
                    history = inverse.OwnerHistory
                    file.remove(inverse)
                    if history:
                        ifcopenshell.util.element.remove_deep2(file, history)
            elif inverse.RelatedObjects == (product,):
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelAggregates"):
            if inverse.RelatingObject == product or len(inverse.RelatedObjects) == 1:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelContainedInSpatialStructure"):
            if inverse.RelatingStructure == product or len(inverse.RelatedElements) == 1:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelConnectsElements"):
            if inverse.is_a("IfcRelConnectsWithRealizingElements"):
                if product not in (inverse.RelatingElement, inverse.RelatedElement) and any(
                    el for el in inverse.RealizingElements if el != product
                ):
                    continue
            history = inverse.OwnerHistory
            file.remove(inverse)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelConnectsPortToElement"):
            if inverse.RelatedElement == product:
                ifcopenshell.api.root.remove_product(file, product=inverse.RelatingPort)
            elif inverse.RelatingPort == product:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelConnectsPorts"):
            if product not in (inverse.RelatingPort, inverse.RelatedPort):
                # if it's not RelatingPort/RelatedPort then it's optional RealizingElement
                # so we keep the relationship
                continue
            history = inverse.OwnerHistory
            file.remove(inverse)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelAssignsToGroup"):
            if len(inverse.RelatedObjects) == 1:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelAssignsToProduct"):
            if inverse.RelatingProduct == product:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
            elif len(inverse.RelatedObjects) == 1:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelFlowControlElements"):
            if inverse.RelatingFlowElement == product:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
            elif inverse.RelatedControlElements == (product,):
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
    history = product.OwnerHistory
    file.remove(product)
    if history:
        ifcopenshell.util.element.remove_deep2(file, history)
