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
from collections.abc import Sequence


_horizontal_callback = None
_vertical_callback = None
_cant_callback = None


def register_referent_name_callback(horizontal=None, vertical=None, cant=None):
    """
    Referents are automatically created at the start of each horizontal, vertical, and cant segment.
    The referents represent key points in the alignment layout such as Point of Curvature, Point of Tangent, and others.
    Different juristicions use different naming systems for these key points.

    The referent name callback functions provide a customizable method for naming these referents. If a callback is registered,
    it is called when creating the referent name, otherwise the default naming is used.

    The callback function signature is

        def mycallback(prev_segment : entity_instance, segment : entity_instance) -> str:

    The callback function returns a string that is used in the referent name for the referent at the start of `segment`.
    The callback must accomodate the following cases:
    * prev_segment = None and segment != None - this indicates the last segment so the "End of Alignment" name is returned
    * prev_segment != None and segment == None - this indicates the first segment so the "Beginning of Alignment" name is returned
    * prev_segment != None and segment != None - this indicates an intermediate segment so a name representitive of the transition is returned

    Setting any or all of the callbacks to None causes the default naming to be used.
    """
    global _horizontal_callback
    _horizontal_callback = horizontal

    global _vertical_callback
    _vertical_callback = vertical

    global _cant_callback
    _cant_callback = cant


def _horizontal_label(prev_segment: entity_instance, segment: entity_instance) -> str:
    if prev_segment == None and segment != None:
        label = "P.O.B."
    elif prev_segment != None and segment == None:
        label = "P.O.E."
    else:
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
                "CIRCULARARC": "P.C.C.",
                "CLOTHOID": "C.S.",
                "COSINECURVE": "C.S.",
                "CUBIC": "C.S.",
                "HELMERTCURVE": "C.S.",
                "LINE": "P.T.",
                "SINECURVE": "C.S.",
                "VIENNESEBEND": "C.S.",
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

    return label


def _vertical_label(prev_segment: entity_instance, segment: entity_instance) -> str:
    if prev_segment == None and segment != None:
        label = "V.P.O.B."
    elif prev_segment != None and segment == None:
        label = "V.P.O.E."
    else:
        lookup_table = {
            "CIRCULARARC": {"CIRCULARARC": "xx", "CLOTHOID": "xx", "CONSTANTGRADIENT": "xx", "PARABOLICARC": "xx"},
            "CLOTHOID": {"CIRCULARARC": "xx", "CLOTHOID": "xx", "CONSTANTGRADIENT": "xx", "PARABOLICARC": "xx"},
            "CONSTANTGRADIENT": {
                "CIRCULARARC": "xx",
                "CLOTHOID": "xx",
                "CONSTANTGRADIENT": "P.V.I",
                "PARABOLICARC": "P.V.C.",
            },
            "PARABOLICARC": {
                "CIRCULARARC": "xx",
                "CLOTHOID": "xx",
                "CONSTANTGRADIENT": "P.V.T.",
                "PARABOLICARC": "V.C.C.",
            },
        }
        label = lookup_table[prev_segment.DesignParameters.PredefinedType][segment.DesignParameters.PredefinedType]

    return label


def _cant_label(prev_segment: entity_instance, segment: entity_instance) -> str:
    if prev_segment == None and segment != None:
        label = "C.P.O.B."
    elif prev_segment != None and segment == None:
        label = "C.P.O.E."
    else:
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


def _get_segment_start_point_label(prev_segment: entity_instance, segment: entity_instance) -> str:
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

    s = segment if segment != None else prev_segment
    if s.DesignParameters.is_a("IfcAlignmentHorizontalSegment"):
        global _horizontal_callback
        if _horizontal_callback:
            label = _horizontal_callback(prev_segment, segment)
        else:
            label = _horizontal_label(prev_segment, segment)
    elif s.DesignParameters.is_a("IfcAlignmentVerticalSegment"):
        global _vertical_callback
        if _vertical_callback:
            label = _vertical_callback(prev_segment, segment)
        else:
            label = _vertical_label(prev_segment, segment)
    elif s.DesignParameters.is_a("IfcAlignmentCantSegment"):
        global _cant_callback
        if _cant_callback:
            label = _cant_callback(prev_segment, segment)
        else:
            label = _cant_label(prev_segment, segment)

    return label
