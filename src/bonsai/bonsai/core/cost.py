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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union, Literal

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import ifcopenshell.util.cost
    import bonsai.tool as tool


def add_cost_schedule(ifc: tool.Ifc, name: str, predefined_type: str) -> None:
    ifc.run("cost.add_cost_schedule", name=name, predefined_type=predefined_type)


def edit_cost_schedule(ifc: tool.Ifc, cost: tool.Cost, cost_schedule: ifcopenshell.entity_instance) -> None:
    attributes = cost.get_cost_schedule_attributes()
    ifc.run("cost.edit_cost_schedule", cost_schedule=cost_schedule, attributes=attributes)
    cost.disable_editing_cost_schedule()


def disable_editing_cost_schedule(cost: tool.Cost) -> None:
    cost.disable_editing_cost_schedule()


def remove_cost_schedule(ifc: tool.Ifc, cost: tool.Cost, cost_schedule: ifcopenshell.entity_instance) -> None:
    cost.remove_stored_schedule_columns(cost_schedule)
    ifc.run("cost.remove_cost_schedule", cost_schedule=cost_schedule)


def enable_editing_cost_schedule_attributes(cost: tool.Cost, cost_schedule: ifcopenshell.entity_instance) -> None:
    cost.load_cost_schedule_attributes(cost_schedule)
    cost.enable_editing_cost_schedule_attributes(cost_schedule)


def enable_editing_cost_items(cost: tool.Cost, cost_schedule: ifcopenshell.entity_instance) -> None:
    cost.enable_editing_cost_items(cost_schedule)
    cost.load_active_schedule_columns()
    cost.load_cost_schedule_tree()
    cost.play_sound()


def add_summary_cost_item(ifc: tool.Ifc, cost: tool.Cost, cost_schedule: ifcopenshell.entity_instance) -> None:
    ifc.run("cost.add_cost_item", cost_schedule=cost_schedule)
    cost.load_cost_schedule_tree()
    # cost.play_sound()


def add_cost_item(ifc: tool.Ifc, cost: tool.Cost, cost_item: ifcopenshell.entity_instance) -> None:
    ifc.run("cost.add_cost_item", cost_item=cost_item)
    cost.load_cost_schedule_tree()
    # cost.enable_editing_cost_schedule_attributes(cost_schedule)


def expand_cost_item(cost: tool.Cost, cost_item: ifcopenshell.entity_instance) -> None:
    cost.expand_cost_item(cost_item)
    cost.load_cost_schedule_tree()


def expand_cost_items(cost: tool.Cost) -> None:
    cost.expand_cost_items()
    cost.load_cost_schedule_tree()


def contract_cost_item(cost: tool.Cost, cost_item: ifcopenshell.entity_instance) -> None:
    cost.contract_cost_item(cost_item)
    cost.load_cost_schedule_tree()


def contract_cost_items(cost: tool.Cost) -> None:
    cost.contract_cost_items()
    cost.load_cost_schedule_tree()


def remove_cost_item(ifc: tool.Ifc, cost: tool.Cost, cost_item_id: int) -> None:
    cost_item = ifc.get().by_id(cost_item_id)
    ifc.run("cost.remove_cost_item", cost_item=cost_item)
    cost.clean_up_cost_item_tree(cost_item_id)
    cost.load_cost_schedule_tree()


def enable_editing_cost_item_attributes(cost: tool.Cost, cost_item: ifcopenshell.entity_instance) -> None:
    cost.enable_editing_cost_item_attributes(cost_item)
    cost.load_cost_item_attributes(cost_item)


def disable_editing_cost_item(cost: tool.Cost) -> None:
    cost.disable_editing_cost_item()


def edit_cost_item(ifc: tool.Ifc, cost: tool.Cost) -> None:
    attributes = cost.get_cost_item_attributes()
    ifc.run("cost.edit_cost_item", cost_item=cost.get_active_cost_item(), attributes=attributes)
    cost.disable_editing_cost_item()
    cost.load_cost_schedule_tree()


