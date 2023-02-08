def add_cost_schedule(ifc):
    ifc.run("cost.add_cost_schedule")

def edit_cost_schedule(ifc, cost, cost_schedule):
    attributes = cost.get_cost_schedule_attributes()
    ifc.run("cost.edit_cost_schedule", cost_schedule=cost_schedule, attributes=attributes)
    cost.disable_editing_cost_schedule()

def disable_editing_cost_schedule(cost):
    cost.disable_editing_cost_schedule()

def remove_cost_schedule(ifc, cost_schedule):
    ifc.run("cost.remove_cost_schedule", cost_schedule=cost_schedule)

def enable_editing_cost_schedule_attributes(cost, cost_schedule):
    cost.enable_editing_cost_schedule_attributes(cost_schedule)
    cost.load_cost_items()
    cost.play_chaching_sound()

def enable_editing_cost_items(cost, cost_schedule):
    cost.enable_editing_cost_items(cost_schedule)
    cost.load_cost_items()

def add_summary_cost_item(ifc, cost, cost_schedule):
    ifc.run("cost.add_cost_item", cost_schedule=cost_schedule)
    cost.load_cost_items()

def add_cost_item(ifc, cost, cost_item):
    ifc.run("cost.add_cost_item", cost_item=cost_item)
    cost.load_cost_items()
    # cost.enable_editing_cost_schedule_attributes(cost_schedule)

def expand_cost_item(cost, cost_item):
    cost.expand_cost_item(cost_item)
    cost.load_cost_items()

def expand_cost_items(cost):
    cost.expand_cost_items()
    cost.load_cost_items()

def contract_cost_item(cost, cost_item):
    cost.contract_cost_item(cost_item)
    cost.load_cost_items()

def contract_cost_items(cost):
    cost.contract_cost_items()
    cost.load_cost_items()

def remove_cost_item(ifc, cost, cost_item):
    ifc.run("cost.remove_cost_item", cost_item=cost_item)
    cost.clean_up_cost_item_tree(cost_item)
    cost.load_cost_items()

def enable_editing_cost_item_attributes(cost, cost_item):
    cost.enable_editing_cost_item_attributes(cost_item)
    cost.load_cost_item_attributes(cost_item)

def disable_editing_cost_item(cost):
    cost.disable_editing_cost_item()

def edit_cost_item(ifc, cost):
    attributes = cost.get_cost_item_attributes()
    ifc.run("cost.edit_cost_item", cost_item=cost.get_active_cost_item(), attributes=attributes)
    cost.disable_editing_cost_item()
    cost.load_cost_items()