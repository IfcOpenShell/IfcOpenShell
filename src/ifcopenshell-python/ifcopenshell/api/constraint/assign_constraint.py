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
    def __init__(self, file, product=None, constraint=None):
        """Assigns a constraint to a product

        This assigns a relationship between a product and a constraint, so that
        when a product's properties and quantities do not match the requirements
        of the constraint's metrics, results can be flagged.

        It is assumed (but not explicit in the IFC documentation) that
        constraints are inherited from the type. This way, it is not necessary
        to create lots of constraint assignments.

        :param product: The product the constraint applies to. This is anything
            which can have properties or quantities.
        :type product: ifcopenshell.entity_instance.entity_instance
        :param constraint: The IfcObjective constraint
        :type constraint: ifcopenshell.entity_instance.entity_instance
        :return: The new or updated IfcRelAssociatesConstraint relationship
        :rtype: ifcopenshell.entity_instance.entity_instance
        """
        self.file = file
        self.settings = {
            "product": product,
            "constraint": constraint,
        }

    def execute(self):
        rel = self.get_constraint_rel()
        related_objects = set(rel.RelatedObjects) if rel.RelatedObjects else set()
        related_objects.add(self.settings["product"])
        rel.RelatedObjects = list(related_objects)
        return rel

    def get_constraint_rel(self):
        for rel in self.file.by_type("IfcRelAssociatesConstraint"):
            if rel.RelatingConstraint == self.settings["constraint"]:
                return rel
        return self.file.create_entity(
            "IfcRelAssociatesConstraint",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                # TODO: owner history
                "RelatingConstraint": self.settings["constraint"],
            }
        )
