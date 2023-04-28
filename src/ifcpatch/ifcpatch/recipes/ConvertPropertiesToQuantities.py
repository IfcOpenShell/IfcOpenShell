# IfcPatch - IFC patching utiliy
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.util.pset
import ifcopenshell.util.element


class Patcher:
    def __init__(self, src, file, logger, property_name=None, quantity_name=None):
        """Converts a property to a standardised quantity

        IFC can store arbitrary key value metadata associated with a elements
        known as properties and quantities. The difference between the two is
        that quantities specifically measure physical dimensions, and can be
        used parametrically. A collection of standardised quantities have also
        been published by buildingSMART. Using standardised quantities can help
        automate BIM workflows, instead of arbitrary properties.

        Sometimes, proprietary BIM software incorrectly stores quantities and
        properties. This patch lets you convert these incorrect properties to
        standardised quantities instead.

        The existing property will not be removed.

        :param property_name: The name of the property to convert into a
            quantity. The name of the property set is not considered.
        :type property_name: str
        :param quantity_name: The name of the quantity that this property should
            be stored in. This should be a standard name that is one of the
            quantity names of a buildingSMART quantity template. For example, it
            may be "NetSideArea" for walls, which exists in
            Qto_WallBaseQuantities. The quantity set name will be based on the
            standard buildingSMART quantity template.
        :type quantity_name: str

        Example:

        .. code:: python

            # Any property named "Area" is converted to a quantity named
            # "NetSideArea", if that standardised quantity exists.
            ifcpatch.execute({"input": model, "recipe": "ConvertPropertiesToQuantities", "arguments": ["Area", "NetSideArea"]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.source_property_name = property_name
        self.destination_quantity_name = quantity_name

    def patch(self):
        self.qto_template_cache = {}
        self.psetqto = ifcopenshell.util.pset.get_template("IFC4")

        for product in self.file.by_type("IfcTypeProduct"):
            self.process_product(product, product.HasPropertySets or [])

        for product in self.file.by_type("IfcProduct"):
            self.process_product(
                product,
                [r.RelatingPropertyDefinition for r in product.IsDefinedBy if r.is_a("IfcRelDefinesByProperties")],
            )

    def process_product(self, product, definitions):
        value = None
        has_quantity = False
        qtos = {}
        for definition in definitions or []:
            if definition.is_a("IfcPropertySet"):
                for prop in definition.HasProperties:
                    if prop.is_a("IfcPropertySingleValue") and prop.Name == self.source_property_name:
                        value = prop.NominalValue.wrappedValue if prop.NominalValue else None
            elif definition.is_a("IfcElementQuantity"):
                qtos[definition.Name] = definition
                for quantity in definition.Quantities:
                    if quantity.is_a("IfcPhysicalSimpleQuantity") and quantity.Name == self.destination_quantity_name:
                        has_quantity = True

        if value and not has_quantity:
            qto_name = self.get_qto_name(product.is_a())
            qto = qtos.get(qto_name, ifcopenshell.api.run("pset.add_qto", self.file, product=product, Name=qto_name))
            ifcopenshell.api.run(
                "pset.edit_qto", self.file, qto=qto, Properties={self.destination_quantity_name: value}
            )

    def get_qto_name(self, ifc_class):
        for template in self.get_qto_templates(ifc_class):
            if self.destination_quantity_name in [t.Name for t in template.HasPropertyTemplates]:
                return template.Name

    def get_qto_templates(self, ifc_class):
        if ifc_class not in self.qto_template_cache:
            self.qto_template_cache[ifc_class] = self.psetqto.get_applicable(ifc_class, qto_only=True)
        return self.qto_template_cache[ifc_class]
