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
import ifcopenshell.util.element


def unassign_constraint(
    file: ifcopenshell.file,
    products: list[ifcopenshell.entity_instance],
    constraint: ifcopenshell.entity_instance,
) -> None:
    """Unassigns a constraint from a list of products

    The constraint will not be deleted and is available to be assigned to
    other products.

    :param products: The list of products the constraint applies to.
    :param constraint: The IfcObjective constraint
    :return: None
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(products, constraint)


class Usecase:
    file: ifcopenshell.file

    def execute(self, products_: list[ifcopenshell.entity_instance], constraint: ifcopenshell.entity_instance):
        if not products_:
            return
        products_set = set(products_)

        rels = self.get_constraint_rels(constraint)
        related_objects = set()
        for rel in rels:
            related_objects.update(rel.RelatedObjects)

        if not related_objects.intersection(products_set):
            return

        for rel in rels:
            related_objects = set(rel.RelatedObjects)
            if not related_objects.intersection(products_set):
                continue
            related_objects -= products_set
            if related_objects:
                rel.RelatedObjects = list(related_objects)
                ifcopenshell.api.owner.update_owner_history(self.file, **{"element": rel})
                continue

            history = rel.OwnerHistory
            self.file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(self.file, history)

    def get_constraint_rels(self, cosntraint: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        rels = []
        for rel in self.file.get_inverse(cosntraint):
            if rel.is_a("IfcRelAssociatesConstraint"):
                rels.append(rel)
        return rels
