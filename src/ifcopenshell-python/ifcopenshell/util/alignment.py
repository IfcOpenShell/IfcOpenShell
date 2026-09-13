# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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

import math

import ifcopenshell
import ifcopenshell.util.unit


def add_linear_placement_fallback_position(file: ifcopenshell.file) -> ifcopenshell.file:
    import ifcopenshell.api.alignment

    patched_file = ifcopenshell.file.from_string(file.to_string())

    linear_placements = patched_file.by_type("IfcLinearPlacement")
    for lp in linear_placements:
        ifcopenshell.api.alignment.update_fallback_position(patched_file, lp)

    return patched_file


def create_alignment_geometry(file: ifcopenshell.file) -> ifcopenshell.file:
    import ifcopenshell.api.alignment

    patched_file = ifcopenshell.file.from_string(file.to_string())

    alignments = patched_file.by_type("IfcAlignment")
    for alignment in alignments:
        ifcopenshell.api.alignment.create_representation(patched_file, alignment)

    return patched_file


def append_zero_length_segments(file: ifcopenshell.file) -> ifcopenshell.file:
    """Appends zero length segments to all alignment layouts and layout geometry, if missing."""
    import ifcopenshell.api.alignment

    patched_file = ifcopenshell.file.from_string(file.to_string())

    alignments = patched_file.by_type("IfcAlignment")
    for alignment in alignments:
        layouts = ifcopenshell.api.alignment.get_alignment_layouts(alignment)
        for layout in layouts:
            ifcopenshell.api.alignment.add_zero_length_segment(patched_file, layout)
            curve = ifcopenshell.api.alignment.get_layout_curve(layout)
            if curve:
                ifcopenshell.api.alignment.add_zero_length_segment(patched_file, curve)

    return patched_file


def station_as_string(file: ifcopenshell.file, sta: float):
    """
    Returns a stringized version of a station. Example 100.0 is 1+00.00 as a stationing string.
    If the project units are SI-based, the string is in the format xxx+yyy.zzz
    If the project units are Emperial-based, the string is in the format xx+yy.zz

    :param station: the station to be stringized
    :return: stringized station
    """

    unit_type = ifcopenshell.util.unit.get_project_unit(file, "LENGTHUNIT")
    project_unit_to_metres = ifcopenshell.util.unit.calculate_unit_scale(file)
    if unit_type.is_a("IfcConversionBasedUnit"):
        # xx+yy.zz display is inherently foot-based, regardless of which foot variant
        # (international vs. US survey, etc.) the project's own unit actually is.
        station = sta * project_unit_to_metres / 0.3048
        plus_seperator = 2
        precision = 2
    else:
        station = sta * project_unit_to_metres
        plus_seperator = 3
        precision = 3

    value = math.fabs(station)

    shifter = math.pow(10.0, plus_seperator)
    v1 = math.floor(value / shifter)
    v2 = value - v1 * shifter

    # Check to make sure that v2 is not basically the same as shifter
    # If station = 69500.00000, we sometimes get 694+100.00 instead of 695+00.00
    if math.isclose(v2 - shifter, 0.0, abs_tol=5.0 * math.pow(10.0, -(precision + 1))):
        v2 = 0.0
        v1 += 1

    v1 = -1 * v1 if station < 0 else v1

    station_string = "{:d}+{:0{}.{}f}".format(v1, v2, plus_seperator + precision + 1, precision)

    # special case when v1 is 0 and station is negative, the string above doesn't get the leading
    # negative sign. this snippet fixes that
    if v1 == 0 and station < 0:
        station_string = "-" + station_string

    return station_string


def station_from_string(file: ifcopenshell.file, s: str) -> float:
    """
    Parses a station value typed by a user, in either of two forms:

    - A plain real number, e.g. "1000" or "1000.5" -- taken literally as the
      station value, in project units.
    - Stationing notation "V1+V2", the inverse of :func:`station_as_string`,
      e.g. "10+00" (a project with Imperial units) or "1+000" (a project
      with SI units). V1 is worth 100 display-feet (Imperial) or 1000
      display-metres (SI) -- matching station_as_string()'s plus-separator
      placement -- and V2 is added to that, before converting the result
      from the format's display unit (foot for Imperial, metre for SI) back
      to the file's actual project length unit.

    :param file: the IFC file, used to resolve the project's LENGTHUNIT
    :param s: the station string to parse
    :return: the station, in project units
    :raises ValueError: if ``s`` is neither a plain number nor valid
        stationing notation
    """
    s = s.strip()
    if not s:
        raise ValueError("Station value is empty")

    if "+" not in s:
        return float(s)

    is_negative = s.startswith("-")
    body = s[1:] if is_negative else s
    left, separator, right = body.partition("+")
    if not separator or not left.strip() or not right.strip():
        raise ValueError(f"Invalid stationing notation: {s!r}")

    v1 = float(left)
    v2 = float(right)

    unit_type = ifcopenshell.util.unit.get_project_unit(file, "LENGTHUNIT")
    project_unit_to_metres = ifcopenshell.util.unit.calculate_unit_scale(file)
    if unit_type is not None and unit_type.is_a("IfcConversionBasedUnit"):
        # Imperial: display value is in feet, plus-separator is worth 100.
        shifter = 100.0
        metres_per_display_unit = 0.3048
    else:
        # SI: display value is in metres, plus-separator is worth 1000.
        shifter = 1000.0
        metres_per_display_unit = 1.0

    display_value = v1 * shifter + v2
    if is_negative:
        display_value = -display_value

    return display_value * metres_per_display_unit / project_unit_to_metres
