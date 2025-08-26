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
from collections.abc import Sequence

import ifcopenshell.util.element


def get_child_alignments(alignment: entity_instance) -> Sequence[entity_instance]:
    """
    Returns the aggregated child alignments to this alignment per CT 4.1.4.4.1.2 Alignment Layout - Reusing Horizontal Layout

    Example:

    .. code:: python

        alignment = model.by_type("IfcAlignment")[0]
        children = ifcopenshell.api.alignment.get_child_alignments(alignment)
    """
    children = []
    for rel in alignment.IsDecomposedBy:
        for child in rel.RelatedObjects:
            if child.is_a("IfcAlignment"):
                children.append(child)

    return children
