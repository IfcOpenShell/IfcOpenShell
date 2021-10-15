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

Scenario: Override delete - without active IFC data
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "object.delete"
    Then the object "Cube" does not exist

Scenario: Override delete - with active IFC data
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When I press "object.delete"
    Then the object "IfcWall/Cube" does not exist

Scenario: Override duplicate move - without active IFC data
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "object.duplicate_move"
    Then the object "Cube" exists
    And the object "Cube.001" exists

Scenario: Override duplicate move - with active IFC data
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When I press "object.duplicate_move"
    Then the object "IfcWall/Cube" exists
    And the object "IfcWall/Cube" is an "IfcWall"
    And the object "IfcWall/Cube.001" exists
    And the object "IfcWall/Cube.001" is an "IfcWall"
