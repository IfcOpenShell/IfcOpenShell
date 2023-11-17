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

from __future__ import annotations
import numpy as np
import ifcopenshell
from typing import Any, Union
from dataclasses import dataclass


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


@dataclass
class ClippingInfo:
    location: tuple[float, float, float]
    normal: tuple[float, float, float]
    type: str = "IfcBooleanClippingResult"
    operand_type: str = "IfcHalfSpaceSolid"

    @classmethod
    def parse(cls, raw_data: Any) -> Union[ifcopenshell.entity_instance, ClippingInfo, None]:
        """`raw_data` can be either:
        - IfcBooleanResult IFC entity
        - `ClippingInfo` instance
        - dictionary to define `ClippingInfo` - either `location` and `normal`
            or a `matrix` where XY plane is the clipping boundary and +Z is removed.
            `matrix` method will be soon to be deprecated completely.
        """
        if isinstance(raw_data, ifcopenshell.entity_instance):
            if not raw_data.is_a("IfcBooleanResult"):
                raise Exception(f"Provided clipping of unexpected IFC class: {raw_data}")
            return raw_data
        elif isinstance(raw_data, ClippingInfo):
            return raw_data
        elif isinstance(raw_data, dict):
            if "matrix" in raw_data:
                raw_data = raw_data.copy()
                matrix = np.array(raw_data["matrix"])[:3]
                raw_data["normal"] = matrix[:, 2].tolist()
                raw_data["location"] = matrix[:, 3].tolist()
                del raw_data["matrix"]
            clipping_data = cls(**raw_data)
            if clipping_data.type != "IfcBooleanClippingResult":
                raise Exception(f'Provided clipping with unexpected result type "{clipping_data.type}"')
            if clipping_data.operand_type != "IfcHalfSpaceSolid":
                raise Exception(f'Provided clipping with unexpected operand type "{clipping_data.operand_type}"')
            return clipping_data
        raise Exception(f"Unexpected clipping type provided: {raw_data}")

    def apply(
        self, file: ifcopenshell.file, first_operand: ifcopenshell.entity_instance, unit_scale: float
    ) -> ifcopenshell.entity_instance:
        # TODO: move to a separate method like `shape_builder.add_plane`
        def create_ifc_half_space_solid():
            location = file.createIfcCartesianPoint([i / unit_scale for i in self.location])
            direction = file.createIfcDirection(self.normal)
            axis_placement = file.createIfcAxis2Placement3D(location, direction, None)
            plane = file.createIfcPlane(axis_placement)
            halfspace_solid = file.createIfcHalfSpaceSolid(plane, False)
            return halfspace_solid

        second_operand = create_ifc_half_space_solid()
        first_operand = file.createIfcBooleanClippingResult("DIFFERENCE", first_operand, second_operand)
        return first_operand
