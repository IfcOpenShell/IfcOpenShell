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


def get_parent_alignment(alignment: entity_instance) -> entity_instance:
    """
    Returns the parent alignment. When multiple vertical alignments share a horizontal alignment
    the horizontal alignment is nested to the parent alignment, a child alignment is aggregated
    to the parent alignment for each vertical alignment, and the vertical alignment is nested with
    its child alignment.

    Example:

    .. code:: python
        alignment = model.by_type("IfcAlignment")[0]
        parent = ifcopenshell.api.alignment.get_parent_alignment(alignment)
    """

    for rel in alignment.Decomposes:
        if rel.RelatingObject.is_a("IfcAlignment"):
            return rel.RelatingObject

    return None
