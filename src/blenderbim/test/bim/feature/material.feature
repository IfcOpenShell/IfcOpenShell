@material
Feature: Material

Scenario: Add default material
    Given an empty IFC project
    When I press "bim.add_default_material"
    Then the material "Default" exists

Scenario: Add material
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add a material
    When I press "bim.add_material"
    Then the material "Material" is an IFC material

Scenario: Remove material
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add a material
    And I press "bim.add_material"
    When I press "bim.remove_material"
    Then the material "Material" is not an IFC material

Scenario: Unlink material
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add a material
    And I press "bim.add_material"
    When I press "bim.unlink_material"
    Then the material "Material" is not an IFC material
