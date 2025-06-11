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
import ifcopenshell.util.representation
import ifcopenshell.util.placement
import ifcopenshell.util.shape
from typing import Optional, Union, TypedDict, Literal
from collections.abc import Generator, Sequence


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


def get_representations_iter(
    element: ifcopenshell.entity_instance,
) -> Generator[ifcopenshell.entity_instance, None, None]:
    """Get an iterator with element's IfcShapeRepresentations.

    :param element: An IfcProduct or IfcTypeProduct
    """
    if element.is_a("IfcProduct") and (rep := element.Representation):
        for r in rep.Representations:
            yield r
    elif element.is_a("IfcTypeProduct") and (maps := element.RepresentationMaps):
        for r in maps:
            yield r.MappedRepresentation


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
    for r in get_representations_iter(element):
        if is_representation_of_context(r, context, subcontext, target_view):
            return r


def guess_type(items: Sequence[ifcopenshell.entity_instance]) -> Union[str, None]:
    """Guesses the appropriate RepresentationType attribute based on a list of items

    :param items: A list of IfcRepresentationItem, typically in an IfcShapeRepresentation
    :return: The appropriate RepresentationType value, or None if no valid value
    """
    if all([True if i.is_a("IfcMappedItem") else False for i in items]):
        return "MappedRepresentation"
    elif all([True if i.is_a("IfcPoint") or i.is_a("IfcCartesianPointList") else False for i in items]):
        return "Point"
    elif all([True if i.is_a("IfcCartesianPointList3d") else False for i in items]):
        return "PointCloud"
    elif all([True if i.is_a("IfcCurve") and i.Dim == 2 else False for i in items]):
        return "Curve2D"
    elif all([True if i.is_a("IfcCurve") and i.Dim == 3 else False for i in items]):
        return "Curve3D"
    elif all([True if i.is_a("IfcCurve") else False for i in items]):
        return "Curve"
    elif all([True if i.is_a("IfcSegment") else False for i in items]):
        return "Segment"
    elif all([True if i.is_a("IfcSurface") and i.Dim == 2 else False for i in items]):
        return "Surface2D"
    elif all([True if i.is_a("IfcSurface") and i.Dim == 3 else False for i in items]):
        return "Surface3D"
    elif all([True if i.is_a("IfcSurface") else False for i in items]):
        return "Surface"
    elif all([True if i.is_a("IfcSectionedSurface") else False for i in items]):
        return "SectionedSurface"
    elif all([True if i.is_a("IfcAnnotationFillArea") else False for i in items]):
        return "FillArea"
    elif all([True if i.is_a("IfcTextLiteral") else False for i in items]):
        return "Text"
    elif all([True if i.is_a("IfcBSplineSurface") else False for i in items]):
        return "AdvancedSurface"
    elif all(
        [
            (
                True
                if i.is_a("IfcGeometricSet") or i.is_a("IfcPoint") or i.is_a("IfcCurve") or i.is_a("IfcSurface")
                else False
            )
            for i in items
        ]
    ):
        return "GeometricSet"
    elif all(
        [
            (
                True
                if i.is_a("IfcGeometricCurveSet")
                or (i.is_a("IfcGeometricSet") and all([e.is_a("IfcSurface") for e in i.Elements]))
                or i.is_a("IfcPoint")
                or i.is_a("IfcCurve")
                else False
            )
            for i in items
        ]
    ):
        return "GeometricCurveSet"
    elif all(
        [
            (
                True
                if i.is_a("IfcPoint")
                or i.is_a("IfcCurve")
                or i.is_a("IfcGeometricCurveSet")
                or i.is_a("IfcAnnotationFillArea")
                or i.is_a("IfcTextLiteral")
                else False
            )
            for i in items
        ]
    ):
        return "Annotation2D"
    elif all([True if i.is_a("IfcTessellatedItem") else False for i in items]):
        return "Tessellation"
    elif all(
        [
            (
                True
                if i.is_a("IfcTessellatedItem")
                or i.is_a("IfcShellBasedSurfaceModel")
                or i.is_a("IfcFaceBasedSurfaceModel")
                else False
            )
            for i in items
        ]
    ):
        return "SurfaceModel"
    elif all(
        [True if i.is_a() == "IfcExtrudedAreaSolid" or i.is_a() == "IfcRevolvedAreaSolid" else False for i in items]
    ):
        return "SweptSolid"
    elif all([True if i.is_a("IfcSolidModel") else False for i in items]):
        return "SolidModel"
    elif all(
        [
            (
                True
                if i.is_a("IfcTessellatedItem")
                or i.is_a("IfcShellBasedSurfaceModel")
                or i.is_a("IfcFaceBasedSurfaceModel")
                or i.is_a("IfcSolidModel")
                else False
            )
            for i in items
        ]
    ):
        return "SurfaceOrSolidModel"
    elif all(
        [
            (
                True
                if i.is_a("IfcSweptAreaSolid") or i.is_a("IfcSweptDiskSolid") or i.is_a("IfcSectionedSolidHorizontal")
                else False
            )
            for i in items
        ]
    ):
        return "AdvancedSweptSolid"
    elif all([True if i.is_a("IfcCsgSolid") or i.is_a("IfcBooleanClippingResult") else False for i in items]):
        return "Clipping"
    elif all(
        [
            True if i.is_a("IfcBooleanResult") or i.is_a("IfcCsgPrimitive3d") or i.is_a("IfcCsgSolid") else False
            for i in items
        ]
    ):
        return "CSG"
    elif all([True if i.is_a("IfcFacetedBrep") else False for i in items]):
        return "Brep"
    elif all([True if i.is_a("IfcManifoldSolidBrep") else False for i in items]):
        return "AdvancedBrep"
    elif all([True if i.is_a("IfcBoundingBox") else False for i in items]):
        return "BoundingBox"
    elif all([True if i.is_a("IfcSectionedSpine") else False for i in items]):
        return "SectionedSpine"
    elif all([True if i.is_a("IfcLightSource") else False for i in items]):
        return "LightSource"
    elif all([True if i.is_a("IfcVertex") else False for i in items]):
        return "Vertex"
    elif all([True if i.is_a("IfcEdge") else False for i in items]):
        return "Edge"
    elif all([True if i.is_a("IfcPath") else False for i in items]):
        return "Path"
    elif all([True if i.is_a("IfcFace") else False for i in items]):
        return "Face"
    elif all([True if i.is_a("IfcOpenShell") else False for i in items]):
        return "Shell"


