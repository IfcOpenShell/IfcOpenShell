# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, classification=None):
        """Adds a new classification system to the project

        External classification systems such as Uniclass or Omniclass are
        ways of categorising elements in the AEC industry, typically
        standardised or nominated by governments or companies. A system
        typically contains a series of hierarchical reference codes and labels
        like Pr_12_23_34.

        Classifications may be applied to many things, not just physical
        elements, such as doors and windows, spatial elements, tasks, cost
        items, or even resources.

        Prior to assigning classificaion references, you need to add the name
        and metadata of the classification system that you will use in your
        project. Classification systems may be revised over time, so this
        metadata includes the edition date.

        Common classification systems are provided as an IFC library which may
        be downloaded from https://github.com/Moult/IfcClassification for your
        convenience. It is advised to use these to ensure that the
        classification metadata is standardised.

        Adding a classification system will not add the entire hierarchy of
        references available in the classification. References need to be added
        separately. Typically, you'd only add the references that you use in
        your project, see ifcopenshell.api.classification.add_reference for more
        information.

        :param classification: If a string is provided, it is assumed to be the
            name of your classification system. This is necessary if you are
            creating your own custom classification system. Alternatively, you
            may provide an entity_instance of an IfcClassification from an IFC
            classification library. The latter approach is preferred if you are
            using a commonly known system such as Uniclass, as this will ensure
            all metadata is added correctly.
        :type classification: str,ifcopenshell.entity_instance.entity_instance
        :return: The added IfcClassification element
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Option 1: adding a custom clasification from scratch
            ifcopenshell.api.run("classification.add_classification", model,
                classification="MyCustomClassification")

            # Option 2: adding a popular classification from a library
            library = ifcopenshell.open("/path/to/Uniclass.ifc")
            classification = library.by_type("IfcClassification")[0]
            ifcopenshell.api.run("classification.add_classification", model,
                classification=classification)
        """
        self.file = file
        self.settings = {
            "classification": classification,
        }

    def execute(self):
        if isinstance(self.settings["classification"], str):
            classification = self.file.createIfcClassification(Name=self.settings["classification"])
            self.relate_to_project(classification)
            return classification
        return self.add_from_library()

    def add_from_library(self):
        edition_date = None
        if self.settings["classification"].EditionDate:
            edition_date = ifcopenshell.util.date.ifc2datetime(self.settings["classification"].EditionDate)
            self.settings["classification"].EditionDate = None

        migrator = ifcopenshell.util.schema.Migrator()
        result = migrator.migrate(self.settings["classification"], self.file)

        # TODO: should auto date migration be part of the migrator?
        if self.file.schema == "IFC2X3" and edition_date:
            result.EditionDate = self.file.create_entity(
                "IfcCalendarDate", **ifcopenshell.util.date.datetime2ifc(edition_date, "IfcCalendarDate")
            )
        else:
            result.EditionDate = ifcopenshell.util.date.datetime2ifc(edition_date, "IfcDate")

        self.relate_to_project(result)

        return result  # See bug #1272

        try:
            result = self.file.add(self.settings["classification"])
        except:
            migrator = ifcopenshell.util.schema.Migrator()
            result = migrator.migrate(self.settings["classification"], self.file)

    def relate_to_project(self, classification):
        self.file.create_entity(
            "IfcRelAssociatesClassification",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[self.file.by_type("IfcProject")[0]],
            RelatingClassification=classification,
        )
