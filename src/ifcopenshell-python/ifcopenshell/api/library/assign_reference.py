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
from typing import Union


def assign_reference(
    file: ifcopenshell.file, products: ifcopenshell.entity_instance, reference: ifcopenshell.entity_instance
) -> Union[ifcopenshell.entity_instance, None]:
    """Associates a list products with a library reference

    A product may be associated with zero, one, or many references across
    multiple libraries. See ifcopenshell.api.library.add_reference for more
    detail about how references work.

    :param products: The list of IfcProducts you want to associate with the reference
    :type products: list[ifcopenshell.entity_instance]
    :param reference: The IfcLibraryReference you want the product to be
        associated with.
    :type reference: ifcopenshell.entity_instance
    :return: The IfcRelAssociatesLibrary relationship entity
        or `None` if `products` was an empty list or all products were
        already assigned to the `reference`.
    :rtype: Union[ifcopenshell.entity_instance, None]

    Example:

    .. code:: python

        library = ifcopenshell.api.library.add_library(model, name="Brickschema")

        # Let's create a reference to a single AHU in our Brickschema dataset
        reference = ifcopenshell.api.library.add_reference(model, library=library)
        ifcopenshell.api.library.edit_reference(model,
            reference=reference, attributes={"Identification": "http://example.org/digitaltwin#AHU01"})

        # Let's assume we have an AHU in our model.
        ahu = ifcopenshell.api.root.create_entity(model,
            ifc_class="IfcUnitaryEquipment", predefined_type="AIRHANDLER")

        # And now assign the IFC model's AHU with its Brickschema counterpart
        ifcopenshell.api.library.assign_reference(model, reference=reference, products=[ahu])
    """
    settings = {
        "products": products,
        "reference": reference,
    }

    # TODO: do we need to support non-ifcroot elements like we do in classification.add_reference?

    referenced_elements = ifcopenshell.util.element.get_referenced_elements(settings["reference"])
    products: set[ifcopenshell.entity_instance] = set(settings["products"])
    products = products - referenced_elements

    if not products:
        return

    if file.schema == "IFC2X3":
        rel = next(
            (r for r in file.by_type("IfcRelAssociatesLibrary") if r.RelatingLibrary == settings["reference"]),
            None,
        )
    else:
        rel = next(iter(settings["reference"].LibraryRefForObjects), None)

    if not rel:
        return file.create_entity(
            "IfcRelAssociatesLibrary",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.owner.create_owner_history(file),
            RelatedObjects=list(products),
            RelatingLibrary=settings["reference"],
        )

    related_objects = set(rel.RelatedObjects) | products
    rel.RelatedObjects = list(related_objects)
    ifcopenshell.api.owner.update_owner_history(file, element=rel)
    return rel