def assign_cost_item_type(
    ifc: tool.Ifc, cost: tool.Cost, spatial: tool.Spatial, cost_item: ifcopenshell.entity_instance, prop_name
) -> list[ifcopenshell.entity_instance]:
    """
    Returns:
        List of found product types.
    """
    product_types = list(spatial.get_selected_product_types())
    rels = [
        ifc.run("control.assign_control", relating_control=cost_item, related_object=product_type)
        for product_type in product_types
    ]
    cost.load_cost_item_types(cost_item)
    return product_types


def unassign_cost_item_type(
    ifc: tool.Ifc,
    cost: tool.Cost,
    spatial: tool.Spatial,
    cost_item: ifcopenshell.entity_instance,
    product_types: Optional[list[ifcopenshell.entity_instance]] = None,
) -> list[ifcopenshell.entity_instance]:
    """
    Returns:
        List of found product types.
    """
    if not product_types:
        product_types = list(spatial.get_selected_product_types())
    [
        ifc.run("control.unassign_control", relating_control=cost_item, related_object=product_type)
        for product_type in product_types
    ]
    cost.load_cost_item_types(cost_item)
    return product_types


def load_cost_item_types(cost: tool.Cost) -> None:
    cost_item = cost.get_active_cost_item()
    cost.load_cost_item_types(cost_item)


def assign_cost_item_quantity(
    ifc: tool.Ifc,
    cost: tool.Cost,
    cost_item: ifcopenshell.entity_instance,
    related_object_type: tool.Cost.RELATED_OBJECT_TYPE,
    prop_name: str,
) -> None:
    products = cost.get_products(related_object_type)
    if products:
        ifc.run("cost.assign_cost_item_quantity", cost_item=cost_item, products=products, prop_name=prop_name)
        cost.load_cost_item_quantity_assignments(cost_item, related_object_type=related_object_type)


def load_cost_item_quantities(cost: tool.Cost) -> None:
    cost.load_cost_item_quantities()


def load_cost_item_element_quantities(cost: tool.Cost) -> None:
    cost_item = cost.get_highlighted_cost_item()
    cost.load_cost_item_quantity_assignments(cost_item, related_object_type="PRODUCT")


def load_cost_item_task_quantities(cost: tool.Cost) -> None:
    cost_item = cost.get_highlighted_cost_item()
    cost.load_cost_item_quantity_assignments(cost_item, related_object_type="PROCESS")


def load_cost_item_resource_quantities(cost: tool.Cost) -> None:
    cost_item = cost.get_highlighted_cost_item()
    cost.load_cost_item_quantity_assignments(cost_item, related_object_type="RESOURCE")


def assign_cost_value(
    ifc: tool.Ifc, cost_item: ifcopenshell.entity_instance, cost_rate: ifcopenshell.entity_instance
) -> None:
    ifc.run("cost.assign_cost_value", cost_item=cost_item, cost_rate=cost_rate)


def load_schedule_of_rates(cost: tool.Cost, schedule_of_rates: ifcopenshell.entity_instance) -> None:
    cost.load_schedule_of_rates_tree(schedule_of_rates)


def unassign_cost_item_quantity(
    ifc: tool.Ifc,
    cost: tool.Cost,
    cost_item: ifcopenshell.entity_instance,
    products: list[ifcopenshell.entity_instance],
) -> None:
    ifc.run("cost.unassign_cost_item_quantity", cost_item=cost_item, products=products)
    cost.load_cost_item_quantities()


def enable_editing_cost_item_quantities(cost: tool.Cost, cost_item: ifcopenshell.entity_instance) -> None:
    cost.enable_editing_cost_item_quantities(cost_item)


def enable_editing_cost_item_values(cost: tool.Cost, cost_item: ifcopenshell.entity_instance) -> None:
    cost.enable_editing_cost_item_values(cost_item)


def add_cost_item_quantity(ifc: tool.Ifc, cost_item: ifcopenshell.entity_instance, ifc_class: str) -> None:
    ifc.run("cost.add_cost_item_quantity", cost_item=cost_item, ifc_class=ifc_class)


