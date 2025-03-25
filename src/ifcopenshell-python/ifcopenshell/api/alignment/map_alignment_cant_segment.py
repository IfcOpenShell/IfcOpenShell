# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Thomas Krijnen <thomas@aecgeeks.com>
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
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment import get_axis_subcontext
from typing import Sequence


def _map_constant_cant(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    raise NotImplementedError("CONSTANTCANT not implemented")


def _map_linear_transition(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    raise NotImplementedError("LINEARTRANSTION not implemented")


def _map_helmert_curve(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    raise NotImplementedError("HELMERTCURVE not implemented")


def _map_bloss_curve(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    raise NotImplementedError("BLOSSCURVE not implemented")


def _map_cosine_curve(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    raise NotImplementedError("COSINECURVE not implemented")


def _map_sine_curve(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    raise NotImplementedError("SINECURVE not implemented")


def _map_viennese_bend(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    raise NotImplementedError("VIENNESEBEND not implemented")


def map_alignment_cant_segment(
    file: ifcopenshell.file, design_parameters: entity_instance
) -> Sequence[entity_instance]:
    """
    Creates IfcCurveSegment entities for the represention of the supplied IfcAlignmentCantSegment business logic entity instance.
    A pair of entities is returned because a single business logic segment of type HELMERTCURVE maps to two representaiton entities.

    The IfcCurveSegment.Transition transition code is set to DISCONTINUOUS.
    """
    expected_type = "IfcAlignmentCantSegment"
    if not design_parameters.is_a(expected_type):
        raise TypeError(f"Expected to see type '{expected_type}', instead received '{design_parameters.is_a()}'.")

    match design_parameters.PredefinedType:
        case "CONSTANTCANT":
            result = _map_constant_cant(file, design_parameters)
        case "LINEARTRANSITION":
            result = _map_linear_transition(file, design_parameters)
        case "HELMERTCURVE":
            result = _map_helmert_curve(file, design_parameters)
        case "BLOSSCURVE":
            result = _map_bloss_curve(file, design_parameters)
        case "COSINECURVE":
            result = _map_cosine_curve(file, design_parameters)
        case "SINECURVE":
            result = _map_sine_curve(file, design_parameters)
        case "VIENNESEBEND":
            result = _map_viennese_bend(file, design_parameters)
        case _:
            raise TypeError("Unexpected predefined type")

    return result
