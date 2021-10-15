@geometry
Feature: Geometry

Scenario: Edit object placement
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When I press "bim.edit_object_placement"
    Then nothing happens

Scenario: Copy representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcWall/Cube.001" is selected
    When I press "bim.copy_representation"
    Then nothing happens
