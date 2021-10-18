@misc
Feature: Misc

Scenario: Set override colour
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.set_override_colour"
    Then nothing happens

Scenario: Set viewport shadow from sun
    Given an empty IFC project
    And I add a sun
    And the object "Sun" is selected
    When I press "bim.set_viewport_shadow_from_sun"
    Then nothing happens

Scenario: Snap spaces together
    Given an empty IFC project
    And I add a cube
    And I add a cube
    And the object "Cube" is selected
    And additionally the object "Cube.001" is selected
    When I press "bim.snap_spaces_together"
    Then nothing happens
