def add_cost_schedule(ifc, predefined_type):
    ifc.run("cost.add_cost_schedule", predefined_type=predefined_type)


def edit_cost_schedule(ifc, cost, cost_schedule):
    attributes = cost.get_cost_schedule_attributes()
    ifc.run("cost.edit_cost_schedule", cost_schedule=cost_schedule, attributes=attributes)
    cost.disable_editing_cost_schedule()


def disable_editing_cost_schedule(cost):
    cost.disable_editing_cost_schedule()


def remove_cost_schedule(ifc, cost_schedule):
    ifc.run("cost.remove_cost_schedule", cost_schedule=cost_schedule)


def enable_editing_cost_schedule_attributes(cost, cost_schedule):
    cost.load_cost_schedule_attributes(cost_schedule)
    cost.enable_editing_cost_schedule_attributes(cost_schedule)

def enable_editing_cost_items(cost, cost_schedule):
    cost.enable_editing_cost_items(cost_schedule)
    cost.load_cost_schedule_tree()
    cost.play_sound()

def add_summary_cost_item(ifc, cost, cost_schedule):
    ifc.run("cost.add_cost_item", cost_schedule=cost_schedule)
    cost.load_cost_schedule_tree()
    # cost.play_sound()

def add_cost_item(ifc, cost, cost_item):
    ifc.run("cost.add_cost_item", cost_item=cost_item)
    cost.load_cost_schedule_tree()
    # cost.enable_editing_cost_schedule_attributes(cost_schedule)


def expand_cost_item(cost, cost_item):
    cost.expand_cost_item(cost_item)
    cost.load_cost_schedule_tree()


def expand_cost_items(cost):
    cost.expand_cost_items()
    cost.load_cost_schedule_tree()


def contract_cost_item(cost, cost_item):
    cost.contract_cost_item(cost_item)
    cost.load_cost_schedule_tree()


def contract_cost_items(cost):
    cost.contract_cost_items()
    cost.load_cost_schedule_tree()


def remove_cost_item(ifc, cost, cost_item):
    ifc.run("cost.remove_cost_item", cost_item=cost_item)
    cost.clean_up_cost_item_tree(cost_item)
    cost.load_cost_schedule_tree()


def enable_editing_cost_item_attributes(cost, cost_item):
    cost.enable_editing_cost_item_attributes(cost_item)
    cost.load_cost_item_attributes(cost_item)


def disable_editing_cost_item(cost):
    cost.disable_editing_cost_item()


def edit_cost_item(ifc, cost):
    attributes = cost.get_cost_item_attributes()
    ifc.run("cost.edit_cost_item", cost_item=cost.get_active_cost_item(), attributes=attributes)
    cost.disable_editing_cost_item()
    cost.load_cost_schedule_tree()


def assign_cost_item_type(ifc, cost, spatial, cost_item, prop_name):
    product_types = spatial.get_selected_product_types()
    [
        ifc.run("control.assign_control", relating_control=cost_item, related_object=product_type)
        for product_type in product_types
    ]
    cost.load_cost_item_types(cost_item)


def unassign_cost_item_type(ifc, cost, spatial, cost_item, product_types):
    if not product_types:
        product_types = spatial.get_selected_product_types()
    [
        ifc.run("control.unassign_control", relating_control=cost_item, related_object=product_type)
        for product_type in product_types
    ]
    cost.load_cost_item_types(cost_item)


def load_cost_item_types(cost):
    cost_item = cost.get_active_cost_item()
    cost.load_cost_item_types(cost_item)


def assign_cost_item_quantity(ifc, cost, cost_item, related_object_type, prop_name):
    products = cost.get_products(related_object_type)
    if products:
        ifc.run("cost.assign_cost_item_quantity", cost_item=cost_item, products=products, prop_name=prop_name)
        cost.load_cost_item_quantity_assignments(cost_item, related_object_type=related_object_type)

def load_cost_item_quantities(cost):
    cost.load_cost_item_quantities()

def load_cost_item_element_quantities(cost):
    cost_item = cost.get_highlighted_cost_item()
    cost.load_cost_item_quantity_assignments(cost_item, related_object_type="PRODUCT")

def load_cost_item_task_quantities(cost):
    cost_item = cost.get_highlighted_cost_item()
    cost.load_cost_item_quantity_assignments(cost_item, related_object_type="PROCESS")

def load_cost_item_resource_quantities(cost):
    cost_item = cost.get_highlighted_cost_item()
    cost.load_cost_item_quantity_assignments(cost_item, related_object_type="RESOURCE")

def assign_cost_value(ifc, cost_item, cost_rate):
    ifc.run("cost.assign_cost_value", cost_item=cost_item, cost_rate=cost_rate)

def load_schedule_of_rates(cost, schedule_of_rates):
    cost.load_schedule_of_rates(schedule_of_rates)

def unassign_cost_item_quantity(ifc, cost, cost_item, products):
    ifc.run("cost.unassign_cost_item_quantity", cost_item=cost_item, products=products)
    cost.load_cost_item_quantities()

def enable_editing_cost_item_quantities(cost, cost_item):
    cost.enable_editing_cost_item_quantities(cost_item)

def enable_editing_cost_item_values(cost, cost_item):
    cost.enable_editing_cost_item_values(cost_item)

