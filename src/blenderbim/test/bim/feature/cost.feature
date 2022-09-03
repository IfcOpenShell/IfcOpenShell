@cost
Feature: Cost

Scenario: Add cost schedule
    Given an empty IFC project
    When I press "bim.add_cost_schedule"
    Then nothing happens

Scenario: Enable editing cost items
    Given an empty IFC project
    When I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    Then nothing happens

Scenario: Add summary cost item
    Given an empty IFC project
    When I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item(cost_schedule={cost_schedule})"
    Then nothing happens
