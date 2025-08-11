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

import ifcopenshell.api.owner
import ifcopenshell.api.geometry
import ifcopenshell.util.element
from typing import Any


def assign_representation(
    file: ifcopenshell.file, product: ifcopenshell.entity_instance, representation: ifcopenshell.entity_instance
) -> None:
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(product, representation)


class Usecase:
    file: ifcopenshell.file

    def execute(self, product: ifcopenshell.entity_instance, representation: ifcopenshell.entity_instance) -> None:
        if product.is_a("IfcProduct"):
            product_type = ifcopenshell.util.element.get_type(product)
            if (
                product_type
                and product_type.RepresentationMaps
                and representation.RepresentationType != "MappedRepresentation"
                # Revit is adding a non-mapped representation to the exported profile-based types,
                # so assigning representation to occurrence by accident was assigning it to the type.
                # We guard from this by skipping profile and layer-based types.
                # See 6934 for example.
                and not (
                    (material := ifcopenshell.util.element.get_material(product_type))
                    and material.is_a() in ("IfcMaterialProfileSet", "IfcMaterialLayerSet")
                )
            ):
                product = product_type

        if product.is_a("IfcProduct"):
            self.assign_product_representation(product, representation)
        elif product.is_a("IfcTypeProduct"):
            if product.RepresentationMaps:
                maps = list(product.RepresentationMaps)
            else:
                maps = []
            self.zero = self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
            self.x_axis = self.file.createIfcDirection((1.0, 0.0, 0.0))
            self.z_axis = self.file.createIfcDirection((0.0, 0.0, 1.0))
            maps.append(
                self.file.create_entity(
                    "IfcRepresentationMap",
                    **{
                        "MappingOrigin": self.file.createIfcAxis2Placement3D(self.zero, self.z_axis, self.x_axis),
                        "MappedRepresentation": representation,
                    },
                )
            )
            product.RepresentationMaps = maps
            if self.file.schema == "IFC2X3":
                types = product.ObjectTypeOf
            else:
                types = product.Types
            if types:
                for element in types[0].RelatedObjects:
                    mapped_representation = ifcopenshell.api.geometry.map_representation(
                        self.file, representation=representation
                    )
                    self.assign_product_representation(element, mapped_representation)
        ifcopenshell.api.owner.update_owner_history(self.file, element=product)

    def assign_product_representation(
        self, product: ifcopenshell.entity_instance, representation: ifcopenshell.entity_instance
    ) -> None:
        definition = product.Representation
        if not definition:
            definition = self.file.createIfcProductDefinitionShape()
            product.Representation = definition
        representations = list(definition.Representations) if definition.Representations else []
        representations.append(representation)
        definition.Representations = representations