def remove_cost_item_quantity(
    ifc: tool.Ifc, cost_item: ifcopenshell.entity_instance, physical_quantity: ifcopenshell.entity_instance
) -> None:
    ifc.run("cost.remove_cost_item_quantity", cost_item=cost_item, physical_quantity=physical_quantity)


def enable_editing_cost_item_quantity(cost: tool.Cost, physical_quantity: ifcopenshell.entity_instance) -> None:
    cost.load_cost_item_quantity_attributes(physical_quantity)
    cost.enable_editing_cost_item_quantity(physical_quantity)


def disable_editing_cost_item_quantity(cost: tool.Cost) -> None:
    cost.disable_editing_cost_item_quantity()


def edit_cost_item_quantity(ifc: tool.Ifc, cost: tool.Cost, physical_quantity: ifcopenshell.entity_instance) -> None:
    attributes = cost.get_cost_item_quantity_attributes()
    ifc.run("cost.edit_cost_item_quantity", physical_quantity=physical_quantity, attributes=attributes)
    cost.disable_editing_cost_item_quantity()
    cost.load_cost_item_quantities()


def add_cost_value(
    ifc: tool.Ifc,
    cost: tool.Cost,
    parent: ifcopenshell.entity_instance,
    cost_type: Literal["FIXED", "SUM", "CATEGORY"],
    cost_category: Optional[str] = None,
) -> None:
    value = ifc.run("cost.add_cost_value", parent=parent)
    ifc.run(
        "cost.edit_cost_value",
        cost_value=value,
        attributes=cost.get_attributes_for_cost_value(cost_type, cost_category),
    )


def remove_cost_value(
    ifc: tool.Ifc, parent: ifcopenshell.entity_instance, cost_value: ifcopenshell.entity_instance
) -> None:
    ifc.run("cost.remove_cost_value", parent=parent, cost_value=cost_value)


def enable_editing_cost_item_value(cost: tool.Cost, cost_value: ifcopenshell.entity_instance) -> None:
    cost.load_cost_item_value_attributes(cost_value)
    cost.enable_editing_cost_item_value(cost_value)


def disable_editing_cost_item_value(cost: tool.Cost) -> None:
    cost.disable_editing_cost_item_value()


def enable_editing_cost_item_value_formula(cost: tool.Cost, cost_value: ifcopenshell.entity_instance) -> None:
    cost.load_cost_item_value_formula_attributes(cost_value)
    cost.enable_editing_cost_item_value_formula(cost_value)


def edit_cost_item_value_formula(ifc: tool.Ifc, cost: tool.Cost, cost_value: ifcopenshell.entity_instance) -> None:
    formula = cost.get_cost_item_value_formula()
    ifc.run("cost.edit_cost_value_formula", cost_value=cost_value, formula=formula)
    cost.disable_editing_cost_item_value()


def edit_cost_value(ifc: tool.Ifc, cost: tool.Cost, cost_value: ifcopenshell.entity_instance) -> None:
    attributes = cost.get_cost_value_attributes()
    ifc.run("cost.edit_cost_value", cost_value=cost_value, attributes=attributes)
    cost.disable_editing_cost_item_value()
    # cost.load_cost_item_values(cost.get_highlighted_cost_item())


def copy_cost_item_values(
    ifc: tool.Ifc, cost: tool.Cost, source: ifcopenshell.entity_instance, destination: ifcopenshell.entity_instance
) -> None:
    ifc.run("cost.copy_cost_item_values", source=source, destination=destination)


def select_cost_item_products(cost: tool.Cost, spatial: tool.Spatial, cost_item: ifcopenshell.entity_instance) -> None:
    is_deep = cost.show_nested_cost_item_elements()
    products = cost.get_cost_item_products(cost_item, is_deep)
    spatial.select_products(products)


def select_cost_schedule_products(
    cost: tool.Cost, spatial: tool.Spatial, cost_schedule: ifcopenshell.entity_instance
) -> None:
    products = cost.get_cost_schedule_products(cost_schedule)
    spatial.select_products(products)


def import_cost_schedule_csv(cost: tool.Cost, file_path: str, is_schedule_of_rates: bool) -> None:
    cost.import_cost_schedule_csv(file_path, is_schedule_of_rates)


