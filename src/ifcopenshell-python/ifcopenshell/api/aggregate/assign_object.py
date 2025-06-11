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
import ifcopenshell.api.owner
import ifcopenshell.api.spatial
import ifcopenshell.api.geometry
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.placement
from typing import Union


def assign_object(
    file: ifcopenshell.file,
    products: list[ifcopenshell.entity_instance],
    relating_object: ifcopenshell.entity_instance,
) -> Union[ifcopenshell.entity_instance, None]:
    """Assigns object as an aggregate to the products

    All physical IFC model elements must be part of a hierarchical tree
    called the "spatial decomposition", where large things are made up of
    smaller things. This tree always begins at an "IfcProject" and is then
    broken down using "decomposition" relationships, of which aggregation is
    the first relationship you will use.

    Typically used when you want to describe how large spaces are made up of
    smaller spaces. For example large spatial elements (e.g. sites,
    buidings) can be made out of smaller spatial elements (e.g. storeys,
    spaces).

    The largest space (typically the IfcSite) can then be aggregated in a
    project. It is requirement for all spatial structures to be directly or
    indirectly aggregated back to the IfcProject to create a hierarchy of
    spaces.

    The other common usecase is when larger physical products are made up of
    smaller physical products. For example, a stair might be made out of a
    flight, a landing, a railing and so on. Or a wall might be made out of
    stud members, and coverings.

    As a product may only have a single location in the "spatial
    decomposition" tree, assigning an aggregate relationship will remove any
    previous aggregation, containment, or nesting relationships it may have.

    IFC placements follow a convention where the placement is relative to
    its parent in the spatial hierarchy. If your product has a placement,
    its placement will be recalculated to follow this convention.

    :param products: The list of parts of the aggregate, typically of IfcElement or
        IfcSpatialStructureElement subclass
    :param relating_object: The whole of the aggregate, typically an
        IfcElement or IfcSpatialStructureElement subclass
    :return: The IfcRelAggregate relationship instance
        or `None` if `products` was empty list.

    Example:

    .. code:: python

        project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
        element = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite")
        subelement = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding")

        # The project contains a site (note that project aggregation is a special case in IFC)
        ifcopenshell.api.aggregate.assign_object(model, products=[element], relating_object=project)

        # The site has a building
        ifcopenshell.api.aggregate.assign_object(model, products=[subelement], relating_object=element)
    """
    if not products:
        return

    products_set = set(products)
    is_decomposed_by = next((i for i in relating_object.IsDecomposedBy if i.is_a("IfcRelAggregates")), None)

    previous_aggregates_rels: set[ifcopenshell.entity_instance] = set()
    products_without_aggregates: list[ifcopenshell.entity_instance] = []
    products_with_aggregates: list[ifcopenshell.entity_instance] = []

    # check if there is anything to change
    for product in products_set:
        product_rel = next(iter(product.Decomposes), None)

        if product_rel is None:
            products_without_aggregates.append(product)
            continue

        # either is_decomposed_by is None or product is part of different rel
        if product_rel != is_decomposed_by:
            previous_aggregates_rels.add(product_rel)
            products_with_aggregates.append(product)

        # products with already assigned aggregates will be skipped

    products_to_change = products_without_aggregates + products_with_aggregates
    # nothing to change
    if not products_to_change:
        return is_decomposed_by

    # can be either only aggregated or only contained at the same time
    # some product might not be able to have a container
    possibly_contained_products = [p for p in products_without_aggregates if hasattr(p, "ContainedInStructure")]
    ifcopenshell.api.spatial.unassign_container(file, products=possibly_contained_products)

    # unassign elements from previous aggregates
    for decomposes in previous_aggregates_rels:
        related_objects = set(decomposes.RelatedObjects) - products_set
        if related_objects:
            decomposes.RelatedObjects = list(related_objects)
            ifcopenshell.api.owner.update_owner_history(file, element=decomposes)
        else:
            history = decomposes.OwnerHistory
            file.remove(decomposes)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)

    # assign elements to a new aggregate
    if is_decomposed_by:
        is_decomposed_by.RelatedObjects = list(set(is_decomposed_by.RelatedObjects) | products_set)
        ifcopenshell.api.owner.update_owner_history(file, element=is_decomposed_by)
    else:
        is_decomposed_by = file.create_entity(
            "IfcRelAggregates",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
                "RelatedObjects": list(products_set),
                "RelatingObject": relating_object,
            }
        )

    # localize placement relative to a new aggregate for affected products
    for product in products_to_change:
        placement = getattr(product, "ObjectPlacement", None)
        if placement and placement.is_a("IfcLocalPlacement"):
            ifcopenshell.api.geometry.edit_object_placement(
                file,
                product=product,
                matrix=ifcopenshell.util.placement.get_local_placement(product.ObjectPlacement),
                is_si=False,
            )

    return is_decomposed_by
