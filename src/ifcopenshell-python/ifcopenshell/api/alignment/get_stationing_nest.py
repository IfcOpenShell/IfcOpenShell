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


def get_stationing_nest(file: ifcopenshell.file, alignment: entity_instance) -> entity_instance:
    """
    Searches for the IfcRelNests that defines the alignment's stationing scheme.

    The returned nest is nested to the IfcAlignment and its RelatedObjects contains only the
    IfcReferent(s) (PredefinedType="STATION") that establish the alignment's starting station and
    any station equations along it, as created by add_stationing_referent. It does not contain any
    other kind of referent (e.g. key-point referents from update_key_point_referents live in their
    own, separate IfcRelNests).

    :param file:
    :param alignment: The IfcAlignment which hosts the stationing IfcReferent(s)
    :return: Returns the IfcRelNests or None
    """
    if not alignment.is_a("IfcAlignment"):
        raise TypeError(f"Expected IfcAlignment, instead received {alignment.is_a()}")

    for nest in alignment.IsNestedBy:
        for related_object in nest.RelatedObjects:
            if related_object.is_a("IfcReferent") and related_object.PredefinedType == "STATION":
                return nest

    return None
