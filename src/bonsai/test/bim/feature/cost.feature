@cost
Feature: Cost

Scenario: Add cost schedule
    Given an empty IFC project
    And I set "scene.BIMCostProperties.cost_schedule_predefined_types" to "COSTPLAN"
    When I press "bim.add_cost_schedule"
    Then nothing happens

Scenario: Enable editing cost schedule
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    When I press "bim.enable_editing_cost_schedule_attributes(cost_schedule={cost_schedule})"
    Then nothing happens

Scenario: Disable editing cost schedule
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_schedule_attributes(cost_schedule={cost_schedule})"
    When I press "bim.disable_editing_cost_schedule"
    Then nothing happens

Scenario: Edit cost schedule
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_schedule_attributes(cost_schedule={cost_schedule})"
    When I press "bim.edit_cost_schedule"
    Then nothing happens

Scenario: Remove cost schedule
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    When I press "bim.remove_cost_schedule(cost_schedule={cost_schedule})"
    Then nothing happens

Scenario: Enable editing cost items
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    When I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    Then nothing happens

Scenario: Disable editing cost schedule - after editing items
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    When I press "bim.disable_editing_cost_schedule"
    Then nothing happens

Scenario: Add summary cost item
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    When I press "bim.add_summary_cost_item()"
    Then nothing happens

Scenario: Remove cost item
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    When I press "bim.remove_cost_item(cost_item={cost_item})"
    Then nothing happens

Scenario: Enable editing cost item
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    When I press "bim.enable_editing_cost_item_attributes(cost_item={cost_item})"
    Then nothing happens

Scenario: Disable editing cost item
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I press "bim.enable_editing_cost_item_attributes(cost_item={cost_item})"
    When I press "bim.disable_editing_cost_item"
    Then nothing happens

Scenario: Edit cost item
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I press "bim.enable_editing_cost_item_attributes(cost_item={cost_item})"
    When I press "bim.edit_cost_item"
    Then nothing happens

Scenario: Add cost item
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    When I press "bim.add_cost_item(cost_item={cost_item})"
    Then nothing happens

Scenario: Contract Cost Item
    Given an empty IFC project
    And I set "scene.BIMCostProperties.cost_schedule_predefined_types" to "COSTPLAN"
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And I press "bim.add_cost_item(cost_item={cost_item})"
    When I press "bim.contract_cost_item(cost_item={cost_item})"
    Then nothing happens

Scenario: Contract All Cost Items
    Given an empty IFC project
    And I set "scene.BIMCostProperties.cost_schedule_predefined_types" to "COSTPLAN"
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And I press "bim.add_cost_item(cost_item={cost_item})"
    When I press "bim.contract_cost_items"
    Then nothing happens

Scenario: Expand Cost Item
    Given an empty IFC project
    And I set "scene.BIMCostProperties.cost_schedule_predefined_types" to "COSTPLAN"
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And I press "bim.add_cost_item(cost_item={cost_item})"
    And I press "bim.contract_cost_item(cost_item={cost_item})"
    When I press "bim.expand_cost_item(cost_item={cost_item})"
    Then nothing happens


Scenario: Expand All Cost Items
    Given an empty IFC project
    And I set "scene.BIMCostProperties.cost_schedule_predefined_types" to "COSTPLAN"
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And I press "bim.add_cost_item(cost_item={cost_item})"
    When I press "bim.expand_cost_items"
    Then nothing happens


Scenario: Enable editing cost item quantities
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    When I press "bim.enable_editing_cost_item_quantities(cost_item={cost_item})"
    Then nothing happens

Scenario: Add cost item quantity
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I press "bim.enable_editing_cost_item_quantities(cost_item={cost_item})"
    When I press "bim.add_cost_item_quantity(cost_item={cost_item}, ifc_class='IfcQuantityArea')"
    Then nothing happens

