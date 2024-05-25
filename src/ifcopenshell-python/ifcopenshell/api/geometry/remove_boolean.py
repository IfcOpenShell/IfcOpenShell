# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.util.element


def remove_boolean(file: ifcopenshell.file, item: ifcopenshell.entity_instance) -> None:
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {"item": item}
    return usecase.execute()


class Usecase:
    def execute(self):
        item = None
        for inverse in self.file.get_inverse(self.settings["item"]):
            if inverse.is_a("IfcBooleanResult"):
                item = inverse
                break

        representation = self.get_representation(item)

        first_operand = item.FirstOperand
        second_operand = item.SecondOperand
        for inverse in self.file.get_inverse(item):
            ifcopenshell.util.element.replace_attribute(inverse, item, first_operand)
        self.file.remove(item)
        ifcopenshell.util.element.remove_deep2(self.file, second_operand)

        item_classes = {i.is_a() for i in representation.Items}
        if "IfcBooleanResult" in item_classes:
            representation.RepresentationType = "CSG"
        elif "IfcBooleanClippingResult" in item_classes:
            representation.RepresentationType = "Clipping"
        else:
            representation.RepresentationType = "SweptSolid"

    def get_representation(self, item):
        for inverse in self.file.get_inverse(item):
            if inverse.is_a("IfcShapeRepresentation"):
                return inverse
            elif inverse.is_a("IfcRepresentationItem"):
                return self.get_representation(inverse)
