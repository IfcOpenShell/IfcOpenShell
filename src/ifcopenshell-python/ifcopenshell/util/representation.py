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

import numpy as np
import ifcopenshell
import ifcopenshell.util.placement
from typing import Optional, Union, TypedDict


def get_context(
    ifc_file: ifcopenshell.file,
    context: str,
    subcontext: Optional[str] = None,
    target_view: Optional[str] = None,
) -> Union[ifcopenshell.entity_instance, None]:
    if subcontext or target_view:
        elements = ifc_file.by_type("IfcGeometricRepresentationSubContext")
    else:
        elements = ifc_file.by_type("IfcGeometricRepresentationContext", include_subtypes=False)
    for element in elements:
        if context and element.ContextType != context:
            continue
        if subcontext and getattr(element, "ContextIdentifier") != subcontext:
            continue
        if target_view and getattr(element, "TargetView") != target_view:
            continue
        return element


def is_representation_of_context(
    representation: ifcopenshell.entity_instance,
    context: Union[ifcopenshell.entity_instance, str],
    subcontext: Optional[str] = None,
    target_view: Optional[str] = None,
) -> bool:
    if isinstance(context, ifcopenshell.entity_instance):
        return representation.ContextOfItems == context

    if target_view is not None:
        return (
            representation.ContextOfItems.is_a("IfcGeometricRepresentationSubContext")
            and representation.ContextOfItems.TargetView == target_view
            and representation.ContextOfItems.ContextIdentifier == subcontext
            and representation.ContextOfItems.ContextType == context
        )
    elif subcontext is not None:
        return (
            representation.ContextOfItems.is_a("IfcGeometricRepresentationSubContext")
            and representation.ContextOfItems.ContextIdentifier == subcontext
            and representation.ContextOfItems.ContextType == context
        )

    return representation.ContextOfItems.ContextType == context


def get_representation(
    element: ifcopenshell.entity_instance,
    context: Union[ifcopenshell.entity_instance, str],
    subcontext: Optional[str] = None,
    target_view: Optional[str] = None,
) -> Union[ifcopenshell.entity_instance, None]:
    if element.is_a("IfcProduct") and element.Representation:
        for r in element.Representation.Representations:
            if is_representation_of_context(r, context, subcontext, target_view):
                return r
    elif element.is_a("IfcTypeProduct") and element.RepresentationMaps:
        for r in element.RepresentationMaps:
            if is_representation_of_context(r.MappedRepresentation, context, subcontext, target_view):
                return r.MappedRepresentation


def resolve_representation(representation: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """Resolve possibly mapped representation.

    :param representation: IfcRepresentation
    :type representation: ifcopenshell.entity_instance.entity_instance
    :return: Representation resolved from mappings
    :rtype: ifcopenshell.entity_instance.entity_instance
    """
    if len(representation.Items) == 1 and representation.Items[0].is_a("IfcMappedItem"):
        return resolve_representation(representation.Items[0].MappingSource.MappedRepresentation)
    return representation


class ResolvedItemDict(TypedDict):
    matrix: np.array
    item: ifcopenshell.entity_instance


def resolve_items(
    representation: ifcopenshell.entity_instance, matrix: Optional[np.array] = None
) -> list[ResolvedItemDict]:
    if matrix is None:
        matrix = np.eye(4)
    results: list[ResolvedItemDict] = []
    for item in representation.Items or []:  # Be forgiving of invalid IFCs because Revit :(
        if item.is_a("IfcMappedItem"):
            rep_matrix = ifcopenshell.util.placement.get_mappeditem_transformation(item)
            if not np.allclose(rep_matrix, np.eye(4)):
                rep_matrix = rep_matrix @ matrix.copy()
            results.extend(resolve_items(item.MappingSource.MappedRepresentation, rep_matrix))
        else:
            results.append(ResolvedItemDict(matrix=matrix.copy(), item=item))
    return results
