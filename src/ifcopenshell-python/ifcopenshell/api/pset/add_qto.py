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


def add_qto(file: ifcopenshell.file, product: ifcopenshell.entity_instance, name: str) -> ifcopenshell.entity_instance:
    """Adds a new quantity set to a product

    Products, such as physical objects or types in IFC may have quantities
    associated with them. These quantities are typically simple key value
    metadata with data types. For example, a wall type may have a quantity
    called NetSideArea with a area value of "4.2". Quantities are grouped
    into quantity sets, so that related quantities are grouped together.

    Quantities are similar to, but different from properties in that they
    may store a method of measurement or formula. Quantities may also have
    parametric relationships to other calculated values, such as cost
    schedules, resource utilisation, or construction task durations.

    buildingSMART has come up with a long list of standardised quantities
    for the most common quantities required internationally. This solves the
    age-old question of "what's the standard way of storing quantity
    take-off data"? It is recommended to view the list of standardised
    buildingSMART quantities and see if any suit your needs first. If none
    are appropriate, then you are free to create your own custom quantities.

    This function adds a blank named quantity set. One you have a quantity
    set you may add quantities using ifcopenshell.api.pset.edit_qto.

    See also ifcopenshell.api.pset.add_qto if you want to arbitrary
    metadata, rather than quantification data.

    :param product: The IfcObject that you want to assign a quantity set to.
    :type product: ifcopenshell.entity_instance
    :param name: The name of the quantity set. Quantity sets that are
        standardised by buildingSMART typically have a prefix of "Qto_",
        like "Qto_WallBaseQuantities". If you create your own, you must not
        use that prefix. It is recommended to use your own prefix tailored
        to your project, company, or local government requirement.
    :type name: str
    :return: The newly created IfcElementQuantity
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # Let's imagine we have a new wall.
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # Note that this only creates and assigns an empty quantity set. We
        # still need to add quantities into the property set. Having blank
        # quantity sets are invalid.
        qto = ifcopenshell.api.pset.add_qto(model, product=wall_type, name="Qto_WallBaseQuantities")

        # Add a side area property standardised by buildingSMART. This
        # allows quantity take-off to occur, even though no geometry has
        # even been modelled!
        ifcopenshell.api.pset.edit_qto(model, qto=qto, properties={"NetSideArea": 4.2})
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {"product": product, "name": name}
    return usecase.execute()


class Usecase:
    def execute(self):
        if self.settings["product"].is_a("IfcObject") or self.settings["product"].is_a("IfcContext"):
            for rel in self.settings["product"].IsDefinedBy or []:
                if (
                    rel.is_a("IfcRelDefinesByProperties")
                    and rel.RelatingPropertyDefinition.Name == self.settings["name"]
                ):
                    return rel.RelatingPropertyDefinition

            qto = self.create_qto()
            self.file.create_entity(
                "IfcRelDefinesByProperties",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.owner.create_owner_history(self.file),
                    "RelatedObjects": [self.settings["product"]],
                    "RelatingPropertyDefinition": qto,
                }
            )
            return qto
        elif self.settings["product"].is_a("IfcTypeObject"):
            for definition in self.settings["product"].HasPropertySets or []:
                if definition.Name == self.settings["name"]:
                    return definition
            qto = self.create_qto()
            has_property_sets = list(self.settings["product"].HasPropertySets or [])
            has_property_sets.append(qto)
            self.settings["product"].HasPropertySets = has_property_sets
            return qto

    def create_qto(self):
        return self.file.create_entity(
            "IfcElementQuantity",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.owner.create_owner_history(self.file),
            Name=self.settings["name"],
        )
