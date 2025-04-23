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
import ifcopenshell.api.owner
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.schema
from typing import Optional, Union, Any


def add_reference(
    file: ifcopenshell.file,
    products: list[ifcopenshell.entity_instance],
    reference: Optional[ifcopenshell.entity_instance] = None,
    identification: Optional[str] = None,
    name: Optional[str] = None,
    classification: Optional[ifcopenshell.entity_instance] = None,
    is_lightweight=True,
) -> Union[ifcopenshell.entity_instance, None]:
    """Adds a new classification reference and assigns it to the list of products

    A classification reference is a single entry such as "Pr_12_23_34" that
    is part of an external classification system (such as Uniclass or
    Omniclass).

    References can be added to almost any object in IFC, including physical
    objects, object types, properties, tasks, costs, resources, or even
    resources such as profiles, documents, libraries, and so on.

    Classification references can be added in two ways. Option 1) specify  a
    custom arbitrary reference, where you have to manually specify the
    identification (e.g. "Pr_12_23_45") and name (e.g. "Door Products").
    Option 2) add a reference from an IFC classification library. The latter
    is preferred if you are using a common classification system such as
    Uniclass, as the library will be prepopulated with all the valid
    classifications already.

    Objects are allowed to have multiple classification references from
    multiple classification systems. This means that adding a new reference
    will not remove existing references.

    References can be inherited from types. This means that if an
    IfcWallType has a classification reference of Pr_12_23_34, then all
    IfcWall occurrences of that type automatically get the same
    classification of Pr_12_23_34. This means that it is more efficient to
    assign to types where possible. If a classification reference is
    assigned to both the type and an occurrence, then the assignment at the
    occurrence will override the type classification.

    :param product: The list of IFC objects, properties, or resources you want to
        associate the classification reference to.
    :param reference: The classification reference entity taken from an
        IFC classification library. If you supply this parameter, you will
        use option 2.
    :param identification: If you choose option 1 and do not specify a
        reference, you may manually specify an identification code. The code
        is typically a short identifier and may have punctuation to separate
        the levels of hierarchy in the classificaion (e.g. Pr_12_23_34).
    :param name: If you choose option 1 and do not specify a reference, you
        may manually specify a name. The name is typically human readable.
    :param classification: The IfcClassification entity in your IFC model
        (not the library, if you are doing option 2) that the reference is
        part of.
    :param is_lightweight: If you are doing option 2, choose whether or not
        to only add that particular reference (lighweight) or also add all
        of its parent references in the classification hierarchy (not
        lighweight). For example, adding a lightweight reference to
        Pr_12_23_34 will only add Pr_12_23_34, but adding a heavy reference
        to Pr_12_23_34 will also add Pr_12_23 and Pr_12. These parent
        references merely help describe the "tree" of classifications, but
        is generally unnecessary. Using lightweight classifications are
        recommended and is the default.

    :raises TypeError: If file is IFC2X3 and `products` has non-IfcRoot elements.

    :return: The newly added IfcClassificationReference
        or `None` if `products` was empty list.

    Example:

    .. code:: python

        # Option 1: adding and assigning a new reference from scratch
        wall_type = model.by_type("IfcWallType")[0]
        classification = ifcopenshell.api.classification.add_classification(
            model, classification="MyCustomClassification")
        ifcopenshell.api.classification.add_reference(model,
            products=[wall_type], classification=classification,
            identification="W_01", name="Interior Walls")

        # Option 2: adding a popular classification from a library
        library = ifcopenshell.open("/path/to/Uniclass.ifc")
        lib_classification = library.by_type("IfcClassification")[0]
        classification = ifcopenshell.api.classification.add_classification(
            model, classification=lib_classification)
        reference = [r for r in library.by_type("IfcClassificationReference")
            if r.Identification == "XYZ"][0]
        ifcopenshell.api.classification.add_reference(model,
            products=[wall_type], classification=classification,
            reference=reference)
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "products": products,
        "reference": reference,
        "identification": identification,
        "name": name,
        "classification": classification,
        "is_lightweight": is_lightweight,
    }
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file
    settings: dict[str, Any]

    def execute(self):
        if not self.settings["products"]:
            return

        if self.settings["reference"]:
            referenced = ifcopenshell.util.element.get_referenced_elements(self.settings["reference"])
            if set(self.settings["products"]).issubset(referenced):
                # nothing to do, all elements already have this reference assigned
                return self.settings["reference"]

        self.rooted_products: set[ifcopenshell.entity_instance] = set()
        self.non_rooted_products: set[ifcopenshell.entity_instance] = set()
        for product in self.settings["products"]:
            if product.is_a("IfcRoot"):
                self.rooted_products.add(product)
            else:
                self.non_rooted_products.add(product)

        if self.non_rooted_products and self.file.schema == "IFC2X3":
            raise TypeError(f"Cannot add reference to non-IfcRoot element in IFC2X3: {self.non_rooted_products}.")

        if self.settings["reference"]:
            return self.add_from_library()
        return self.add_from_identification()

    def add_from_identification(self):
        reference = self.get_existing_reference(self.settings["identification"])
        if not reference:
            reference = self.file.createIfcClassificationReference(
                Name=self.settings["name"], ReferencedSource=self.settings["classification"]
            )
            if self.file.schema == "IFC2X3":
                reference.ItemReference = self.settings["identification"]
            else:
                reference.Identification = self.settings["identification"]

        self.update_relationships(reference)
        return reference

    def add_from_library(self) -> ifcopenshell.entity_instance:
        if hasattr(self.settings["reference"], "ItemReference"):
            identification = self.settings["reference"].ItemReference  # IFC2X3
        else:
            identification = self.settings["reference"].Identification

        reference = self.get_existing_reference(identification)
        if not reference:
            migrator = ifcopenshell.util.schema.Migrator()

            if self.settings["is_lightweight"]:
                old_referenced_source = self.settings["reference"].ReferencedSource
                self.settings["reference"].ReferencedSource = None
            else:
                classification_name = self.settings["classification"].Name
                existing_classification = [
                    c for c in self.file.by_type("IfcClassification") if c.Name == classification_name
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

        self.update_relationships(reference)
        return reference

    def get_existing_reference(self, identification: Optional[str] = None) -> Union[ifcopenshell.entity_instance, None]:
        for reference in self.file.by_type("IfcClassificationReference"):
            if self.file.schema == "IFC2X3":
                if reference.ItemReference == identification:
                    return reference
            else:
                if reference.Identification == identification:
                    return reference

    def update_relationships(self, reference: ifcopenshell.entity_instance) -> None:
        root_rel, non_root_rel = None, None
        if self.rooted_products:
            if self.file.schema == "IFC2X3":
                for rel in self.file.by_type("IfcRelAssociatesClassification"):
                    if rel.RelatingClassification == reference:
                        root_rel = rel
                        break
            else:
                root_rel = next(iter(reference.ClassificationRefForObjects), None)

            if root_rel:
                related_objects = set(root_rel.RelatedObjects) | self.rooted_products
                root_rel.RelatedObjects = list(related_objects)
                ifcopenshell.api.owner.update_owner_history(self.file, **{"element": root_rel})
            else:
                self.file.create_entity(
                    "IfcRelAssociatesClassification",
                    OwnerHistory=ifcopenshell.api.owner.create_owner_history(self.file),
                    GlobalId=ifcopenshell.guid.new(),
                    RelatedObjects=list(self.rooted_products),
                    RelatingClassification=reference,
                )

        if self.non_rooted_products:
            # NOTE: Only Ifc4+. Ifc2x3 is already handled by raising TypeError
            non_root_rel = next(iter(reference.ExternalReferenceForResources), None)
            if non_root_rel:
                related_objects = set(non_root_rel.RelatedResourceObjects) | self.non_rooted_products
                non_root_rel.RelatedResourceObjects = list(related_objects)
            else:
                self.file.create_entity(
                    "IfcExternalReferenceRelationship",
                    RelatingReference=reference,
                    RelatedResourceObjects=list(self.non_rooted_products),
                )
