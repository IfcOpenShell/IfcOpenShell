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
    def __init__(self, file, product=None, name=None):
        """Adds a new property set to a product

        Products, such as physical objects or types in IFC may have properties
        associated with them. These properties are typically simple key value
        metadata with data types. For example, a wall type may have a property
        called FireRating with a text value of "2HR". Properties are grouped
        into property sets, so that related properties are grouped together.

        If a property is assigned to a type, the property is inherited by all
        occurrences of that type. For example, a wall type with a FireRating
        property of "2HR" automatically implies that all walls of that wall type
        also have a FireRating of "2HR". It is not necessary to explictly define
        the property again for each occurrence. This also means that properties
        are typically defined on types. If the same property is defined at an
        occurrence, this overrides the property defined on the type.

        buildingSMART has come up with a long list of standardised properties
        for the most common properties required internationally. This solves the
        age-old question of "where do I store my FireRating data for walls"? The
        answer, in this case, is in the "FireRating" property with an "IfcLabel"
        data type grouped in the "Pset_WallCommon" property set. It is
        recommended to view the list of standardised buildingSMART properties
        and see if any suit your needs first. If none are appropriate, then you
        are free to create your own custom properties.

        This function adds a blank named property set. One you have a property
        set you may add properties using ifcopenshell.api.pset.edit_pset.

        See also ifcopenshell.api.pset.add_qto if you want to add quantification
        data, rather than arbitrary metadata.

        :param product: The IfcObject that you want to assign a property set to.
        :type product: ifcopenshell.entity_instance.entity_instance
        :param name: The name of the property set. Property sets that are
            standardised by buildingSMART typically have a prefix of "Pset_",
            like "Pset_WallCommon". If you create your own, you must not use
            that prefix. It is recommended to use your own prefix tailored to
            your project, company, or local government requirement.
        :type name: str
        :return: The newly created IfcPropertySet
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Let's imagine we have a new wall type.
            wall_type = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWallType")

            # Note that this only creates and assigns an empty property set. We
            # still need to add properties into the property set. Having blank
            # property sets are invalid.
            pset = ifcopenshell.api.run("pset.add_pset", model, product=wall_type, name="Pset_WallCommon")

            # Add a fire rating property standardised by buildingSMART.
            ifcopenshell.api.run("pset.edit_pset", model, pset=pset, properties={"FireRating": "2HR"})
        """
        self.file = file
        self.settings = {"product": product, "name": name}

    def execute(self):
        if self.settings["product"].is_a("IfcObject") or self.settings["product"].is_a("IfcContext"):
            for rel in self.settings["product"].IsDefinedBy or []:
                if (
                    rel.is_a("IfcRelDefinesByProperties")
                    and rel.RelatingPropertyDefinition.Name == self.settings["name"]
                ):
                    return rel.RelatingPropertyDefinition

            pset = self.file.create_entity(
                "IfcPropertySet",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "Name": self.settings["name"],
                }
            )
            self.file.create_entity(
                "IfcRelDefinesByProperties",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [self.settings["product"]],
                    "RelatingPropertyDefinition": pset,
                }
            )
            return pset
        elif self.settings["product"].is_a("IfcTypeObject"):
            for definition in self.settings["product"].HasPropertySets or []:
                if definition.Name == self.settings["name"]:
                    return definition

            pset = self.file.create_entity(
                "IfcPropertySet",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "Name": self.settings["name"],
                }
            )
            has_property_sets = list(self.settings["product"].HasPropertySets or [])
            has_property_sets.append(pset)
            self.settings["product"].HasPropertySets = has_property_sets
            return pset
        elif self.settings["product"].is_a("IfcMaterialDefinition"):
            for definition in self.settings["product"].HasProperties or []:
                if definition.Name == self.settings["name"]:
                    return definition

            return self.file.create_entity(
                "IfcMaterialProperties",
                **{
                    "Name": self.settings["name"],
                    "Material": self.settings["product"],
                }
            )
        elif self.settings["product"].is_a("IfcProfileDef"):
            for definition in self.settings["product"].HasProperties or []:
                if definition.Name == self.settings["name"]:
                    return definition

            return self.file.create_entity(
                "IfcProfileProperties",
                **{
                    "Name": self.settings["name"],
                    "ProfileDefinition": self.settings["product"],
                }
            )
