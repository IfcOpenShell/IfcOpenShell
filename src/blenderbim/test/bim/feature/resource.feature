@resource
Feature: Resource

Scenario: Load Resources
    Given an empty IFC project
    When I press "bim.load_resources"
    Then nothing happens

Scenario: Add Crew Resource
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    Then nothing happens

Scenario: Disable Editing resources
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    When I press "bim.disable_resource_editing_ui"
    Then nothing happens

Scenario: Re-enable Editing resources
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    When I press "bim.disable_resource_editing_ui"
    When I press "bim.load_resources"
    Then nothing happens


Scenario: Add Labor Resource
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    Then nothing happens


Scenario: Enable Editing Resource
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.enable_editing_resource(resource={crew_resource})"
    Then nothing happens

Scenario: Edit Resource
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.enable_editing_resource(resource={crew_resource})"
    And I set "scene.BIMResourceProperties.resource_attributes.get('Name').string_value" to "Foo"
    When I press "bim.edit_resource()"
    Then nothing happens

Scenario: Remove Resource
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.enable_editing_resource(resource={crew_resource})"
    And I set "scene.BIMResourceProperties.resource_attributes.get('Name').string_value" to "Foo"
    When I press "bim.edit_resource()"
    When I press "bim.remove_resource(resource={crew_resource})"
    Then nothing happens

Scenario: Remove Parent Resource
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    When I press "bim.enable_editing_resource_time(resource={labor_resource})"
    And I set "scene.BIMResourceProperties.resource_time_attributes.get('Name').string_value" to "TimelyFoo"
    When I press "bim.edit_resource_time()"
    When I press "bim.remove_resource(resource={crew_resource})"
    Then nothing happens

Scenario: Enable Editing Resource time
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    When I press "bim.enable_editing_resource_time(resource={labor_resource})"
    Then nothing happens

Scenario: Disable editing resource time
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    And I press "bim.enable_editing_resource_time(resource={labor_resource})"
    When I press "bim.disable_editing_resource()"
    Then nothing happens

Scenario: Edit Resource time
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    When I press "bim.enable_editing_resource_time(resource={labor_resource})"
    And I set "scene.BIMResourceProperties.resource_time_attributes.get('ScheduleUsage').float_value" to "305.25"
    When I press "bim.edit_resource_time()"
    Then nothing happens

Scenario: Enable Editing Resource Costs
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    When I press "bim.enable_editing_resource_costs(resource={labor_resource})"
    Then nothing happens

Scenario: Disable Editing Resource Costs
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    When I press "bim.enable_editing_resource_costs(resource={labor_resource})"
    When I press "bim.disable_editing_resource()"
    Then nothing happens


Scenario: Add Resource Fixed Cost Value
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    When I press "bim.enable_editing_resource_costs(resource={labor_resource})"
    When I press "bim.add_cost_value(parent={labor_resource}, cost_type="FIXED")"
    Then nothing happens

Scenario: Edit Resource Cost Value
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    When I press "bim.enable_editing_resource_costs(resource={labor_resource})"
    When I press "bim.add_cost_value(parent={labor_resource}, cost_type="FIXED")"
    And the variable "cost_value" is "IfcStore.get_file().by_type('IfcCostValue')[0].id()" 
    When I press "bim.enable_editing_resource_cost_value(cost_value={cost_value})"
    Then nothing happens

Scenario: Enable Editing Resource Cost Value Formula
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    When I press "bim.enable_editing_resource_costs(resource={labor_resource})"
    When I press "bim.add_cost_value(parent={labor_resource}, cost_type="FIXED")"
    And the variable "cost_value" is "IfcStore.get_file().by_type('IfcCostValue')[0].id()" 
    When I press "bim.enable_editing_resource_cost_value(cost_value={cost_value})"
    Then nothing happens