Scenario: Remove cost item quantity
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I press "bim.enable_editing_cost_item_quantities(cost_item={cost_item})"
    And I press "bim.add_cost_item_quantity(cost_item={cost_item}, ifc_class='IfcQuantityArea')"
    And the variable "quantity" is "{ifc}.by_type('IfcQuantityArea')[0].id()"
    When I press "bim.remove_cost_item_quantity(cost_item={cost_item}, physical_quantity={quantity})"
    Then nothing happens

Scenario: Enable editing cost item quantity
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I press "bim.enable_editing_cost_item_quantities(cost_item={cost_item})"
    And I press "bim.add_cost_item_quantity(cost_item={cost_item}, ifc_class='IfcQuantityArea')"
    And the variable "quantity" is "{ifc}.by_type('IfcQuantityArea')[0].id()"
    When I press "bim.enable_editing_cost_item_quantity(physical_quantity={quantity})"
    Then nothing happens

Scenario: Disable editing cost item quantity
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I press "bim.enable_editing_cost_item_quantities(cost_item={cost_item})"
    And I press "bim.add_cost_item_quantity(cost_item={cost_item}, ifc_class='IfcQuantityArea')"
    And the variable "quantity" is "{ifc}.by_type('IfcQuantityArea')[0].id()"
    And I press "bim.enable_editing_cost_item_quantity(physical_quantity={quantity})"
    When I press "bim.disable_editing_cost_item_quantity"
    Then nothing happens

Scenario: Edit cost item quantity
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I press "bim.enable_editing_cost_item_quantities(cost_item={cost_item})"
    And I press "bim.add_cost_item_quantity(cost_item={cost_item}, ifc_class='IfcQuantityArea')"
    And the variable "quantity" is "{ifc}.by_type('IfcQuantityArea')[0].id()"
    And I press "bim.enable_editing_cost_item_quantity(physical_quantity={quantity})"
    And I set "scene.BIMCostProperties.quantity_attributes[2].float_value" to "3"
    When I press "bim.edit_cost_item_quantity(physical_quantity={quantity})"
    Then nothing happens

Scenario: Enable editing cost item quantity
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    When I press "bim.enable_editing_cost_item_values(cost_item={cost_item})"
    Then nothing happens

Scenario: Add cost value - fixed
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I press "bim.enable_editing_cost_item_values(cost_item={cost_item})"
    And I set "scene.BIMCostProperties.cost_types" to "FIXED"
    When I press "bim.add_cost_value(parent={cost_item}, cost_type='FIXED')"
    Then nothing happens

Scenario: Enable editing cost item value
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I press "bim.enable_editing_cost_item_values(cost_item={cost_item})"
    And I set "scene.BIMCostProperties.cost_types" to "FIXED"
    And I press "bim.add_cost_value(parent={cost_item}, cost_type='FIXED')"
    And the variable "cost_value" is "{ifc}.by_type('IfcCostValue')[0].id()"
    When I press "bim.enable_editing_cost_item_value(cost_value={cost_value})"
    Then nothing happens

Scenario: Disable editing cost item value
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I press "bim.enable_editing_cost_item_values(cost_item={cost_item})"
    And I set "scene.BIMCostProperties.cost_types" to "FIXED"
    And I press "bim.add_cost_value(parent={cost_item}, cost_type='FIXED')"
    And the variable "cost_value" is "{ifc}.by_type('IfcCostValue')[0].id()"
    And I press "bim.enable_editing_cost_item_value(cost_value={cost_value})"
    When I press "bim.disable_editing_cost_item_value"
    Then nothing happens

Scenario: Edit cost item value
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I press "bim.enable_editing_cost_item_values(cost_item={cost_item})"
    And I set "scene.BIMCostProperties.cost_types" to "FIXED"
    And I press "bim.add_cost_value(parent={cost_item}, cost_type='FIXED')"
    And the variable "cost_value" is "{ifc}.by_type('IfcCostValue')[0].id()"
    And I press "bim.enable_editing_cost_item_value(cost_value={cost_value})"
    When I press "bim.edit_cost_value(cost_value={cost_value})"
    Then nothing happens

