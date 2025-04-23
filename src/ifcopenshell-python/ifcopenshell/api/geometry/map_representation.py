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


def map_representation(
    file: ifcopenshell.file, representation: ifcopenshell.entity_instance
) -> ifcopenshell.entity_instance:
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(representation)


class Usecase:
    file: ifcopenshell.file

    def execute(self, representation: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        self.representation = representation
        mapping_source = self.get_mapping_source()

        zero = self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
        x_axis = self.file.createIfcDirection((1.0, 0.0, 0.0))
        y_axis = self.file.createIfcDirection((0.0, 1.0, 0.0))
        z_axis = self.file.createIfcDirection((0.0, 0.0, 1.0))

        mapping_target = self.file.createIfcCartesianTransformationOperator3D(x_axis, y_axis, zero, 1, z_axis)
        mapped_item = self.file.createIfcMappedItem(mapping_source, mapping_target)
        return self.file.create_entity(
            "IfcShapeRepresentation",
            **{
                "ContextOfItems": representation.ContextOfItems,
                "RepresentationIdentifier": representation.RepresentationIdentifier,
                "RepresentationType": "MappedRepresentation",
                "Items": [mapped_item],
            }
        )

    def get_mapping_source(self) -> ifcopenshell.entity_instance:
        for inverse in self.file.get_inverse(self.representation):
            if inverse.is_a("IfcRepresentationMap"):
                return inverse
        zero = self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
        x_axis = self.file.createIfcDirection((1.0, 0.0, 0.0))
        z_axis = self.file.createIfcDirection((0.0, 0.0, 1.0))
        mapping_origin = self.file.createIfcAxis2Placement3D(zero, z_axis, x_axis)
        return self.file.createIfcRepresentationMap(
            MappingOrigin=mapping_origin, MappedRepresentation=self.representation
        )
