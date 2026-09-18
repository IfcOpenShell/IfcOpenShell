# IfcPatch - IFC patching utiliy
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.


class Patcher:
    # IfcClassificationItem and IfcClassificationItemRelationship are IFC2X3
    # only, IfcExternalReference covers IfcClassificationReference everywhere.
    DEPENDENT_CLASSES = (
        "IfcExternalReference",
        "IfcClassificationItem",
        "IfcClassificationItemRelationship",
    )

    def __init__(self, file, logger):
        """Removes the built-in Revit Uniformat classification.

        Revit has a bug (see https://github.com/Autodesk/revit-ifc/issues/486)
        where it always inserts a Uniformat classification regardless if your
        project needs it or not. This patch removes it.

        Example:

        .. code:: python

            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "RemoveRevitUniformatClassification"})
        """
        self.file = file
        self.logger = logger

    def patch(self):
        for classification in self.file.by_type("IfcClassification"):
            if classification.Name != "Uniformat":
                continue
            references = self.get_references(classification)
            for reference in references:
                self.file.remove(reference)
            self.file.remove(classification)
            for rel in self.file.by_type("IfcRelAssociatesClassification"):
                if not rel.RelatingClassification:
                    self.file.remove(rel)
            if self.file.schema == "IFC2X3":
                continue
            for rel in self.file.by_type("IfcExternalReferenceRelationship"):
                if not rel.RelatingReference:
                    self.file.remove(rel)

    def get_references(self, classification):
        # IFC2X3 has no HasReferences inverse on IfcClassification or
        # IfcClassificationReference, so the dependents are resolved through the
        # inverse index instead of a schema specific inverse attribute.
        results = []
        seen = set()
        queue = [classification]
        while queue:
            for inverse in self.file.get_inverse(queue.pop()):
                if inverse.id() in seen:
                    continue
                if not any(inverse.is_a(c) for c in self.DEPENDENT_CLASSES):
                    continue
                seen.add(inverse.id())
                results.append(inverse)
                queue.append(inverse)
        return results
