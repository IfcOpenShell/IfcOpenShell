@material
Feature: Material

Scenario: Unlink object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add a material
    And I press "bim.add_material"
    When I press "bim.unlink_material"
    Then the material "Material" is not an IFC material
