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

    patched_file = ifcopenshell.file.from_string(file.wrapped_data.to_string())

    linear_placements = patched_file.by_type("IfcLinearPlacement")
    for lp in linear_placements:
        ifcopenshell.api.alignment.update_fallback_position(patched_file, lp)

    return patched_file


def create_alignment_geometry(file: ifcopenshell.file) -> ifcopenshell.file:
    import ifcopenshell.api.alignment

    patched_file = ifcopenshell.file.from_string(file.wrapped_data.to_string())

    alignments = patched_file.by_type("IfcAlignment")
    for alignment in alignments:
        ifcopenshell.api.alignment.create_representation(patched_file, alignment)

    return patched_file


def append_zero_length_segments(file: ifcopenshell.file) -> ifcopenshell.file:
    """Appends zero length segments to all alignment layouts and layout geometry, if missing."""
    import ifcopenshell.api.alignment

    patched_file = ifcopenshell.file.from_string(file.wrapped_data.to_string())

    alignments = patched_file.by_type("IfcAlignment")
    for alignment in alignments:
        layouts = ifcopenshell.api.alignment.get_alignment_layouts(alignment)
        for layout in layouts:
            ifcopenshell.api.alignment.add_zero_length_segment(patched_file, layout, include_referent=False)
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
    if unit_type.is_a("IfcConversionBasedUnit"):
        station = ifcopenshell.util.unit.convert(
            sta, from_unit=unit_type.Name, from_prefix=None, to_unit="foot", to_prefix=None
        )
        plus_seperator = 2
        precision = 2
    else:
        station = ifcopenshell.util.unit.convert(
            sta, from_unit=unit_type.Name, from_prefix=unit_type.Prefix, to_unit="meter", to_prefix=None
        )
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
