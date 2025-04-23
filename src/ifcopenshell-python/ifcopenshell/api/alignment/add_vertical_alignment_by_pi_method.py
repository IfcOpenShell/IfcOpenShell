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
import ifcopenshell.api.alignment.add_vertical_alignment
from ifcopenshell import entity_instance
from typing import Sequence


def add_vertical_alignment_by_pi_method(
    file: ifcopenshell.file,
    parent_alignment: entity_instance,
    vpoints: Sequence[Sequence[float]],
    lengths: Sequence[float],
) -> None:
    """
    Adds a vertical alignment to a previously created alignment using the PI method.

    If this is the first vertical alignment assigned to the parent_alignment the IFC CT 4.1.4.4.1.1 Alignment Layout - Horizontal, Vertical and Cant
    is followed. If this is the second or subsequent vertical alignment assigned to the parent_alignment the
    IFC CT 4.1.4.4.1.2 Alignment Layout - Reusing Horizontal Layout is followed.

    When the second vertical alignment is added, the structure of the IFC model must transition from one concept template to the other.
    Specifically, the following occurs:

    1) The first child IfcAlignment is created and is IfcRelAggregates with the parent alignment.
    2) The first vertical alignment is unassigned from the IfcRelNests of the parent alignment and assigned to the new child alignment IfcRelNests
    3) A second child IfcAlignment is created and it is IfcRelAggregates with the parent alignment.
    4) An IfcAlignmentVertical is created from vpoints and lengths and it is assigned to the second child alignment

    For the third and subsequent vertical alignments, a new child alignment is created and aggregated to the parent alignment and an IfcAlignmentVertical is created
    from vpoints and lengths and assigned to the new child alignment.

    If the parent_alignment has a geometric representation, a geometric representation will be created for the vertical alignment.

    :param parent_alignment: The parent alignment
    :param vpoints: A sequence of (D,Z) points where D is distance along horizontal and Z is elevation
    :param: lengths: Lengths of parabolic vertical curves occuring at each VPI
    :return: None
    """
    vertical_alignment = ifcopenshell.api.alignment.create_vertical_alignment_by_pi_method(
        file, parent_alignment.Name, vpoints, lengths
    )
    ifcopenshell.api.alignment.add_vertical_alignment(file, parent_alignment, vertical_alignment)
