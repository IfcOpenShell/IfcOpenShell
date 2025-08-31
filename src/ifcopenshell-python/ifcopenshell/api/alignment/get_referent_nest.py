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


def get_referent_nest(file: ifcopenshell.file, alignment: entity_instance) -> entity_instance:
    """
    Searches for the IfcRelNest that contains IfcReferent. If one is not found, a empty IfcRelNests is created.

    :param file:
    :param alignment: The IfcAlignment which hosts IfcReferent
    :return: Returns the IfcRelNests.
    """
    if not alignment.is_a("IfcAlignment"):
        raise TypeError(f"Expected IfcAlignment, instead received {alignment.is_a()}")

    for nest in alignment.IsNestedBy:
        for related_object in nest.RelatedObjects:
            if related_object.is_a("IfcReferent"):
                return nest

    nest = file.createIfcRelNests(GlobalId=ifcopenshell.guid.new(), RelatingObject=alignment, RelatedObjects=[])
    return nest
