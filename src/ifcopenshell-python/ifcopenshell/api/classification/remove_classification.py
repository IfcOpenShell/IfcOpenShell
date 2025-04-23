# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.util.element


def remove_classification(file: ifcopenshell.file, classification: ifcopenshell.entity_instance) -> None:
    """Removes an IfcClassification from the project and all references

    The classification and all of its relationships, children references,
    and relationships between objects and child references are completely
    removed from a project.

    :param classification: The IfcClassification entity you want to remove
    :return: None

    Example:

    .. code:: python

        classification = model.by_type("IfcClassification")[0]
        ifcopenshell.api.classification.remove_classification(model,
            classification=classification)
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(classification)


class Usecase:
    file: ifcopenshell.file

    def execute(self, classification: ifcopenshell.entity_instance) -> None:
        references = self.get_references(classification)
        for reference in references:
            self.file.remove(reference)
        self.file.remove(classification)
        for rel in self.file.by_type("IfcRelAssociatesClassification"):
            if not rel.RelatingClassification:
                history = rel.OwnerHistory
                self.file.remove(rel)
                if history:
                    ifcopenshell.util.element.remove_deep2(self.file, history)

        if self.file.schema != "IFC2X3":
            for rel in self.file.by_type("IfcExternalReferenceRelationship"):
                if not rel.RelatingReference:
                    self.file.remove(rel)

    def get_references(self, classification: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        results = []
        if self.file.schema == "IFC2X3":
            for reference in self.file.by_type("IfcClassificationReference"):
                if reference.ReferencedSource == classification:
                    results.append(reference)
        else:
            for reference in classification.HasReferences:
                results.append(reference)
                results.extend(self.get_references(reference))
        return results
