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


from __future__ import annotations
from typing import Any, TypedDict
from dataclasses import dataclass, asdict
import warnings
import ifcopenshell
from ifcopenshell.util.unit import convert_si_to_unit


def get_context(ifc_file, context, subcontext=None, target_view=None):
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


def is_representation_of_context(representation, context, subcontext=None, target_view=None):
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
    elif representation.ContextOfItems.ContextType == context:
        return True


def get_representation(element, context, subcontext=None, target_view=None):
    if element.is_a("IfcProduct") and element.Representation:
        for r in element.Representation.Representations:
            if is_representation_of_context(r, context, subcontext, target_view):
                return r
    elif element.is_a("IfcTypeProduct") and element.RepresentationMaps:
        for r in element.RepresentationMaps:
            if is_representation_of_context(r.MappedRepresentation, context, subcontext, target_view):
                return r.MappedRepresentation


def resolve_representation(representation):
    if len(representation.Items) == 1 and representation.Items[0].is_a("IfcMappedItem"):
        return resolve_representation(representation.Items[0].MappingSource.MappedRepresentation)
    return representation


@dataclass(slots=True)
class ClippingInfo:
    location: tuple[float, float, float]
    normal: tuple[float, float, float]
    result_type: str = "IfcBooleanClippingResult"
    operand_type: str = "IfcHalfSpaceSolid"
    unit_scale: float = 1.

    @classmethod
    def typed_dict(cls) -> type:
        return TypedDict(cls.__name__, **cls.__annotations__)

    def asdict(self) -> ClippingInfo.typed_dict():
        return asdict(self)

    @classmethod
    def parse(cls, raw_data: Any, unit_scale: float) -> ifcopenshell.entity_instance | ClippingInfo | None:
        if isinstance(raw_data, ifcopenshell.entity_instance):
            if not raw_data.is_a("IfcBooleanResult"):
                warnings.warn(f"Ignoring clipping of unexpected IFC class: {raw_data}")
                return
            return raw_data
        elif isinstance(raw_data, ClippingInfo):
            return raw_data
        elif isinstance(raw_data, dict):
            try:
                clipping_data = cls(**raw_data, unit_scale=unit_scale)
            except TypeError:
                warnings.warn(f"Ignoring clipping with unexpected arguments: {raw_data}")
                return
            else:
                if clipping_data.result_type != "IfcBooleanClippingResult":
                    warnings.warn(f"Ignoring clipping with unexpected result type '{clipping_data.result_type}'")
                    return
                if clipping_data.operand_type != "IfcHalfSpaceSolid":
                    warnings.warn(f"Ignoring clipping with unexpected operand type '{clipping_data.operand_type}'")
                    return
                return clipping_data
        else:
            warnings.warn(f"Ignoring clipping of unexpected type: {raw_data}")

    def apply(
            self, file: ifcopenshell.file, first_operand: ifcopenshell.entity_instance
    ) -> ifcopenshell.entity_instance:
        second_operand = file.createIfcHalfSpaceSolid(
            file.createIfcPlane(
                file.createIfcAxis2Placement3D(
                    file.createIfcCartesianPoint([convert_si_to_unit(self, coord) for coord in self.location]),
                    file.createIfcDirection(self.normal),
                    None,
                )
            ),
            False,
        )
        first_operand = file.createIfcBooleanClippingResult("DIFFERENCE", first_operand, second_operand)
        return first_operand

def resolve_items(representation, matrix=None):
    if matrix is None:
        matrix = np.eye(4)
    results = []
    for item in representation.Items or []:  # Be forgiving of invalid IFCs because Revit :(
        if item.is_a("IfcMappedItem"):
            rep_matrix = ifcopenshell.util.placement.get_mappeditem_transformation(item)
            if not np.allclose(rep_matrix, np.eye(4)):
                rep_matrix = rep_matrix @ matrix.copy()
            results.extend(resolve_items(item.MappingSource.MappedRepresentation, rep_matrix))
        else:
            results.append({"matrix": matrix.copy(), "item": item})
    return results