Scenario: Enable editing cost item value formula
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I press "bim.enable_editing_cost_item_values(cost_item={cost_item})"
    And I set "scene.BIMCostProperties.cost_types" to "FIXED"
    And I press "bim.add_cost_value(parent={cost_item}, cost_type='FIXED')"
    And the variable "cost_value" is "{ifc}.by_type('IfcCostValue')[0].id()"
    When I press "bim.enable_editing_cost_item_value_formula(cost_value={cost_value})"
    Then nothing happens

Scenario: Edit cost item value formula
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I press "bim.enable_editing_cost_item_values(cost_item={cost_item})"
    And I set "scene.BIMCostProperties.cost_types" to "FIXED"
    And I press "bim.add_cost_value(parent={cost_item}, cost_type='FIXED')"
    And the variable "cost_value" is "{ifc}.by_type('IfcCostValue')[0].id()"
    And I press "bim.enable_editing_cost_item_value_formula(cost_value={cost_value})"
    And I set "scene.BIMCostProperties.cost_value_formula" to "3 + 2"
    When I press "bim.edit_cost_value_formula(cost_value={cost_value})"
    Then nothing happens

Scenario: Add cost column
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And I set "scene.BIMCostProperties.should_show_column_ui" to "True"
    And I set "scene.BIMCostProperties.cost_column" to "Foobar"
    When I press "bim.add_cost_column(name='Foobar')"
    Then nothing happens

Scenario: Remove cost column
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And I set "scene.BIMCostProperties.should_show_column_ui" to "True"
    And I set "scene.BIMCostProperties.cost_column" to "Foobar"
    And I press "bim.add_cost_column(name='Foobar')"
    When I press "bim.remove_cost_column(name='Foobar')"
    Then nothing happens

Scenario: Assign cost item quantity - count based
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When I press "bim.assign_cost_item_quantity(cost_item={cost_item}, related_object_type='PRODUCT', prop_name='')"
    Then nothing happens

Scenario: Assign cost item quantity - quantity based
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.add_qto(obj='IfcWall/Cube', obj_type='Object')"
    And I press "bim.perform_quantity_take_off"
    When I press "bim.assign_cost_item_quantity(cost_item={cost_item}, related_object_type='PRODUCT', prop_name='NetVolume')"
    Then nothing happens

Scenario: Unassign cost item quantity - selection based
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_cost_item_quantity(cost_item={cost_item}, related_object_type='PRODUCT', prop_name='')"
    When I press "bim.unassign_cost_item_quantity(cost_item={cost_item}, related_object=0)"
    Then nothing happens

Scenario: Unassign cost item quantity - explicit object
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_cost_item_quantity(cost_item={cost_item}, related_object_type='PRODUCT', prop_name='')"
    And the variable "wall" is "{ifc}.by_type('IfcWall')[0].id()"
    When I press "bim.unassign_cost_item_quantity(cost_item={cost_item}, related_object={wall})"
    Then nothing happens

Scenario: Select cost item products
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_cost_item_quantity(cost_item={cost_item}, related_object_type='PRODUCT', prop_name='')"
    When I press "bim.select_cost_item_products(cost_item={cost_item})"
    Then nothing happens

Scenario: Select Cost Schedule Products
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_cost_item_quantity(cost_item={cost_item}, related_object_type='PRODUCT', prop_name='')"
    When I press "bim.select_cost_schedule_products(cost_schedule={cost_schedule})"
    Then nothing happens
Scenario: Load Cost Item Types
    Given an empty IFC project
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And the variable "cost_item" is "{ifc}.by_type('IfcCostItem')[0].id()"
    When I press "bim.add_cost_item(cost_item={cost_item})"
    And I press "bim.load_cost_item_types"
    Then nothing happens
