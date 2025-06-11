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
from typing import Optional


def get_references(element: ifcopenshell.entity_instance, should_inherit=True) -> set[ifcopenshell.entity_instance]:
    """Gets classification references associated with the element

    :param should_inherit: If true, classification references are inherited
        from the type. Classifications can be overriden per system.
    :return: A set of IfcClassificationReference
    """
    results = set()
    if not element.is_a("IfcRoot"):
        if (references := getattr(element, "HasExternalReferences", None)) is not None or (
            references := getattr(element, "HasExternalReference", None)
        ) is not None:
            return {r.RelatingReference for r in references}
    if should_inherit and element.is_a("IfcObject"):
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


def get_classification(reference: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """Get the IfcClassification that a classification reference belongs to

    :param reference: An IfcClassificationReference
    :return: IfcClassification
    """
    if reference.is_a("IfcClassification"):
        return reference
    return get_classification(reference.ReferencedSource) if reference.ReferencedSource is not None else None


def get_inherited_references(reference: Optional[ifcopenshell.entity_instance]) -> list[ifcopenshell.entity_instance]:
    results = []
    while True:
        if not reference or reference.is_a("IfcClassification"):
            break
        results.append(reference)
        reference = reference.ReferencedSource
    return results


def get_classification_data(file: ifcopenshell.file) -> Optional[tuple[list[dict], str]]:
    if not file or not file.by_type("IfcClassification"):
        return [], ""
    classification = file.by_type("IfcClassification")[0]
    classification_name = classification.Name

    def process_references(reference):
        data = reference.get_info()
        del data["ReferencedSource"]
        data["referenced_source"] = reference.ReferencedSource.id() if reference.ReferencedSource else None
        data["has_references"] = bool(reference.HasReferences)
        data["references"] = (
            [process_references(ref) for ref in reference.HasReferences] if reference.HasReferences else []
        )
        return data

    classification_data = [process_references(reference) for reference in classification.HasReferences]
    return classification_data, classification_name
