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
    def __init__(self, file, reference=None, product=None):
        """Removes a classification reference from a product

        If the classification reference is no longer associated to any products,
        the classification reference itself is also removed.

        :param reference: The IfcClassificationReference entity of the
            relationship you want to remove.
        :type reference: ifcopenshell.entity_instance.entity_instance
        :param product: The object entity of the relationship you want to
            remove.
        :type reference: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            wall_type = model.by_type("IfcWallType")[0]
            classification = ifcopenshell.api.run("classification.add_classification",
                model, classification="MyCustomClassification")
            reference = ifcopenshell.api.run("classification.add_reference", model,
                product=wall_type, classification=classification,
                identification="W_01", name="Interior Walls")
            ifcopenshell.api.run("classification.remove_reference", model,
                reference=reference, product=wall_type)
        """
        self.file = file
        self.settings = {"reference": reference, "product": product}

    def execute(self):
        if self.settings["product"].is_a("IfcRoot"):
            for rel in self.file.by_type("IfcRelAssociatesClassification"):
                if rel.RelatingClassification == self.settings["reference"] and rel.RelatedObjects:
                    if self.settings["product"] in rel.RelatedObjects:
                        related_objects = list(rel.RelatedObjects)
                        related_objects.remove(self.settings["product"])
                        if len(related_objects):
                            rel.RelatedObjects = related_objects
                        else:
                            self.file.remove(rel)
        else:
            for rel in self.file.by_type("IfcExternalReferenceRelationship"):
                if rel.RelatingReference == self.settings["reference"] and rel.RelatedResourceObjects:
                    if self.settings["product"] in rel.RelatedResourceObjects:
                        related_objects = list(rel.RelatedResourceObjects)
                        related_objects.remove(self.settings["product"])
                        if len(related_objects):
                            rel.RelatedResourceObjects = related_objects
                        else:
                            self.file.remove(rel)

        # TODO: we only handle lightweight classifications here
        if (
            not self.settings["reference"].ClassificationRefForObjects
            and not self.settings["reference"].ExternalReferenceForResources
        ):
            self.file.remove(self.settings["reference"])
