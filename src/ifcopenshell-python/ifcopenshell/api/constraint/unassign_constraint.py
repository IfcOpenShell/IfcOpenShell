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
    def __init__(self, file, product=None, constraint=None):
        """Unassigns a constraint to a product

        The constraint will not be deleted and is available to be assigned to
        other products.

        :param product: The product the constraint applies to.
        :type product: ifcopenshell.entity_instance.entity_instance
        :param constraint: The IfcObjective constraint
        :type constraint: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None
        """
        self.file = file
        self.settings = {
            "product": product,
            "constraint": constraint,
        }

    def execute(self):
        for rel in self.settings["product"].HasAssociations:
            if rel.is_a("IfcRelAssociatesConstraint") and rel.RelatingConstraint == self.settings["constraint"]:
                self.file.remove(rel)
