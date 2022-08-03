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
            "identification": None,
            "name": None,
            "classification": None,
            "is_lightweight": True,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["reference"]:
            return self.add_from_library()
        return self.add_from_identification()

    def add_from_identification(self):
        reference = self.get_existing_reference(self.settings["identification"])
        if reference:
            self.add_to_existing_relationship(reference)
        else:
            reference = self.file.createIfcClassificationReference(
                Name=self.settings["name"], ReferencedSource=self.settings["classification"]
            )
            if self.file.schema == "IFC2X3":
                reference.ItemReference = self.settings["identification"]
            else:
                reference.Identification = self.settings["identification"]
            self.add_new_relationship(reference)
        return reference

    def add_from_library(self):
        if hasattr(self.settings["reference"], "ItemReference"):
            identification = self.settings["reference"].ItemReference  # IFC2X3
        else:
            identification = self.settings["reference"].Identification

        reference = self.get_existing_reference(identification)

        if reference:
            self.add_to_existing_relationship(reference)
            return reference

        migrator = ifcopenshell.util.schema.Migrator()

        if self.settings["is_lightweight"]:
            old_referenced_source = self.settings["reference"].ReferencedSource
            self.settings["reference"].ReferencedSource = None
        else:
            existing_classification = [
                c for c in self.file.by_type("IfcClassification") if c.Name == self.settings["classification"].Name
            ]

        reference = migrator.migrate(self.settings["reference"], self.file)

        if self.settings["is_lightweight"]:
            reference.ReferencedSource = self.settings["classification"]
            self.settings["reference"].ReferencedSource = old_referenced_source
        elif existing_classification:
            to_delete = set()
            for traversed_reference in self.file.traverse(reference):
                if traversed_reference.ReferencedSource.is_a("IfcClassification"):
                    to_delete.add(traversed_reference.ReferencedSource)
                    traversed_reference.ReferencedSource = existing_classification[0]
                    break
            for element in to_delete:
                self.file.remove(element)
        self.add_new_relationship(reference)

    def get_existing_reference(self, identification):
        for reference in self.file.by_type("IfcClassificationReference"):
            if self.file.schema == "IFC2X3":
                if reference.ItemReference == identification:
                    return reference
            else:
                if reference.Identification == identification:
                    return reference

    def add_new_relationship(self, reference):
        self.file.create_entity(
            "IfcRelAssociatesClassification",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[self.settings["product"]],
            RelatingClassification=reference,
        )

    def add_to_existing_relationship(self, reference):
        rel = self.get_rel_associates_classification(reference)
        related_objects = set(rel.RelatedObjects)
        related_objects.add(self.settings["product"])
        rel.RelatedObjects = list(related_objects)

    def get_rel_associates_classification(self, reference):
        if self.file.schema == "IFC2X3":
            for association in self.file.by_type("IfcRelAssociatesClassification"):
                if association.RelatingClassification == reference:
                    return association
        elif reference.ClassificationRefForObjects:
            return reference.ClassificationRefForObjects[0]
