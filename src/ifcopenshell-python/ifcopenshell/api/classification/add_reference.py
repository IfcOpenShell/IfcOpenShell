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
import ifcopenshell.util.schema


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "product": None,
            "reference": None,
            "classification": None,
            "is_lightweight": True,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        relating_classification = None

        if hasattr(self.settings["reference"], "ItemReference"):
            identification = self.settings["reference"].ItemReference  # IFC2X3
        else:
            identification = self.settings["reference"].Identification

        for reference in self.file.by_type("IfcClassificationReference"):
            if self.file.schema == "IFC2X3":
                if reference.ItemReference == identification:
                    relating_classification = reference
                    break
            else:
                if reference.Identification == identification:
                    relating_classification = reference
                    break

        if relating_classification:
            association = self.get_association(relating_classification)
            related_objects = set(association.RelatedObjects)
            related_objects.add(self.settings["product"])
            association.RelatedObjects = list(related_objects)
            return

        migrator = ifcopenshell.util.schema.Migrator()
        if self.settings["is_lightweight"]:
            old_referenced_source = self.settings["reference"].ReferencedSource
            self.settings["reference"].ReferencedSource = None
        relating_classification = migrator.migrate(self.settings["reference"], self.file)
        if self.settings["is_lightweight"]:
            relating_classification.ReferencedSource = self.settings["classification"]
            self.settings["reference"].ReferencedSource = old_referenced_source
        self.file.create_entity(
            "IfcRelAssociatesClassification",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "RelatedObjects": [self.settings["product"]],
                "RelatingClassification": relating_classification,
            }
        )

    def get_association(self, reference):
        if self.file.schema == "IFC2X3":
            for association in self.file.by_type("IfcRelAssociatesClassification"):
                if association.RelatingClassification == reference:
                    return association
        elif reference.ClassificationRefForObjects:
            return reference.ClassificationRefForObjects[0]