def add_cost_item_quantity(ifc, cost_item, ifc_class):
    ifc.run("cost.add_cost_item_quantity", cost_item=cost_item, ifc_class=ifc_class)

def remove_cost_item_quantity(ifc, cost_item, physical_quantity):
    ifc.run("cost.remove_cost_item_quantity", cost_item=cost_item, physical_quantity=physical_quantity)
    
def enable_editing_cost_item_quantity(cost, physical_quantity):
    cost.load_cost_item_quantity_attributes(physical_quantity)
    cost.enable_editing_cost_item_quantity(physical_quantity)

def disable_editing_cost_item_quantity(cost):
    cost.disable_editing_cost_item_quantity()

def edit_cost_item_quantity(ifc, cost, physical_quantity):
    attributes = cost.get_cost_item_quantity_attributes()
    ifc.run("cost.edit_cost_item_quantity", physical_quantity=physical_quantity, attributes=attributes)
    cost.disable_editing_cost_item_quantity()
    cost.load_cost_item_quantities()

def add_cost_value(ifc, cost, parent, cost_type, cost_category):
    value = ifc.run("cost.add_cost_value", parent=parent)
    ifc.run(
        "cost.edit_cost_value",
        cost_value=value,
        attributes=cost.get_attributes_for_cost_value(cost_type, cost_category))

def remove_cost_value(ifc, parent, cost_value):
    ifc.run("cost.remove_cost_value", parent=parent, cost_value=cost_value)

def enable_editing_cost_item_value(cost, cost_value):
    cost.load_cost_item_value_attributes(cost_value)
    cost.enable_editing_cost_item_value(cost_value)

def disable_editing_cost_item_value(cost):
    cost.disable_editing_cost_item_value()

def enable_editing_cost_item_value_formula(cost, cost_value):
    cost.load_cost_item_value_formula_attributes(cost_value)
    cost.enable_editing_cost_item_value_formula(cost_value)

def edit_cost_item_value_formula(ifc, cost, cost_value):
    formula = cost.get_cost_item_value_formula()
    ifc.run("cost.edit_cost_value_formula", cost_value=cost_value, formula=formula)
    cost.disable_editing_cost_item_value()

def edit_cost_value(ifc, cost, cost_value):
    attributes = cost.get_cost_value_attributes()
    ifc.run("cost.edit_cost_value", cost_value=cost_value, attributes=attributes)
    cost.disable_editing_cost_item_value()
    #cost.load_cost_item_values(cost.get_active_cost_item())

def copy_cost_item_values(ifc, cost, source, destination):
    ifc.run("cost.copy_cost_item_values", source=source, destination=destination)

def select_cost_item_products(cost, spatial, cost_item):
    is_deep = cost.show_nested_cost_item_elements()
    products = cost.get_cost_item_products(cost_item, is_deep)
    spatial.select_products(products)

def select_cost_schedule_products(cost, spatial, cost_schedule):
    products = cost.get_cost_schedule_products(cost_schedule)
    spatial.select_products(products)

def import_cost_schedule_csv(cost, file_path, is_schedule_of_rates):
    cost.import_cost_schedule_csv(file_path, is_schedule_of_rates)

def add_cost_column(cost, name):
    cost.add_cost_column(name)

def remove_cost_column(cost, name):
    cost.remove_cost_column(name)

def expand_cost_item_rate(cost, cost_item):
    cost.expand_cost_item_rate(cost_item)

def contract_cost_item_rate(cost, cost_item):
    cost.contract_cost_item_rate(cost_item)

def calculate_cost_item_resource_value(ifc, cost_item):
    ifc.run("cost.calculate_cost_item_resource_value", cost_item=cost_item)

def export_cost_schedules(cost, format):
    cost.export_cost_schedules(format)

def clear_cost_item_assignments(ifc, cost, cost_item, related_object_type):
    products = cost.get_cost_item_assignments(cost_item, filter_by_type=related_object_type)
    if products:
        ifc.run("cost.unassign_cost_item_quantity", cost_item=cost_item, products=products)
    cost.load_cost_item_quantity_assignments(cost_item, related_object_type=related_object_type)
    cost.load_cost_schedule_tree()

def select_unassigned_products(ifc, cost, spatial):
    spatial.deselect_all()
    products = ifc.get().by_type("IfcElement")
    cost_schedule = cost.get_active_cost_schedule()
    selection = [product for product in products if not cost.has_cost_assignments(product, cost_schedule)]
    spatial.select_products(selection)

def load_product_cost_items(cost, product):
    cost.load_product_cost_items(product)

def highlight_product_cost_item(spatial, cost, cost_item):
    cost_schedule = cost.get_cost_schedule(cost_item)
    is_cost_schedule_active = cost.is_cost_schedule_active(cost_schedule)
    if is_cost_schedule_active:
        cost.highlight_cost_item(cost_item)
    else:
        return "Cost schedule is not active"

def toggle_cost_item_parent(cost, cost_item):
    cost.toggle_cost_item_parent(cost_item)

def change_parent_cost_item(ifc, cost, new_parent):
    cost_item = cost.get_active_cost_item()
    if cost_item and cost.is_root_cost_item(cost_item):
        return "Cannot change root cost item"
    if cost_item :
        ifc.run("nest.change_nest", item=cost_item, new_parent=new_parent)
        cost.disable_editing_cost_item_parent()
        cost.load_cost_schedule_tree()