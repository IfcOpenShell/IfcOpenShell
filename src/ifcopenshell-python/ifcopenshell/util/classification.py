# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.util.element


def get_references(element, should_inherit=True):
    results = set()
    if should_inherit:
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type and element_type != element:
            results.update(get_references(element_type))
    results.update(
        {
            r.RelatingClassification
            for r in getattr(element, "HasAssociations", [])
            if r.is_a("IfcRelAssociatesClassification")
        }
    )
    return results


def get_classification(reference):
    if reference.is_a("IfcClassification"):
        return reference
    return get_classification(reference.ReferencedSource)


def get_inherited_references(reference):
    results = []
    while True:
        if not reference or reference.is_a("IfcClassification"):
            break
        results.append(reference)
        reference = reference.ReferencedSource
    return results