Scenario: Edit Resource Cost Value Formula
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    When I press "bim.enable_editing_resource_costs(resource={labor_resource})"
    When I press "bim.add_cost_value(parent={labor_resource}, cost_type="FIXED")"
    And the variable "cost_value" is "IfcStore.get_file().by_type('IfcCostValue')[0].id()" 
    When I press "bim.enable_editing_resource_cost_value(cost_value={cost_value})"
    And I set "scene.BIMResourceProperties.cost_value_formula" to "220*0.2"
    When I press "bim.edit_resource_cost_value_formula(cost_value={cost_value})"
    Then nothing happens

Scenario: Edit Resource Cost Value
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    When I press "bim.enable_editing_resource_costs(resource={labor_resource})"
    When I press "bim.add_cost_value(parent={labor_resource}, cost_type="FIXED")"
    And the variable "cost_value" is "IfcStore.get_file().by_type('IfcCostValue')[0].id()" 
    When I press "bim.enable_editing_resource_cost_value(cost_value={cost_value})"
    And I set "scene.BIMResourceProperties.cost_value_attributes.get('AppliedValue').float_value" to "1.00"
    When I press "bim.edit_resource_cost_value(cost_value={cost_value})"
    Then nothing happens

Scenario: Enable Editing Resource Quantity
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    When I press "bim.enable_editing_resource_base_quantity(resource={labor_resource})"
    When I press "bim.add_resource_quantity(resource={labor_resource}, ifc_class="IfcQuantityArea")"
    When I press "bim.enable_editing_resource_quantity(resource={labor_resource})"
    Then nothing happens

Scenario: Edit Resource Quantity
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    When I press "bim.enable_editing_resource_base_quantity(resource={labor_resource})"
    When I press "bim.add_resource_quantity(resource={labor_resource}, ifc_class="IfcQuantityArea")"
    When I press "bim.enable_editing_resource_quantity(resource={labor_resource})"
    And I set "scene.BIMResourceProperties.quantity_attributes.get('AreaValue').float_value" to "50.00"
    And the variable "quantity_area" is "IfcStore.get_file().by_type('IfcQuantityArea')[0].id()" 
    When I press "bim.edit_resource_quantity(physical_quantity={quantity_area})"
    Then nothing happens

Scenario: Remove Resource Quantity
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    When I press "bim.enable_editing_resource_base_quantity(resource={labor_resource})"
    When I press "bim.add_resource_quantity(resource={labor_resource}, ifc_class="IfcQuantityArea")"
    And the variable "quantity_area" is "IfcStore.get_file().by_type('IfcQuantityArea')[0].id()" 
    When I press "bim.remove_resource_quantity(resource={labor_resource})"
    Then nothing happens

Scenario: Calculate Resource Work
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_attributes.get('PredefinedType').enum_value" to "CONSTRUCTION"
    And I press "bim.edit_task"
    And I press "bim.enable_editing_task_time(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I set "active_object.PsetProperties.qto_name" to "Qto_WallBaseQuantities"
    When I press "bim.add_pset(obj='IfcWall/Cube', obj_type='Object')"
    And the variable "qto" is "{ifc}.by_type('IfcElementQuantity')[-1].id()"
    And I press "bim.enable_pset_editing(obj='IfcWall/Cube', obj_type='Object', pset_id={qto})"
    #And I set "active_object.PsetProperties.properties[2].metadata.float_value" to "3.00"
    # TO DO: complete
    Then nothing happens


Scenario: Assign Resource
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_resource(resource={labor_resource}, related_object="")"
    Then nothing happens

Scenario: UnAssign Resource
    Given an empty IFC project
    When I press "bim.load_resources"
    When I press "bim.add_resource(ifc_class="IfcCrewResource")"
    And the variable "crew_resource" is "IfcStore.get_file().by_type('IfcCrewResource')[0].id()" 
    When I press "bim.add_resource(ifc_class="IfcLaborResource", parent_resource={crew_resource})"
    And the variable "labor_resource" is "IfcStore.get_file().by_type('IfcLaborResource')[0].id()" 
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_resource(resource={labor_resource}, related_object="")"
    And the object "IfcWall/Cube" is selected
    And I press "bim.unassign_resource(resource={labor_resource}, related_object="")"
    Then nothing happens