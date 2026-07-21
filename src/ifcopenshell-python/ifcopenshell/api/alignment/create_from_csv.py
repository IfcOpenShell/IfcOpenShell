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

import csv
from typing import Optional

import ifcopenshell
import ifcopenshell.api.alignment
from ifcopenshell import entity_instance

# number of values per horizontal PI for each supported format
_horizontal_group_sizes = (3, 5, 6)


def _is_number(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def _parse_horizontal_row(data: list[float], group_size: int):
    """
    Parses the horizontal row into PI coordinates, radii (optionally with spiral transition
    lengths), and cants. The curve values of the first and last PI are placeholders and are
    discarded.
    """
    if len(data) % group_size != 0 or len(data) // group_size < 2:
        raise ValueError(
            f"expected the horizontal row to have {group_size} values per PI for at least two PIs, "
            f"instead received {len(data)} values"
        )

    groups = [data[k : k + group_size] for k in range(0, len(data), group_size)]
    coordinates = [(g[0], g[1]) for g in groups]

    cants: Optional[list[float]] = None
    if group_size == 3:
        radii = [g[2] for g in groups[1:-1]]
    elif group_size == 5:
        radii = [(g[2], g[3], g[4]) for g in groups[1:-1]]
    else:
        radii = [(g[2], g[3], g[4]) for g in groups[1:-1]]
        cants = [g[5] for g in groups[1:-1]]

    return coordinates, radii, cants


def _parse_vertical_row(data: list[float]):
    """
    Parses a vertical row into VPI coordinates and vertical curve lengths. The length values of the
    first and last VPI are placeholders and are discarded.
    """
    if len(data) % 3 != 0 or len(data) // 3 < 2:
        raise ValueError(
            f"expected a vertical row to have 3 values per VPI for at least two VPIs, "
            f"instead received {len(data)} values"
        )

    groups = [data[k : k + 3] for k in range(0, len(data), 3)]
    coordinates = [(g[0], g[1]) for g in groups]
    lengths = [g[2] for g in groups[1:-1]]

    return coordinates, lengths


def create_from_csv(file: ifcopenshell.file, filepath: str, rail_head_distance: float = 1.0) -> entity_instance:
    """
    Creates an alignment from PI data stored in a CSV file.

    The format of the file is:

        X1,Y1,R1,X2,Y2,R2 ... Xn,Yn,Rn

        D1,Z1,L1,D2,Z2,L2 ... Dn,Zn,Ln

        D1,Z1,L1,D2,Z2,L2 ... Dn,Zn,Ln

        ...

    where:
        X,Y are PI coordinates

        R is the horizontal circular curve radius

        D,Z are VPI coordinates as "Distance Along","Elevation"

        L is the horizontal length of a parabolic vertical transition curve

        R1 and Rn, as well as L1 and Ln are placeholders and not used. They are recommended to have values of 0.0.

    The CSV file contains one horizontal alignment, zero, one, or more vertical alignments

    Optionally, the file can begin with a header row naming the values that define each horizontal
    PI. The number of header columns sets the format of the horizontal row:

        X,Y,R - PI coordinates and circular curve radius (the default format described above)

        X,Y,R,Lin,Lout - adds clothoid spiral transition curves of length Lin ahead of the circular
        curve and Lout following the circular curve. Use 0.0 for a spiral-less connection.

        X,Y,R,Lin,Lout,E - adds a cant profile. E is the cant of the curve, in the project length
        unit, applied to the rail on the outside of the curve. The cant varies linearly over the
        spiral transition curves, is constant over the circular curve, and is zero on tangent runs.
        Curves with a non-zero cant require non-zero Lin and Lout so the cant profile is continuous.

    As with R, the Lin, Lout, and E values of the first and last PI are placeholders and are
    recommended to have values of 0.0. Vertical rows always have 3 values per VPI. A cant layout is
    created only for the X,Y,R,Lin,Lout,E format, and at least one vertical alignment row is
    required in that case.

    :param filepath: path the to CSV file
    :param rail_head_distance: value assigned to IfcAlignmentCant.RailHeadDistance when a cant layout is created
    :return: IfcAlignment
    """
    alignment = None
    group_size = 3
    include_cant = False
    vertical_count = 0
    with open(filepath, newline="") as csvfile:
        reader = csv.reader(csvfile)
        row_count = 0
        for row in reader:
            if row_count == 0 and len(row) and not _is_number(row[0]):
                # the first row is a header row naming the horizontal PI values
                header = [column for column in row if column.strip()]
                if len(header) not in _horizontal_group_sizes:
                    raise ValueError(
                        f"expected the header row to have {_horizontal_group_sizes} columns, "
                        f"instead received {len(header)} columns"
                    )
                group_size = len(header)
                continue

            data = list(map(float, row))  # Convert all values to float

            row_count += 1

            if row_count == 1:
                coordinates, radii, cants = _parse_horizontal_row(data, group_size)
                include_cant = cants is not None
                if include_cant:
                    # cant requires horizontal, vertical, and cant layouts. the vertical layout is
                    # populated by the first vertical row.
                    alignment = ifcopenshell.api.alignment.create(
                        file,
                        "Alignment_from_CSV",
                        include_vertical=True,
                        include_cant=True,
                        rail_head_distance=rail_head_distance,
                    )
                    cant_layout = ifcopenshell.api.alignment.get_cant_layout(alignment)
                else:
                    alignment = ifcopenshell.api.alignment.create(file, "Alignment_from_CSV")
                    cant_layout = None
                horizontal_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
                ifcopenshell.api.alignment.layout_horizontal_alignment_by_pi_method(
                    file, horizontal_layout, coordinates, radii, cant_layout=cant_layout, cants=cants
                )
            else:
                # add all subsequent vertical alignments
                assert alignment is not None
                coordinates, lengths = _parse_vertical_row(data)
                vertical_count += 1
                if include_cant and vertical_count == 1:
                    # the vertical layout was created along with the cant layout
                    vertical_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
                else:
                    vertical_layout = ifcopenshell.api.alignment.add_vertical_layout(file, alignment)
                ifcopenshell.api.alignment.layout_vertical_alignment_by_pi_method(
                    file, vertical_layout, coordinates, lengths
                )

    if row_count == 0:
        raise ValueError(f"CSV file '{filepath}' is empty; expected at least one row for the horizontal alignment.")

    if include_cant and vertical_count == 0:
        raise ValueError(
            f"CSV file '{filepath}' has a cant profile but no vertical alignment; "
            "at least one vertical alignment row is required with cant."
        )

    assert alignment is not None
    return alignment
