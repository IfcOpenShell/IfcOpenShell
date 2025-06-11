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
from typing import Union


def assign_constraint(
    file: ifcopenshell.file,
    products: list[ifcopenshell.entity_instance],
    constraint: ifcopenshell.entity_instance,
) -> Union[ifcopenshell.entity_instance, None]:
    """Assigns a constraint to a list of products

    This assigns a relationship between a product and a constraint, so that
    when a product's properties and quantities do not match the requirements
    of the constraint's metrics, results can be flagged.

    It is assumed (but not explicit in the IFC documentation) that
    constraints are inherited from the type. This way, it is not necessary
    to create lots of constraint assignments.

    :param products: The list of products the constraint applies to. This is anything
        which can have properties or quantities.
    :param constraint: The IfcObjective constraint
    :return: The new or updated IfcRelAssociatesConstraint relationship
        or `None` if `products` was an empty list.
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(products, constraint)


class Usecase:
    file: ifcopenshell.file

    def execute(self, products: list[ifcopenshell.entity_instance], constraint: ifcopenshell.entity_instance):
        if not products:
            return
        products_set = set(products)

        rels = self.get_constraint_rels(constraint)
        related_objects = set()
        for rel in rels:
            related_objects.update(rel.RelatedObjects)

        products_to_assign = products_set - related_objects
        if not products_to_assign:
            return rels[0]

        rel = next(iter(rels), None)

        if rel:
            related_objects = set(rel.RelatedObjects) | products_to_assign
            rel.RelatedObjects = list(related_objects)
            ifcopenshell.api.owner.update_owner_history(self.file, element=rel)
            return rel

        return self.file.create_entity(
            "IfcRelAssociatesConstraint",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.owner.create_owner_history(self.file),
                "RelatingConstraint": constraint,
                "RelatedObjects": list(products_to_assign),
            }
        )

    def get_constraint_rels(self, constraint: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        rels = []
        for rel in self.file.get_inverse(constraint):
            if rel.is_a("IfcRelAssociatesConstraint"):
                rels.append(rel)
        return rels
