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
import ifcopenshell.api.aggregate
import ifcopenshell.api.geometry
import ifcopenshell.api.pset
import ifcopenshell.api.spatial
import ifcopenshell.api.type
import ifcopenshell.guid
import ifcopenshell.util.representation
import ifcopenshell.util.type
import ifcopenshell.util.schema
import ifcopenshell.util.element
from typing import Optional, Union, Literal


def reassign_class(
    file: ifcopenshell.file,
    product: ifcopenshell.entity_instance,
    ifc_class: str = "IfcBuildingElementProxy",
    predefined_type: Optional[str] = None,
    occurrence_class: Optional[str] = None,
) -> ifcopenshell.entity_instance:
    """Changes the class of a product

    If you ever created a wall then realised it's meant to be something
    else, this function lets you change the IFC class whilst retaining all
    other geometry and relationships.

    This is especially useful when dealing with poorly classified data from
    proprietary software with limited IFC capabilities.

    If you are reassigning a type, the occurrence classes are also
    reassigned to maintain validity.

    Vice versa, if you are reassigning an occurrence, the type is also
    reassigned in IFC4 and up. In IFC2X3, this may not occur if the type
    cannot be unambiguously derived, so you are required to manually check
    this.

    Reassigning type class to occurrence (and vice versa) is supported.

    :param product: The IfcProduct that you want to change the class of.
    :param ifc_class: The new IFC class you want to change it to.
    :param predefined_type: In case you want to change the predefined type
        too. User defined types are also allowed, just type what you want.
    :param occurrence_class: IFC class to assign to occurrences in case
        if provided ``ifc_class`` is IfcTypeProduct.
        If omitted, class will be deduced automatically from the type.
        Only really needed in IFC2X3, since in IFC4+ there is no ambiguity on
        what class to assign to occurrences.
    :return: The newly modified product.

    Example:

    .. code:: python

        # We have a wall.
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # Oh, did I say wall? I meant slab.
        slab = ifcopenshell.api.root.reassign_class(model, product=wall, ifc_class="IfcSlab")

        # Warning: this will crash since wall doesn't exist any more.
        print(wall) # Kaboom.
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(product, ifc_class, predefined_type, occurrence_class)


class Usecase:
    file: ifcopenshell.file

    def execute(
        self,
        product: ifcopenshell.entity_instance,
        ifc_class: str,
        predefined_type: Union[str, None],
        occurrence_class: Union[str, None],
    ) -> ifcopenshell.entity_instance:
        self.occurrence_class = occurrence_class
        was_type_product_before = product.is_a("IfcTypeProduct")
        self.schema = schema = ifcopenshell.schema_by_name(self.file.schema)
        is_type_product_after: bool
        is_type_product_after = schema.declaration_by_name(ifc_class)._is("IfcTypeProduct")

        if was_type_product_before == is_type_product_after:
            return self.simple_reassignment(product, ifc_class, predefined_type)

        switch_type = "occurrence_to_type" if is_type_product_after else "type_to_occurrence"

        return self.switch_between_class_types(
            product,
            switch_type,
            ifc_class,
            predefined_type,
        )

    def switch_between_class_types(
        self,
        element: ifcopenshell.entity_instance,
        switch_type: Literal["occurrence_to_type", "type_to_occurrence"],
        ifc_class: str,
        predefined_type: Union[str, None],
    ) -> ifcopenshell.entity_instance:

        psets_to_reassign: list[ifcopenshell.entity_instance] = []

        representations = list(ifcopenshell.util.representation.get_representations_iter(element))
        for rep in representations:
            if switch_type == "type_to_occurrence":
                rep = ifcopenshell.util.representation.resolve_representation(rep)
            ifcopenshell.api.geometry.unassign_representation(self.file, product=element, representation=rep)

        if switch_type == "type_to_occurrence":
            occurrences = ifcopenshell.util.element.get_types(element)
            # Don't need to reassign as psets are linked to type directly, without rel.
            psets_to_reassign = element.HasPropertySets or []

            element = self.reassign_class(element, ifc_class, predefined_type)
            ifcopenshell.api.type.unassign_type(self.file, occurrences)

        else:  # occurrence_to_type
            element_type = ifcopenshell.util.element.get_type(element)
            # Handle element type.
            if element_type:
                ifcopenshell.api.type.unassign_type(self.file, [element])

            # Handle containers and aggregates.
            if ifcopenshell.util.element.get_container(element):
                ifcopenshell.api.spatial.unassign_container(self.file, [element])
            elif ifcopenshell.util.element.get_aggregate(element):
                ifcopenshell.api.aggregate.unassign_object(self.file, [element])

            psets = ifcopenshell.util.element.get_psets(element)
            for pset_name in psets:
                pset = self.file.by_id(psets[pset_name]["id"])
                psets_to_reassign.append(pset)
                ifcopenshell.api.pset.unassign_pset(self.file, [element], pset)

            element = self.reassign_class(element, ifc_class, predefined_type)

        # Reassign psets.
        for pset in psets_to_reassign:
            ifcopenshell.api.pset.assign_pset(self.file, [element], pset)

        # Reassign representations.
        for rep in representations:
            ifcopenshell.api.geometry.assign_representation(self.file, product=element, representation=rep)

        # Keep IFC valid (PlacementForShapeRepresentation).
        if switch_type == "type_to_occurrence" and representations:
            ifcopenshell.api.geometry.edit_object_placement(self.file, product=element)

        return element

    def simple_reassignment(
        self,
        element: ifcopenshell.entity_instance,
        ifc_class: str,
        predefined_type: Union[str, None],
    ) -> ifcopenshell.entity_instance:
        """
        Simple class reassignment doesn't involve changing class type.

        E.g. IfcWindow (IfcProduct class) -> IfcWall (other IfcProduct class).

        Changing class type (e.g. IfcWindowType -> IfcWindow) is more complex
        as it requires to recreate some entities / assign them in different way
        (e.g. representations, property sets and their rels).
        """
        element = self.reassign_class(element, ifc_class, predefined_type)
        if element.is_a("IfcTypeProduct"):

            if self.occurrence_class:
                occurrence_class = self.occurrence_class
            else:
                # NOTE: in theory we can skip reassignment in IFC2X3 in some cases
                # e.g. if occurrence is IfcRoof and we're reassigning to IfcBuildingElementProxyType
                # but currently type_to_entity_map doesn't completely match entity_to_type_map,
                # see type.py for more details.
                occurrence_class = next(
                    iter(ifcopenshell.util.type.get_applicable_entities(ifc_class, self.file.schema))
                )
            assert not self.schema.declaration_by_name(occurrence_class)._is(
                "IfcTypeProduct"
            ), f"Unexpected occurrence_class: '{occurrence_class}' / '{self.occurrence_class}'."

            for occurrence in ifcopenshell.util.element.get_types(element):
                self.reassign_class(occurrence, occurrence_class, predefined_type)
        else:
            element_type = ifcopenshell.util.element.get_type(element)
            if element_type:
                ifc_class_ = next(iter(ifcopenshell.util.type.get_applicable_types(ifc_class, self.file.schema)))
                element_type = self.reassign_class(element_type, ifc_class_, predefined_type)
                ifc_class = element.is_a()
                for occurrence in ifcopenshell.util.element.get_types(element_type):
                    if occurrence == element:
                        continue
                    self.reassign_class(occurrence, ifc_class, predefined_type)
        return element

    def reassign_class(
        self, element: ifcopenshell.entity_instance, ifc_class: str, predefined_type: Union[str, None]
    ) -> ifcopenshell.entity_instance:
        element = ifcopenshell.util.schema.reassign_class(self.file, element, ifc_class)
        if predefined_type and hasattr(element, "PredefinedType"):
            try:
                element.PredefinedType = predefined_type
            except:
                # PredefinedType wasn't in the respective enum, assume it's actually USERDEFINED
                # and set .ElementType / .ObjectType to the provided predefined type
                element.PredefinedType = "USERDEFINED"
                if element.is_a("IfcTypeProduct"):
                    element.ElementType = predefined_type
                else:
                    element.ObjectType = predefined_type

        return element
