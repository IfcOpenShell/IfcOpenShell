@unit
Feature: Unit

Scenario: Assign scene units
    Given an empty IFC project
    When I press "bim.assign_scene_units"
    Then nothing happens

Scenario: Assign unit
    Given an empty IFC project
    And the variable "unit" is "{ifc}.by_type('IfcSIUnit')[0].id()"
    When I press "bim.assign_unit(unit={unit})"
    Then nothing happens

Scenario: Unassign unit
    Given an empty IFC project
    And the variable "unit" is "{ifc}.by_type('IfcSIUnit')[0].id()"
    When I press "bim.unassign_unit(unit={unit})"
    Then nothing happens

Scenario: Load units
    Given an empty IFC project
    When I press "bim.load_units"
    Then nothing happens

Scenario: Disable unit editing UI
    Given an empty IFC project
    And I press "bim.load_units"
    When I press "bim.disable_unit_editing_ui"
    Then nothing happens

Scenario: Remove unit
    Given an empty IFC project
    And the variable "unit" is "{ifc}.by_type('IfcSIUnit')[0].id()"
    When I press "bim.remove_unit(unit={unit})"
    Then nothing happens

Scenario: Add monetary unit
    Given an empty IFC project
    When I press "bim.add_monetary_unit"
    Then nothing happens

Scenario: Add SI unit
    Given an empty IFC project
    When I press "bim.add_si_unit(unit_type='LENGTHUNIT')"
    Then nothing happens

Scenario: Add context dependent unit
    Given an empty IFC project
    When I press "bim.add_context_dependent_unit(name='THINGAMAJIGS', unit_type='LENGTHUNIT')"
    Then nothing happens

Scenario: Add conversion based unit
    Given an empty IFC project
    When I press "bim.add_conversion_based_unit(name='inch')"
    Then nothing happens

Scenario: Add conversion based unit with offset
    Given an empty IFC project
    When I press "bim.add_conversion_based_unit(name='fahrenheit')"
    Then nothing happens

Scenario: Enable editing unit
    Given an empty IFC project
    And the variable "unit" is "{ifc}.by_type('IfcSIUnit')[0].id()"
    When I press "bim.enable_editing_unit(unit={unit})"
    Then nothing happens

Scenario: Disable editing unit
    Given an empty IFC project
    And the variable "unit" is "{ifc}.by_type('IfcSIUnit')[0].id()"
    And I press "bim.enable_editing_unit(unit={unit})"
    When I press "bim.disable_editing_unit"
    Then nothing happens

Scenario: Edit unit
    Given an empty IFC project
    And the variable "unit" is "{ifc}.by_type('IfcSIUnit')[0].id()"
    And I press "bim.enable_editing_unit(unit={unit})"
    When I press "bim.edit_unit(unit={unit})"
    Then nothing happens
