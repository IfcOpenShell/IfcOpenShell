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
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        self.qto_template_cache = {}
        self.psetqto = ifcopenshell.util.pset.get_template("IFC4")

        self.source_property_name = self.args[0]
        self.destination_quantity_name = self.args[1]

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
