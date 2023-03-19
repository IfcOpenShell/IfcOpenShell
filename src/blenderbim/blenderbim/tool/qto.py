# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

from types import ClassMethodDescriptorType
import bpy
import blenderbim.core.tool
import blenderbim.tool as tool
import ifcopenshell
from mathutils import Vector
from ifcopenshell import util
from blenderbim.bim.module.pset.qto_calculator import QtoCalculator
from blenderbim.bim.module.pset.calc_quantity_function_mapper import mapper
import blenderbim.bim.schema


class Qto(blenderbim.core.tool.Qto):
    @classmethod
    def get_radius_of_selected_vertices(cls, obj):
        selected_verts = [v.co for v in obj.data.vertices if v.select]
        total = Vector()
        for v in selected_verts:
            total += v
        circle_center = total / len(selected_verts)
        return max([(v - circle_center).length for v in selected_verts])

    @classmethod
    def set_qto_result(cls, result):
        bpy.context.scene.BIMQtoProperties.qto_result = str(round(result, 3))

    @classmethod
    def add_object_base_qto(cls, obj):
        product = tool.Ifc.get_entity(obj)
        return cls.add_product_base_qto(product)

    @classmethod
    def add_product_base_qto(cls, product):
        base_quantity_name = cls.get_applicable_base_quantity_name(product)
        if base_quantity_name:
            return tool.Ifc.run(
                "pset.add_qto",
                product=product,
                name=base_quantity_name,
            )

    @classmethod
    def get_applicable_quantity_names(cls, qto_name):
        pset_template = blenderbim.bim.schema.ifc.psetqto.get_by_name(qto_name)
        return (
            [property.Name for property in pset_template.HasPropertyTemplates]
            if hasattr(pset_template, "HasPropertyTemplates")
            else []
        )

    @classmethod
    def get_applicable_base_quantity_name(cls, product=None):
        if not product:
            return
        applicable_qto_names = blenderbim.bim.schema.ifc.psetqto.get_applicable_names(product.is_a(), qto_only=True)
        return next((qto_name for qto_name in applicable_qto_names if "Qto_" in qto_name and "Base" in qto_name), None)

    @classmethod
    def get_new_calculated_quantity(cls, qto_name, quantity_name, obj):
        return QtoCalculator().calculate_quantity(qto_name, quantity_name, obj)

    @classmethod
    def get_new_guessed_quantity(cls, obj, quantity_name, alternative_prop_names):
        return QtoCalculator().guess_quantity(quantity_name, alternative_prop_names, obj)

    @classmethod
    def get_rounded_value(cls, new_quantity):
        return round(new_quantity, 3)

    @classmethod
    def get_calculated_object_quantities(cls, calculator, qto_name, obj):
        return {
            quantity_name: cls.get_rounded_value(calculator.calculate_quantity(qto_name, quantity_name, obj))
            for quantity_name in cls.get_applicable_quantity_names(qto_name) or []
            if cls.has_calculator(qto_name, quantity_name) and calculator.calculate_quantity(qto_name, quantity_name, obj) is not None
        }

    @classmethod
    def has_calculator(cls, qto_name, quantity_name):
        return bool(mapper.get(qto_name, {}).get(quantity_name, None))

    @classmethod
    def get_guessed_quantities(cls, obj, pset_qto_properties):
        calculated_quantities = {}
        for pset_qto_property in pset_qto_properties:
            quantity_name = pset_qto_property.get_info()["Name"]
            alternative_prop_names = [p.get_info()["Name"] for p in pset_qto_properties]

            new_quantity = cls.get_new_guessed_quantity(obj, quantity_name, alternative_prop_names)

            if not new_quantity:
                new_quantity = 0
            else:
                new_quantity = cls.get_rounded_value(new_quantity)

            calculated_quantities[quantity_name] = new_quantity

        return calculated_quantities

    @classmethod
    def get_base_qto(cls, product):
        if not hasattr(product, "IsDefinedBy"):
            return
        for rel in product.IsDefinedBy or []:
            if not (
                rel.is_a("IfcRelDefinesByProperties")
                and "Base" in rel.RelatingPropertyDefinition.Name
                and "Qto_" in rel.RelatingPropertyDefinition.Name
            ):
                continue
            return rel.RelatingPropertyDefinition

    @classmethod
    def get_related_cost_item_quantities(cls, product):
        """_summary_: Returns the related cost item and related quantities of the product

        :param ifc-instance product: ifc instance
        :type product: ifcopenshell.entity_instance.entity_instance

        :return list of dictionaries in the form [
        {
        "cost_item_id" : XX,
        "cost_item_name" : XX,
        "quantity_id" : XX,
        "quantity_name" : XX,
        "quantity_value" : XX,
        "quantity_type" : XX
        }]
        :rtype list

        Example:

        .. code::Python
        import blenderbim.tool as tool

        relating_cost_items = tool.Qto.relating_cost_items(my_beautiful_wall)
        for relating_cost_item in relating_cost_items:
            print(f"RELATING COST ITEM NAME: {relating_cost_item["cost_item_name"]}")
            print(f"RELATING COST QUANTITY NAME: {relating_cost_item["quantity_name"]}")
            ...
        """
        quantities = cls.get_base_qto(product).Quantities
        model = tool.Ifc.get()
        cost_items = model.by_type("IfcCostItem")
        result = []

        for cost_item in cost_items:
            cost_item_quantities = cost_item.CostQuantities if cost_item.CostQuantities is not None else []
            for cost_item_quantity in cost_item_quantities:
                for quantity in quantities:
                    if quantity == cost_item_quantity:
                        result.append(
                            {
                                "cost_item_id" : cost_item.id(),
                                "cost_item_name" : cost_item.Name,
                                "quantity_id" : quantity.id(),
                                "quantity_name" : quantity.Name,
                                "quantity_value" : quantity[3],
                                "quantity_type" : quantity.is_a(),
                            }
                        )
        return result