def resolve_representation(representation: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """Resolve possibly mapped representation.

    :param representation: IfcRepresentation
    :return: Representation resolved from mappings
    """
    # Tekla 2023 has missing items and mapped representation, though it's invalid IFC.
    if (
        len(representation.Items or []) == 1
        and representation.Items[0].is_a("IfcMappedItem")
        and (mapped_rep := representation.Items[0].MappingSource.MappedRepresentation)
    ):
        return resolve_representation(mapped_rep)
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


def resolve_base_items(
    representation: ifcopenshell.entity_instance,
) -> Generator[ifcopenshell.entity_instance, None, None]:
    """Resolve representation to it's base items resolving mapped items and boolean results to it's operands."""
    queue: list[ifcopenshell.entity_instance] = list(representation.Items)
    while queue:
        item = queue.pop()
        if item.is_a("IfcMappedItem"):
            yield from resolve_base_items(item.MappingSource.MappedRepresentation)
        elif item.is_a("IfcBooleanResult"):
            queue.append(item.FirstOperand)
            queue.append(item.SecondOperand)
        else:
            yield item


def get_prioritised_contexts(ifc_file: ifcopenshell.file) -> list[ifcopenshell.entity_instance]:
    """Gets a list of contexts ordered from high priority to low priority

    Models can contain multiple geometric contexts. When visualising models,
    you may want to prioritise visualising certain contexts over others,
    determined by the context type, identifier, target view, and target scale.

    The default prioritises 3D, then 2D. It then prioritises subcontexts, then
    contexts. It then prioritises bodies, then others. It also prioritises
    model views, then plan views, then others.

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

        if context.ContextIdentifier in identifier_priority:
            priority.append(len(identifier_priority) - identifier_priority.index(context.ContextIdentifier))
        else:
            priority.append(0)

        if getattr(context, "TargetView", None) in target_view_priority:
            priority.append(len(target_view_priority) - target_view_priority.index(context.TargetView))
        else:
            priority.append(0)

        priority.append(getattr(context, "TargetScale", None) or 0)  # Big then small

        return tuple(priority)

    return sorted(ifc_file.by_type("IfcGeometricRepresentationContext"), key=sort_context, reverse=True)


def get_part_of_product(
    element: ifcopenshell.entity_instance, context: ifcopenshell.entity_instance
) -> Union[ifcopenshell.entity_instance, None]:
    """Gets the product definition or representation map of an element

    This is typically used for setting shape aspects. Note that this will
    return None for IFC2X3 element types.

    :param element: An IfcProduct or IfcTypeProduct
    :param context: A IfcGeometricRepresentationContext
    :return: IfcProductRepresentationSelect
    """
    if element.is_a("IfcProduct"):
        return element.Representation
    elif element.is_a("IfcTypeProduct") and element.file.schema != "IFX2X3":
        if maps := [r for r in element.RepresentationMaps if r.MappedRepresentation.ContextOfItems == context]:
            return maps[0]


def get_item_shape_aspect(
    representation: ifcopenshell.entity_instance, item: ifcopenshell.entity_instance
) -> Union[ifcopenshell.entity_instance, None]:
    """Gets the shape aspect relating to an item

    :param representation: The IfcShapeRepresentation that the item is part of
    :param item: The IfcRepresentationItem you want to get the shape aspect of
    :return: IfcShapeAspect, or None if none exists
    """
    for inverse in item.file.get_inverse(item):
        if (
            inverse.is_a("IfcShapeRepresentation")
            and inverse.ContextOfItems == representation.ContextOfItems
            and (of_shape_aspect := inverse.OfShapeAspect)
        ):
            return of_shape_aspect[0]


def get_material_style(
    material: ifcopenshell.entity_instance, context: ifcopenshell.entity_instance, ifc_class: str = "IfcSurfaceStyle"
) -> Union[ifcopenshell.entity_instance, None]:
    """Get a presentation style associated with a material

    :param material: the IfcMaterial
    :param context: IfcGeometricRepresentationContext that the style belongs to
    :param ifc_class: The class name of the type of style you need, typically
        IfcSurfaceStyle for 3D styling.
    :return: IfcPresentationStyle
    """
    if definition_representation := material.HasRepresentation:
        for styled_rep in definition_representation[0].Representations:
            if styled_rep.ContextOfItems == context:
                for item in styled_rep.Items:
                    for style in item.Styles:
                        if style.is_a(ifc_class):
                            return style


def get_reference_line(wall: ifcopenshell.entity_instance, fallback_length: float = 1.0) -> list[npt.NDArray]:
    """Fetch the reference axis that goes in the +X direction

    A base line will then be offset from this reference line based on the
    material usage. From that base line, the layer thicknesses will offset
    again, and be extruded to form the body representation.

    :param wall: ifcopenshell.entity_instance
    :param fallback_length: If there is no reference axis, assume it starts at
        the object placement (i.e. 0.0, 0.0) and extends for this fallback
        length along the +X axis.
    :return: A list of two 2D coordinates representing the start and end of the
        axis. The axis always goes in the +X direction.
    """
    if axis := ifcopenshell.util.representation.get_representation(wall, "Plan", "Axis", "GRAPH_VIEW"):
        for item in ifcopenshell.util.representation.resolve_representation(axis).Items:
            if item.is_a("IfcPolyline"):
                points = [p[0] for p in item.Points]
            elif item.is_a("IfcIndexedPolyCurve"):
                points = item.Points.CoordList
            else:
                continue
            if points[0][0] < points[1][0]:  # An axis always goes in the +X direction
                return [np.array(points[0]), np.array(points[1])]
            return [np.array(points[1]), np.array(points[0])]
    elif extrusions := ifcopenshell.util.shape.get_base_extrusions(wall):
        for extrusion in extrusions:
            profile = extrusion.SweptArea
            curve = getattr(profile, "OuterCurve", None)
            if not curve:
                continue
            elif curve.is_a("IfcPolyline"):
                x = [p[0][0] for p in curve.Points]
            elif curve.is_a("IfcIndexedPolyCurve"):
                x = [p[0] for p in curve.Points.CoordList]
            else:
                continue
            return [np.array((min(x), 0.0)), np.array((max(x), 0.0))]
    return [np.array((0.0, 0.0)), np.array((fallback_length, 0.0))]
