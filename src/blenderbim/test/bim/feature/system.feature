@system
Feature: System

Scenario: Load systems
    Given an empty IFC project
    When I press "bim.load_systems"
    Then nothing happens

Scenario: Disable system editing UI
    Given an empty IFC project
    When I press "bim.load_systems"
    And I press "bim.disable_system_editing_ui"
    Then nothing happens

Scenario: Add system
    Given an empty IFC project
    And I press "bim.load_systems"
    When I press "bim.add_system"
    Then nothing happens

Scenario: Edit system
    Given an empty IFC project
    And I press "bim.load_systems"
    And I press "bim.add_system"
    And the variable "system" is "{ifc}.by_type('IfcSystem')[0].id()"
    And I press "bim.enable_editing_system(system={system})"
    When I press "bim.edit_system"
    Then nothing happens

Scenario: Edit system
    Given an empty IFC project
    And I press "bim.load_systems"
    And I press "bim.add_system"
    And the variable "system" is "{ifc}.by_type('IfcSystem')[0].id()"
    When I press "bim.remove_system(system={system})"
    Then nothing happens

Scenario: Enable editing system
    Given an empty IFC project
    And I press "bim.load_systems"
    And I press "bim.add_system"
    And the variable "system" is "{ifc}.by_type('IfcSystem')[0].id()"
    When I press "bim.enable_editing_system(system={system})"
    Then nothing happens

Scenario: Disable editing system
    Given an empty IFC project
    And I press "bim.load_systems"
    And I press "bim.add_system"
    And the variable "system" is "{ifc}.by_type('IfcSystem')[0].id()"
    And I press "bim.enable_editing_system(system={system})"
    When I press "bim.disable_editing_system"
    Then nothing happens

Scenario: Assign system
    Given an empty IFC project
    And I press "bim.load_systems"
    And I set "scene.BIMSystemProperties.system_class" to "IfcDistributionSystem"
    And I press "bim.add_system"
    And the variable "system" is "{ifc}.by_type('IfcSystem')[0].id()"
    And I press "bim.enable_editing_system(system={system})"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcPump"
    And I press "bim.assign_class"
    And the object "IfcPump/Cube" is selected
    When I press "bim.assign_system(system={system})"
    Then nothing happens

Scenario: Unassign system
    Given an empty IFC project
    And I press "bim.load_systems"
    And I set "scene.BIMSystemProperties.system_class" to "IfcDistributionSystem"
    And I press "bim.add_system"
    And the variable "system" is "{ifc}.by_type('IfcSystem')[0].id()"
    And I press "bim.enable_editing_system(system={system})"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcPump"
    And I press "bim.assign_class"
    And the object "IfcPump/Cube" is selected
    And I press "bim.assign_system(system={system})"
    When I press "bim.unassign_system(system={system})"
    Then nothing happens

Scenario: Select system products
    Given an empty IFC project
    And I press "bim.load_systems"
    And I set "scene.BIMSystemProperties.system_class" to "IfcDistributionSystem"
    And I press "bim.add_system"
    And the variable "system" is "{ifc}.by_type('IfcSystem')[0].id()"
    And I press "bim.enable_editing_system(system={system})"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcPump"
    And I press "bim.assign_class"
    And the object "IfcPump/Cube" is selected
    And I press "bim.assign_system(system={system})"
    When I press "bim.select_system_products(system={system})"
    Then nothing happens
