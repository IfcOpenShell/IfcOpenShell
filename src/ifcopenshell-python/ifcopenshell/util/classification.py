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
    if not element.is_a("IfcRoot"):
        if hasattr(element, "HasExternalReferences"):
            return {r.RelatingReference for r in element.HasExternalReferences or []}
        elif hasattr(element, "HasExternalReference"): # Seriously, IFC?
            return {r.RelatingReference for r in element.HasExternalReference or []}
    if should_inherit:
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type and element_type != element:
            results = get_references(element_type)
    occurrence_results = {
        r.RelatingClassification
        for r in getattr(element, "HasAssociations", [])
        if r.is_a("IfcRelAssociatesClassification")
    }
    if results:
        type_references_per_system = {}
        occurrence_references_per_system = {}
        for result in results:
            type_references_per_system.setdefault(get_classification(result), []).append(result)
        for result in occurrence_results:
            occurrence_references_per_system.setdefault(get_classification(result), []).append(result)
        type_references_per_system.update(occurrence_references_per_system)
        results = set()
        for values in type_references_per_system.values():
            [results.add(v) for v in values]
        return results
    return occurrence_results


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

