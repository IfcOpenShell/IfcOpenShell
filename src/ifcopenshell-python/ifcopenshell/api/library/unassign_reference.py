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
        """Unassigns a product from a reference

        If the product isn't assigned to the reference, nothing will happen.

        :param reference: The IfcLibraryReference to unassign from
        :type reference: ifcopenshell.entity_instance.entity_instance
        :param product: A IfcProduct element to unassign from the reference
        :type product: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

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

            # Let's change our mind and unassign it.
            ifcopenshell.api.run("library.unassign_reference", model, reference=reference, product=ahu)
        """

        self.file = file
        self.settings = {"reference": reference, "product": product}

    def execute(self):
        rels = self.settings["reference"].LibraryRefForObjects
        if not rels:
            return
        for rel in rels:
            if self.settings["product"] in rel.RelatedObjects:
                if len(rel.RelatedObjects) == 1:
                    self.file.remove(rel)
                    continue
                related_objects = list(rel.RelatedObjects)
                related_objects.remove(self.settings["product"])
                rel.RelatedObjects = related_objects
