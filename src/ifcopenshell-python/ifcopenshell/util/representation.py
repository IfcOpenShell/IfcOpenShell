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
import numpy.typing as npt
import ifcopenshell
import ifcopenshell.util.placement
from typing import Optional, Union, TypedDict, Literal


CONTEXT_TYPE = Literal["Model", "Plan", "NotDefined"]
REPRESENTATION_IDENTIFIER = Literal[
    "CoG",
    "Box",
    "Annotation",
    "Axis",
    "FootPrint",
    "Profile",
    "Surface",
    "Reference",
    "Body",
    "Body-Fallback",
    "Clearance",
    "Lighting",
]
TARGET_VIEW = Literal[
    "ELEVATION_VIEW",
    "GRAPH_VIEW",
    "MODEL_VIEW",
    "PLAN_VIEW",
    "REFLECTED_PLAN_VIEW",
    "SECTION_VIEW",
    "SKETCH_VIEW",
    "USERDEFINED",
    "NOTDEFINED",
]


def get_context(
    ifc_file: ifcopenshell.file,
    context: CONTEXT_TYPE,
    subcontext: Optional[REPRESENTATION_IDENTIFIER] = None,
    target_view: Optional[TARGET_VIEW] = None,
) -> Union[ifcopenshell.entity_instance, None]:
    """Get IfcGeometricRepresentationSubContext by the provided context type, identifier, and target view.

    :param context: ContextType.
    :param subcontext: A ContextIdentifier string, or any if left blank.
    :param target_view: A TargetView string, or any if left blank.
    """

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
    context: Union[ifcopenshell.entity_instance, CONTEXT_TYPE],
    subcontext: Optional[REPRESENTATION_IDENTIFIER] = None,
    target_view: Optional[TARGET_VIEW] = None,
) -> bool:
    """Check if representation has specified context or context type, identifier, and target view.

    :param representation: IfcShapeRepresentation.
    :param context: Either a specific IfcGeometricRepresentationContext or a ContextType.
    :param subcontext: A ContextIdentifier string, or any if left blank.
    :param target_view: A TargetView string, or any if left blank.
    """

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
    context: Union[ifcopenshell.entity_instance, CONTEXT_TYPE],
    subcontext: Optional[REPRESENTATION_IDENTIFIER] = None,
    target_view: Optional[TARGET_VIEW] = None,
) -> Union[ifcopenshell.entity_instance, None]:
    """Gets a IfcShapeRepresentation filtered by the context type, identifier, and target view

    :param element: An IfcProduct or IfcTypeProduct
    :param context: Either a specific IfcGeometricRepresentationContext or a ContextType
    :param subcontext: A ContextIdentifier string, or any if left blank.
    :param target_view: A TargetView string, or any if left blank.
    :return: The first IfcShapeRepresentation matching the criteria.
    """
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
    :return: Representation resolved from mappings
    """
    if len(representation.Items) == 1 and representation.Items[0].is_a("IfcMappedItem"):
        return resolve_representation(representation.Items[0].MappingSource.MappedRepresentation)
    return representation


class ResolvedItemDict(TypedDict):
    matrix: npt.NDArray[np.float64]
    item: ifcopenshell.entity_instance


def resolve_items(
    representation: ifcopenshell.entity_instance, matrix: Optional[npt.NDArray[np.float64]] = None
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


def get_prioritised_contexts(ifc_file: ifcopenshell.file) -> list[ifcopenshell.entity_instance]:
    """Gets a list of contexts ordered from high priority to low priority

    Models can contain multiple geometric contexts. When visualising models,
    you may want to prioritise visualising certain contexts over others,
    determined by the context type, identifier, target view, and target scale.

    The default prioritises subcontexts, then contexts. It then prioritises 3D,
    then 2D. It then prioritises bodies, then others. It also prioritises model
    views, then plan views, then others.

    :param ifc_file: The model containing contexts
    :return: A list of IfcGeometricRepresentationContext (or SubContext) from
        high priority to low priority.
    """
    # Annotation ContextType is to accommodate broken Revit files
    # See https://github.com/Autodesk/revit-ifc/issues/187
    type_priority = ["Model", "Plan", "Annotation"]
    identifier_priority = [
        "Body",
        "Body-FallBack",
        "Facetation",
        "FootPrint",
        "Profile",
        "Surface",
        "Reference",
        "Axis",
        "Clearance",
        "Box",
        "Lighting",
        "Annotation",
        "CoG",
    ]
    target_view_priority = [
        "MODEL_VIEW",
        "PLAN_VIEW",
        "REFLECTED_PLAN_VIEW",
        "ELEVATION_VIEW",
        "SECTION_VIEW",
        "GRAPH_VIEW",
        "SKETCH_VIEW",
        "USERDEFINED",
        "NOTDEFINED",
    ]

    def sort_context(context):
        priority = []
        if context.ContextType in type_priority:
            priority.append(len(type_priority) - type_priority.index(context.ContextType))
        else:
            priority.append(0)
        return tuple(priority)

    def sort_subcontext(context):
        priority = []

        if context.ContextType in type_priority:
            priority.append(len(type_priority) - type_priority.index(context.ContextType))
        else:
            priority.append(0)

        if context.ContextIdentifier in identifier_priority:
            priority.append(len(identifier_priority) - identifier_priority.index(context.ContextIdentifier))
        else:
            priority.append(0)

        if context.TargetView in target_view_priority:
            priority.append(len(target_view_priority) - target_view_priority.index(context.TargetView))
        else:
            priority.append(0)

        priority.append(context.TargetScale or 0)  # Big then small

        return tuple(priority)

    # Ideally, all representations should be in a subcontext, but some BIM programs don't do this correctly
    return sorted(ifc_file.by_type("IfcGeometricRepresentationSubContext"), key=sort_subcontext, reverse=True) + sorted(
        ifc_file.by_type("IfcGeometricRepresentationContext", include_subtypes=False),
        key=sort_context,
        reverse=True,
    )
