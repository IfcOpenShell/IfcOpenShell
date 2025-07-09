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
import ifcopenshell.api.alignment
import ifcopenshell.api
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment import get_axis_subcontext

from collections.abc import Sequence

import csv


def create_from_csv(file: ifcopenshell.file, filepath: str) -> entity_instance:
    """
    Creates an alignment from PI data stored in a CSV file.

    The format of the file is:

        X1,Y1,R1,X2,Y2,R2 ... Xn-1,Yn-1,Rn-1,Xn,Yn

        D1,Z1,L1,D2,Z2,L2 ... Dn-1,Zn-1,Ln-1,Dn,Zn

        D1,Z1,L1,D2,Z2,L2 ... Dn-1,Zn-1,Ln-1,Dn,Zn

        ...

    where:
        X,Y are PI coordinates

        R is the horizontal circular curve radius

        D,Z are VPI coordinates as "Distance Along","Elevation"

        L is the horizontal length of a parabolic vertical transition curve

        R1 and Rn, as well as L1 and Ln are placeholders and not used. They are recommended to have values of 0.0.

        R2 and Rn-2 are the radii of the first and last horizontal curves.

        L2 and Ln-2 are the length of the first and last vertical curves.

    The CSV file contains one horizontal alignment, zero, one, or more vertical alignments

    :param filepath: path the to CSV file
    :return: IfcAlignment
    """
    with open(filepath, newline="") as csvfile:
        reader = csv.reader(csvfile)
        row_count = 0
        for row in reader:
            data = list(map(float, row))  # Convert all values to float
            coordinates: list[list[float]] = (
                []
            )  # horizontal coordinates for first row, vertical coordinates for subsequent rows
            radii: list[float] = []  # horizontal curve radii for first row, vertical curve length for subsequent rows

            row_count += 1

            i = 0
            while i < len(data):
                if i + 1 < len(data):
                    x, y = float(data[i]), float(data[i + 1])
                    coordinates.append((x, y))  # Store (X, Y) pair
                    i += 2
                if i < len(data) and (i + 1) % 3 == 0:  # Every third element after an (X,Y) pair is R
                    radii.append(data[i])
                    i += 1

            radii = radii[1:-1]  # The first radius value is a placeholder, remove it

            if row_count == 1:
                alignment = ifcopenshell.api.alignment.create(file, "Alignment_from_CSV")
                horizontal_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
                ifcopenshell.api.alignment.layout_horizontal_alignment_by_pi_method(
                    file, horizontal_layout, coordinates, radii
                )
            else:
                # add all subsequent vertical alignments
                vertical_layout = ifcopenshell.api.alignment.add_vertical_layout(file, alignment)
                ifcopenshell.api.alignment.layout_vertical_alignment_by_pi_method(
                    file, vertical_layout, coordinates, radii
                )

    return alignment
