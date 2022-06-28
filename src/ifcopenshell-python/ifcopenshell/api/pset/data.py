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
import ifcopenshell.util.attribute
import ifcopenshell.util.pset


class Data:
    products = {}
    psets = {}
    qtos = {}
    properties = {}

    @classmethod
    def purge(cls):
        cls.products = {}
        cls.psets = {}
        cls.qtos = {}
        cls.properties = {}

    @classmethod
    def load(cls, file, product_id):
        if not file:
            return
        product = file.by_id(product_id)
        cls.products[product_id] = {"psets": set(), "qtos": set()}
        if product.is_a("IfcTypeObject"):
            cls.add_type_product_psets(product, product_id)
        elif product.is_a("IfcMaterialDefinition"):
            cls.add_material_psets(product, product_id)
        elif product.is_a("IfcProfileDef"):
            cls.add_profile_psets(product, product_id)
        else:
            cls.add_product_psets(product, product_id)

    @classmethod
    def add_type_product_psets(cls, product, product_id):
        if not hasattr(product, "HasPropertySets") or not product.HasPropertySets:
            return  # TODO
        for definition in product.HasPropertySets:
            if definition.is_a("IfcPropertySet"):
                cls.add_pset(definition, product_id)

    @classmethod
    def add_material_psets(cls, product, product_id):
        if not product.HasProperties:
            return
        for pset in product.HasProperties:
            cls.add_pset(pset, product_id)

    @classmethod
    def add_profile_psets(cls, product, product_id):
        if not product.HasProperties:
            return
        for pset in product.HasProperties:
            cls.add_pset(pset, product_id)

    @classmethod
    def add_product_psets(cls, product, product_id):
        if not hasattr(product, "IsDefinedBy") or not product.IsDefinedBy:
            return
        for definition in product.IsDefinedBy:
            if not definition.is_a("IfcRelDefinesByProperties"):
                continue
            if definition.RelatingPropertyDefinition.is_a("IfcPropertySet"):
                cls.add_pset(definition.RelatingPropertyDefinition, product_id)
            elif definition.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                cls.add_qto(definition.RelatingPropertyDefinition, product_id)

    @classmethod
    def add_pset(cls, pset, product_id):
        data = pset.get_info()
        if not pset.is_a("IfcMaterialProperties") and not pset.is_a("IfcProfileProperties"):
            del data["OwnerHistory"]
            del data["HasProperties"]
        if hasattr(pset, "HasProperties"):
            props = pset.HasProperties or []
        elif hasattr(pset, "Properties"):
            props = pset.Properties or []
        # TODO: support more than single values
        data["Properties"] = [p.id() for p in props if p.is_a("IfcPropertyEnumeratedValue") or p.is_a("IfcPropertySingleValue")]
        cls.psets[pset.id()] = data
        cls.products[product_id]["psets"].add(pset.id())
        for prop in props:
            # TODO: support more than single values
            if prop.is_a("IfcPropertySingleValue"):
                cls.load_prop(prop)
            elif prop.is_a("IfcPropertyEnumeratedValue"):
                cls.load_prop_enum(prop)

    @classmethod
    def load_prop(cls, prop):
        data = prop.get_info()
        if prop.is_a("IfcProperty"):
            # TODO: support units
            del data["Unit"]
            if prop.NominalValue is not None:
                data["NominalValue"] = prop.NominalValue.wrappedValue
        elif prop.is_a("IfcPhysicalQuantity"):
            # TODO: support units
            del data["Unit"]
            # For convenience, which trumps correctness in this case
            data["NominalValue"] = prop[3]
        cls.properties[prop.id()] = data
        
    @classmethod
    def load_prop_enum(cls, prop):
        data = prop.get_info()
        enumerations = [enum.wrappedValue for enum in data["EnumerationValues"]]
        data["NominalValue"] = str(enumerations)
        cls.properties[prop.id()] = data
        
    @classmethod
    def add_qto(cls, qto, product_id):
        data = qto.get_info()
        del data["OwnerHistory"]
        del data["Quantities"]
        # TODO: support more than just simple quantities
        # We call it properties for convenience, not for correctness
        data["Properties"] = [q.id() for q in qto.Quantities or [] if q.is_a("IfcPhysicalSimpleQuantity")]
        cls.qtos[qto.id()] = data
        cls.products[product_id]["qtos"].add(qto.id())
        for quantity in qto.Quantities or []:
            if quantity.is_a("IfcPhysicalSimpleQuantity"):
                cls.load_prop(quantity)
