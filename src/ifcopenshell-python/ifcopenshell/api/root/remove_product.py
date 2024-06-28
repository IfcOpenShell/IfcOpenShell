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
import ifcopenshell.api.void
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
    :type product: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # We have a wall.
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # No we don't.
        ifcopenshell.api.root.remove_product(model, product=wall)
    """
    settings = {"product": product}

    representations = []
    if settings["product"].is_a("IfcProduct"):
        if settings["product"].Representation:
            representations = settings["product"].Representation.Representations or []
        else:
            representations = []

        # remove object placements
        object_placement = settings["product"].ObjectPlacement
        if object_placement:
            if file.get_total_inverses(object_placement) == 1:
                settings["product"].ObjectPlacement = None  # remove the inverse for remove_deep2 to work
                ifcopenshell.util.element.remove_deep2(file, object_placement)

    elif settings["product"].is_a("IfcTypeProduct"):
        representations = [rm.MappedRepresentation for rm in settings["product"].RepresentationMaps or []]

        # remove psets
        psets = settings["product"].HasPropertySets or []
        for pset in psets:
            if file.get_total_inverses(pset) != 1:
                continue
            ifcopenshell.api.pset.remove_pset(file, product=settings["product"], pset=pset)

    for representation in representations:
        ifcopenshell.api.geometry.unassign_representation(
            file, product=settings["product"], representation=representation
        )
        ifcopenshell.api.geometry.remove_representation(file, **{"representation": representation})
    for opening in getattr(settings["product"], "HasOpenings", []) or []:
        ifcopenshell.api.void.remove_opening(file, opening=opening.RelatedOpeningElement)

    if settings["product"].is_a("IfcGrid"):
        for axis in settings["product"].UAxes + settings["product"].VAxes + (settings["product"].WAxes or ()):
            ifcopenshell.api.grid.remove_grid_axis(file, axis=axis)

    def element_exists(element_id):
        try:
            file.by_id(element_id)
            return True
        except RuntimeError:
            return False

    # TODO: remove object placement and other relationships
    for inverse_id in [i.id() for i in file.get_inverse(settings["product"])]:
        try:
            inverse = file.by_id(inverse_id)
        except:
            continue
        if inverse.is_a("IfcRelDefinesByProperties"):
            ifcopenshell.api.pset.remove_pset(
                file, product=settings["product"], pset=inverse.RelatingPropertyDefinition
            )
        elif inverse.is_a("IfcRelAssociatesMaterial"):
            ifcopenshell.api.material.unassign_material(file, products=[settings["product"]])
        elif inverse.is_a("IfcRelDefinesByType"):
            if inverse.RelatingType == settings["product"]:
                ifcopenshell.api.type.unassign_type(file, related_objects=inverse.RelatedObjects)
            else:
                ifcopenshell.api.type.unassign_type(file, related_objects=[settings["product"]])
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
            if inverse.RelatingObject == settings["product"]:
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
            elif inverse.RelatedObjects == (settings["product"],):
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelAggregates"):
            if inverse.RelatingObject == settings["product"] or len(inverse.RelatedObjects) == 1:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelContainedInSpatialStructure"):
            if inverse.RelatingStructure == settings["product"] or len(inverse.RelatedElements) == 1:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelConnectsElements"):
            if inverse.is_a("IfcRelConnectsWithRealizingElements"):
                if settings["product"] not in (inverse.RelatingElement, inverse.RelatedElement) and any(
                    el for el in inverse.RealizingElements if el != settings["product"]
                ):
                    continue
            history = inverse.OwnerHistory
            file.remove(inverse)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelConnectsPortToElement"):
            if inverse.RelatedElement == settings["product"]:
                ifcopenshell.api.root.remove_product(file, product=inverse.RelatingPort)
            elif inverse.RelatingPort == settings["product"]:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelConnectsPorts"):
            if settings["product"] not in (inverse.RelatingPort, inverse.RelatedPort):
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
            if inverse.RelatingProduct == settings["product"]:
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
            if inverse.RelatingFlowElement == settings["product"]:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
            elif inverse.RelatedControlElements == (settings["product"],):
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
    history = settings["product"].OwnerHistory
    file.remove(settings["product"])
    if history:
        ifcopenshell.util.element.remove_deep2(file, history)
