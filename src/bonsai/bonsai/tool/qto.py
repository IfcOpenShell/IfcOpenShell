# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bonsai.core.tool
import bonsai.bim.schema
import bonsai.tool as tool
import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.element
from mathutils import Vector
from typing import Optional, Union, Literal

QuantityTypes = Literal["Q_LENGTH", "Q_AREA", "Q_VOLUME"]


class Qto(bonsai.core.tool.Qto):
    @classmethod
    def get_radius_of_selected_vertices(cls, obj: bpy.types.Object) -> float:
        selected_verts = [v.co for v in obj.data.vertices if v.select]
        total = Vector()
        for v in selected_verts:
            total += v
        circle_center = total / len(selected_verts)
        return max([(v - circle_center).length for v in selected_verts])

    @classmethod
    def set_qto_result(cls, result: float) -> None:
        bpy.context.scene.BIMQtoProperties.qto_result = str(round(result, 3))

    @classmethod
    def get_rounded_value(cls, new_quantity: float) -> float:
        return round(new_quantity, 3)

    @classmethod
    def convert_to_project_units(
        cls,
        value: float,
        qto_name: Optional[str] = None,
        quantity_name: Optional[str] = None,
        quantity_type: Optional[QuantityTypes] = None,
    ) -> Union[float, None]:
        """You can either specify `quantity_type` or provide `qto_name/quantity_name`
        to let method figure the `quantity_type` from the templates
        """
        ifc_file = tool.Ifc.get()
        quantity_to_unit_types = {
            "Q_LENGTH": ("LENGTHUNIT", "METRE"),
            "Q_AREA": ("AREAUNIT", "SQUARE_METRE"),
            "Q_VOLUME": ("VOLUMEUNIT", "CUBIC_METRE"),
        }
        if not quantity_type:
            qt = bonsai.bim.schema.ifc.psetqto.get_by_name(qto_name)
            quantity_type = next(q.TemplateType for q in qt.HasPropertyTemplates if q.Name == quantity_name)

        unit_type = quantity_to_unit_types.get(quantity_type, None)
        if not unit_type:
            return

        unit_type, base_unit = unit_type
        project_unit = ifcopenshell.util.unit.get_project_unit(ifc_file, unit_type)
        if not project_unit:
            return
        value = ifcopenshell.util.unit.convert(
            value,
            from_prefix=None,
            from_unit=base_unit,
            to_prefix=getattr(project_unit, "Prefix", None),
            to_unit=project_unit.Name,
        )
        return value

    @classmethod
    def get_base_qto(cls, product: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        if not hasattr(product, "IsDefinedBy"):
            return
        base_qto_definition = None
        base_qto_definition_name: Union[str, None] = None
        for rel in product.IsDefinedBy or []:
            definition = rel.RelatingPropertyDefinition
            if not rel.is_a("IfcRelDefinesByProperties"):
                continue
            definition = rel.RelatingPropertyDefinition
            definition_name = definition.Name
            if "Qto_" not in definition_name:
                continue
            if "Base" in definition_name:
                return definition
            if base_qto_definition and "BodyGeometryValidation" not in base_qto_definition_name:
                continue
            base_qto_definition = definition
            base_qto_definition_name = definition_name
        return base_qto_definition

    @classmethod
    def get_related_cost_item_quantities(cls, product: ifcopenshell.entity_instance) -> list[dict]:
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
        :rtype: list

        Example:

        .. code::Python
        import bonsai.tool as tool

        relating_cost_items = tool.Qto.relating_cost_items(my_beautiful_wall)
        for relating_cost_item in relating_cost_items:
            print(f"RELATING COST ITEM NAME: {relating_cost_item["cost_item_name"]}")
            print(f"RELATING COST QUANTITY NAME: {relating_cost_item["quantity_name"]}")
            ...
        """
        model = tool.Ifc.get()
        cost_items = model.by_type("IfcCostItem")
        result = []
        base_qto = cls.get_base_qto(product)
        quantities = base_qto.Quantities if base_qto else []

        for cost_item in cost_items:
            cost_item_quantities = cost_item.CostQuantities if cost_item.CostQuantities is not None else []
            for cost_item_quantity in cost_item_quantities:
                for quantity in quantities:
                    if quantity == cost_item_quantity:
                        result.append(
                            {
                                "cost_item_id": cost_item.id(),
                                "cost_item_name": cost_item.Name,
                                "quantity_id": quantity.id(),
                                "quantity_name": quantity.Name,
                                "quantity_value": quantity[3],
                                "quantity_type": quantity.is_a(),
                            }
                        )
        return result