def add_cost_column(cost: tool.Cost, name: str) -> None:
    cost.add_cost_column(name)


def remove_cost_column(cost: tool.Cost, name: str) -> None:
    cost.remove_cost_column(name)


def expand_cost_item_rate(cost: tool.Cost, cost_item: ifcopenshell.entity_instance) -> None:
    cost.expand_cost_item_rate(cost_item)


def contract_cost_item_rate(cost: tool.Cost, cost_item: ifcopenshell.entity_instance) -> None:
    cost.contract_cost_item_rate(cost_item)


def calculate_cost_item_resource_value(ifc: tool.Ifc, cost_item: ifcopenshell.entity_instance) -> None:
    ifc.run("cost.calculate_cost_item_resource_value", cost_item=cost_item)


def export_cost_schedules(
    cost: tool.Cost, filepath: str, format: str, cost_schedule: Union[ifcopenshell.entity_instance, None] = None
) -> Union[str, None]:
    cost.play_sound()
    return cost.export_cost_schedules(filepath, format, cost_schedule)


def clear_cost_item_assignments(
    ifc: tool.Ifc,
    cost: tool.Cost,
    cost_item: ifcopenshell.entity_instance,
    related_object_type: ifcopenshell.util.cost.FILTER_BY_TYPE,
) -> None:
    products = cost.get_cost_item_assignments(cost_item, filter_by_type=related_object_type)
    if products:
        ifc.run("cost.unassign_cost_item_quantity", cost_item=cost_item, products=products)
    cost.load_cost_item_quantity_assignments(cost_item, related_object_type=related_object_type)
    cost.load_cost_schedule_tree()


def select_unassigned_products(ifc: tool.Ifc, cost: tool.Cost, spatial: tool.Spatial) -> None:
    spatial.deselect_objects()
    products = ifc.get().by_type("IfcElement")
    cost_schedule = cost.get_active_cost_schedule()
    selection = [product for product in products if not cost.has_cost_assignments(product, cost_schedule)]
    spatial.select_products(selection)


def load_product_cost_items(cost: tool.Cost, product: ifcopenshell.entity_instance) -> None:
    cost.load_product_cost_items(product)


def highlight_product_cost_item(
    spatial: tool.Spatial, cost: tool.Cost, cost_item: ifcopenshell.entity_instance
) -> Union[str, None]:
    cost_schedule = cost.get_cost_schedule(cost_item)
    is_cost_schedule_active = cost.is_cost_schedule_active(cost_schedule)
    if is_cost_schedule_active:
        cost.highlight_cost_item(cost_item)
    else:
        return "Cost schedule is not active"


def change_parent_cost_item(ifc: tool.Ifc, cost: tool.Cost, new_parent) -> Union[str, None]:
    cost_item = cost.get_active_cost_item()
    if cost_item and cost.is_root_cost_item(cost_item):
        return "Cannot change root cost item"
    if cost_item:
        ifc.run("nest.change_nest", item=cost_item, new_parent=new_parent)
        cost.disable_editing_cost_item_parent()
        cost.load_cost_schedule_tree()


def copy_cost_item(ifc: tool.Ifc, cost: tool.Cost) -> None:
    cost_item = cost.get_highlighted_cost_item()
    if cost_item:
        cost_item = ifc.run("cost.copy_cost_item", cost_item=cost_item)
        cost.disable_editing_cost_item_parent()
        cost.load_cost_schedule_tree()


def add_currency(ifc: tool.Ifc, cost: tool.Cost) -> ifcopenshell.entity_instance:
    unit = ifc.run("unit.add_monetary_unit")
    attributes = cost.get_currency_attributes()
    ifc.run("unit.edit_monetary_unit", unit=unit, attributes=attributes)
    ifc.run("unit.assign_unit", units=[unit])
    return unit


def generate_cost_schedule_browser(cost: tool.Cost, cost_schedule: ifcopenshell.entity_instance) -> bpy.types.Panel:
    return cost.generate_cost_schedule_browser(cost_schedule)
