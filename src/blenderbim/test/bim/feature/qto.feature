@qto
Feature: Qto

Scenario: Calculate circle radius
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.calculate_circle_radius"
    Then "scene.BIMQtoProperties.qto_result" is "1.732"

Scenario: Calculate edge lengths
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.calculate_edge_lengths"
    Then "scene.BIMQtoProperties.qto_result" is "24.0"

Scenario: Calculate face areas
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.calculate_face_areas"
    Then "scene.BIMQtoProperties.qto_result" is "24.0"

Scenario: Calculate object volumes
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.calculate_object_volumes"
    Then "scene.BIMQtoProperties.qto_result" is "8.0"
