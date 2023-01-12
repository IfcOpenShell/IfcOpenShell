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


class Usecase:
    def __init__(self, file, product=None, reference=None):
        """Associates a product with a library reference

        A product may be associated with zero, one, or many references across
        multiple libraries. See ifcopenshell.api.library.add_reference for more
        detail about how references work.

        :param product: The IfcProduct you want to associate with the reference
        :type product: ifcopenshell.entity_instance.entity_instance
        :param reference: The IfcLibraryReference you want the product to be
            associated with.
        :type reference: ifcopenshell.entity_instance.entity_instance
        :return: The IfcRelAssociatesLibrary relationship entity
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            library = ifcopenshell.api.run("library.add_library", model, name="Brickschema")

            # Let's create a reference to a single AHU in our Brickschema dataset
            reference = ifcopenshell.api.run("library.add_reference", model, library=library)
            ifcopenshell.api.run("library.edit_reference", model,
                reference=reference, attributes={"Identification": "http://example.org/digitaltwin#AHU01"})

            # Let's assume we have an AHU in our model.
            ahu = ifcopenshell.api.run("root.create_entity", model,
                ifc_class="IfcUnitaryEquipment", predefined_type="AIRHANDLER")

            # And now assign the IFC model's AHU with its Brickschema counterpart
            ifcopenshell.api.run("library.assign_reference", model, reference=reference, product=ahu)
        """
        self.file = file
        self.settings = {
            "product": product,
            "reference": reference,
        }

    def execute(self):
        if self.file.schema == "IFC2X3":
            rels = self.get_ifc2x3_rels()
        else:
            rels = self.settings["reference"].LibraryRefForObjects
        if not rels:
            return self.file.create_entity(
                "IfcRelAssociatesLibrary",
                GlobalId=ifcopenshell.guid.new(),
                OwnerHistory=ifcopenshell.api.run("owner.create_owner_history", self.file),
                RelatedObjects=[self.settings["product"]],
                RelatingLibrary=self.settings["reference"],
            )

        for rel in rels:
            if self.settings["product"] in rel.RelatedObjects:
                return rel

        rel = rels[0]
        related_objects = list(rel.RelatedObjects)
        related_objects.append(self.settings["product"])
        rel.RelatedObjects = related_objects
        ifcopenshell.api.run("owner.update_owner_history", self.file, element=rel)
        return rel

    def get_ifc2x3_rels(self):
        return [
            r for r in self.file.by_type("IfcRelAssociatesLibrary") if r.RelatingLibrary == self.settings["reference"]
        ]
