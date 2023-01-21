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


class Usecase:
    def __init__(self, file, classification=None):
        """Removes an IfcClassification from the project and all references

        The classification and all of its relationships, children references,
        and relationships between objectse and child references are completely
        removed from a project.

        :param classification: The IfcClassification entity you want to remove
        :type classification: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            classification = model.by_type("IfcClassification")[0]
            ifcopenshell.api.run("classification.remove_classification", model,
                classification=classification)
        """
        self.file = file
        self.settings = {"classification": classification}

    def execute(self):
        references = self.get_references(self.settings["classification"])
        for reference in references:
            self.file.remove(reference)
        self.file.remove(self.settings["classification"])
        for rel in self.file.by_type("IfcRelAssociatesClassification"):
            if not rel.RelatingClassification:
                self.file.remove(rel)
        for rel in self.file.by_type("IfcExternalReferenceRelationship"):
            if not rel.RelatingReference:
                self.file.remove(rel)

    def get_references(self, classification):
        results = []
        if not classification.HasReferences:
            return results
        for reference in classification.HasReferences:
            results.append(reference)
            results.extend(self.get_references(reference))
        return results
