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
import ifcopenshell.util
from ifcopenshell import entity_instance
from typing import Sequence

import ifcopenshell.util.representation


def __get_segment_start_point_label(prev_segment: entity_instance, segment: entity_instance) -> str:
    """
    Returns the label for the start point of a segment. Typically used in the name of an IfcReferent
    """
    if prev_segment != None and segment != None and prev_segment.is_a() != segment.is_a():
        raise TypeError(
            f"Expected entity type to be the same type, instead received {prev_segment.is_a()} and {segment.is_a()}"
        )

    expected_types = ["IfcAlignmentHorizontalSegment", "IfcAlignmentVerticalSegment", "IfcAlignmentCantSegment"]
    if prev_segment != None and not prev_segment.DesignParameters.is_a() in expected_types:
        raise TypeError(
            f"Expected prev_segment.DesignParameters type to be one of {[_ for _ in expected_types]}, instead received {prev_segment.DesignParameters.is_a()}"
        )
    if segment != None and not segment.DesignParameters.is_a() in expected_types:
        raise TypeError(
            f"Expected segment.DesignParameters type to be one of {[_ for _ in expected_types]}, instead received {segment.DesignParameters.is_a()}"
        )

    label = "Unknown"
    if prev_segment == None and segment != None:
        if segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment"):
            label = "P.O.B."
        elif segment.DesignParameters.is_a("IfcAlignmentVerticalSegment"):
            label = "V.P.O.B."
        elif segment.DesignParameters.is_a("IfcAlignmentCantSegment"):
            label = "C.P.O.B."
    elif prev_segment != None and segment == None:
        if prev_segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment"):
            label = "P.O.E."
        elif prev_segment.DesignParameters.is_a("IfcAlignmentVerticalSegment"):
            label = "V.P.O.E."
        elif prev_segment.DesignParameters.is_a("IfcAlignmentCantSegment"):
            label = "C.P.O.E."
    else:
        if segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment"):
            lookup_table = {
                "BLOSSCURVE": {
                    "BLOSSCURVE": "xx",
                    "CIRCULARARC": "S.C.",
                    "CLOTHOID": "xx",
                    "COSINECURVE": "xx",
                    "CUBIC": "xx",
                    "HELMERTCURVE": "xx",
                    "LINE": "S.T.",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
                "CIRCULARARC": {
                    "BLOSSCURVE": "C.S.",
                    "CIRCULARARC": "C.C",
                    "CLOTHOID": "xx",
                    "COSINECURVE": "xx",
                    "CUBIC": "xx",
                    "HELMERTCURVE": "xx",
                    "LINE": "P.T.",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
                "CLOTHOID": {
                    "BLOSSCURVE": "xx",
                    "CIRCULARARC": "S.C.",
                    "CLOTHOID": "xx",
                    "COSINECURVE": "xx",
                    "CUBIC": "xx",
                    "HELMERTCURVE": "xx",
                    "LINE": "S.T.",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
                "COSINECURVE": {
                    "BLOSSCURVE": "xx",
                    "CIRCULARARC": "S.C.",
                    "CLOTHOID": "xx",
                    "COSINECURVE": "xx",
                    "CUBIC": "xx",
                    "HELMERTCURVE": "xx",
                    "LINE": "S.T.",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
                "CUBIC": {
                    "BLOSSCURVE": "xx",
                    "CIRCULARARC": "S.C.",
                    "CLOTHOID": "xx",
                    "COSINECURVE": "xx",
                    "CUBIC": "xx",
                    "HELMERTCURVE": "xx",
                    "LINE": "S.T.",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
                "HELMERTCURVE": {
                    "BLOSSCURVE": "xx",
                    "CIRCULARARC": "S.C.",
                    "CLOTHOID": "xx",
                    "COSINECURVE": "xx",
                    "CUBIC": "xx",
                    "HELMERTCURVE": "xx",
                    "LINE": "S.T.",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
                "LINE": {
                    "BLOSSCURVE": "T.S.",
                    "CIRCULARARC": "P.C.",
                    "CLOTHOID": "T.S.",
                    "COSINECURVE": "T.S.",
                    "CUBIC": "T.S.",
                    "HELMERTCURVE": "T.S.",
                    "LINE": "P.I.",
                    "SINECURVE": "T.S.",
                    "VIENNESEBEND": "T.S.",
                },
                "SINECURVE": {
                    "BLOSSCURVE": "xx",
                    "CIRCULARARC": "S.C.",
                    "CLOTHOID": "xx",
                    "COSINECURVE": "xx",
                    "CUBIC": "xx",
                    "HELMERTCURVE": "xx",
                    "LINE": "S.T.",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
                "VIENNESEBEND": {
                    "BLOSSCURVE": "xx",
                    "CIRCULARARC": "S.C.",
                    "CLOTHOID": "xx",
                    "COSINECURVE": "xx",
                    "CUBIC": "xx",
                    "HELMERTCURVE": "xx",
                    "LINE": "S.T.",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
            }
            label = lookup_table[prev_segment.DesignParameters.PredefinedType][segment.DesignParameters.PredefinedType]
        elif segment.DesignParameters.is_a("IfcAlignmentVerticalSegment"):
            lookup_table = {
                "CIRCULARARC": {"CIRCULARARC": "xx", "CLOTHOID": "xx", "CONSTANTGRADIENT": "xx", "PARABOLICARC": "xx"},
                "CLOTHOID": {"CIRCULARARC": "xx", "CLOTHOID": "xx", "CONSTANTGRADIENT": "xx", "PARABOLICARC": "xx"},
                "CONSTANTGRADIENT": {
                    "CIRCULARARC": "xx",
                    "CLOTHOID": "xx",
                    "CONSTANTGRADIENT": "P.V.I",
                    "PARABOLICARC": "B.V.C.",
                },
                "PARABOLICARC": {
                    "CIRCULARARC": "xx",
                    "CLOTHOID": "xx",
                    "CONSTANTGRADIENT": "E.V.C.",
                    "PARABOLICARC": "xx",
                },
            }
            label = lookup_table[prev_segment.DesignParameters.PredefinedType][segment.DesignParameters.PredefinedType]
        elif segment.DesignParameters.is_a("IfcAlignmentCantSegment"):
            lookup_table = {
                "BLOSSCURVE": {
                    "BLOSSCURVE": "xx",
                    "CONSTANTCANT": "xx",
                    "COSINECURVE": "xx",
                    "HELMERTCURVE": "xx",
                    "LINEARTRANSITION": "xx",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
                "CONSTANTCANT": {
                    "BLOSSCURVE": "xx",
                    "CONSTANTCANT": "xx",
                    "COSINECURVE": "xx",
                    "HELMERTCURVE": "xx",
                    "LINEARTRANSITION": "xx",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
                "COSINECURVE": {
                    "BLOSSCURVE": "xx",
                    "CONSTANTCANT": "xx",
                    "COSINECURVE": "xx",
                    "HELMERTCURVE": "xx",
                    "LINEARTRANSITION": "xx",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
                "HELMERTCURVE": {
                    "BLOSSCURVE": "xx",
                    "CONSTANTCANT": "xx",
                    "COSINECURVE": "xx",
                    "HELMERTCURVE": "xx",
                    "LINEARTRANSITION": "xx",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
                "LINEARTRANSITION": {
                    "BLOSSCURVE": "xx",
                    "CONSTANTCANT": "xx",
                    "COSINECURVE": "xx",
                    "HELMERTCURVE": "xx",
                    "LINEARTRANSITION": "xx",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
                "SINECURVE": {
                    "BLOSSCURVE": "xx",
                    "CONSTANTCANT": "xx",
                    "COSINECURVE": "xx",
                    "HELMERTCURVE": "xx",
                    "LINEARTRANSITION": "xx",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
                "VIENNESEBEND": {
                    "BLOSSCURVE": "xx",
                    "CONSTANTCANT": "xx",
                    "COSINECURVE": "xx",
                    "HELMERTCURVE": "xx",
                    "LINEARTRANSITION": "xx",
                    "SINECURVE": "xx",
                    "VIENNESEBEND": "xx",
                },
            }
            label = lookup_table[prev_segment.DesignParameters.PredefinedType][segment.DesignParameters.PredefinedType]

    return label
