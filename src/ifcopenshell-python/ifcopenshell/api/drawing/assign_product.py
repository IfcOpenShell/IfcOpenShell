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
import ifcopenshell.guid


def assign_product(
    file: ifcopenshell.file,
    relating_product: ifcopenshell.entity_instance,
    related_object: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:
    """Associates a product and an object, typically for annotation

    Warning: this is an experimental API.

    When you want to draw attention to a feature or characteristic (such as
    a dimension, material, or name) or of a product (e.g. wall, slab,
    furniture, etc), an annotation object is created. This annotation is
    then associated with the product so that it can reference attributes,
    properties, and relationships.

    For example, an annotation of a line will be associated with a grid
    axis, such that when that grid axis moves, the annotation of that grid
    axis (which is typically truncated to the extents of a drawing) will
    also move.

    Another example might be a label of a furniture product, which might
    have some text of the name of the furniture to be shown on drawings or
    in 3D.

    :param relating_product: The IfcProduct the object is related to
    :type relating_product: ifcopenshell.entity_instance
    :param related_object: The object (typically IfcAnnotation) that the
        product is related to
    :type related_object: ifcopenshell.entity_instance
    :return: The created IfcRelAssignsToProduct relationship
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        furniture = ifcopenshell.api.root.create_entity(model, ifc_class="IfcFurniture")
        annotation = ifcopenshell.api.root.create_entity(model, ifc_class="IfcAnnotation")
        ifcopenshell.api.drawing.assign_product(model,
            relating_product=furniture, related_object=annotation)
    """
    settings = {
        "relating_product": relating_product,
        "related_object": related_object,
    }

    is_grid_axis = settings["relating_product"].is_a("IfcGridAxis")

    if is_grid_axis:
        if settings["related_object"].HasAssignments:
            for rel in settings["related_object"].HasAssignments:
                if rel.is_a("IfcRelAssignsToProduct") and rel.Name == settings["relating_product"].AxisTag:
                    return
    elif settings["related_object"].HasAssignments:
        for rel in settings["related_object"].HasAssignments:
            if rel.is_a("IfcRelAssignsToProduct") and rel.RelatingProduct == settings["relating_product"]:
                return

    referenced_by = None

    if is_grid_axis:
        axis = settings["relating_product"]
        grid = None
        for attribute in ("PartOfW", "PartOfV", "PartOfU"):
            if getattr(axis, attribute, None):
                grid = getattr(axis, attribute)[0]
        settings["relating_product"] = grid
        for rel in grid.ReferencedBy:
            if rel.Name == axis.AxisTag:
                referenced_by = rel
                break
    elif settings["relating_product"].ReferencedBy:
        referenced_by = settings["relating_product"].ReferencedBy[0]

    if referenced_by:
        related_objects = list(referenced_by.RelatedObjects)
        related_objects.append(settings["related_object"])
        referenced_by.RelatedObjects = related_objects
        ifcopenshell.api.owner.update_owner_history(file, **{"element": referenced_by})
    else:
        referenced_by = file.create_entity(
            "IfcRelAssignsToProduct",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
                "RelatedObjects": [settings["related_object"]],
                "RelatingProduct": settings["relating_product"],
            },
        )

    if is_grid_axis:
        referenced_by.Name = axis.AxisTag
    return referenced_by
