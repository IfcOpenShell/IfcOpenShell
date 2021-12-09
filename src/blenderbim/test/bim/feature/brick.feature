@brick
Feature: Brick

Scenario: Load Brick project
    Given an empty Blender session
    When I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    Then nothing happens

Scenario: View Brick class
    Given an empty Blender session
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    When I press "bim.view_brick_class(brick_class='Equipment')"
    Then nothing happens

Scenario: View Brick item
    Given an empty Blender session
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    When I press "bim.view_brick_item(item='https://brickschema.org/schema/Brick#Chiller')"
    Then nothing happens

Scenario: Rewind brick class
    Given an empty Blender session
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And I press "bim.view_brick_class(brick_class='Equipment')"
    When I press "bim.rewind_brick_class()"
    Then nothing happens

Scenario: Close Brick project
    Given an empty Blender session
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    When I press "bim.close_brick_project"
    Then nothing happens

Scenario: Convert brick project
    Given an empty IFC project
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    When I press "bim.convert_brick_project"
    Then nothing happens

Scenario: Assign brick reference
    Given an empty IFC project
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And I press "bim.view_brick_item(item='https://brickschema.org/schema/Brick#Chiller')"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcChiller"
    And I press "bim.assign_class"
    And the object "IfcChiller/Cube" is selected
    And I press "bim.convert_brick_project"
    When I press "bim.assign_brick_reference"
    Then nothing happens

Scenario: Add brick - without a brick IFC library
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcChiller"
    And I press "bim.assign_class"
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And the object "IfcChiller/Cube" is selected
    And I set "scene.BIMBrickProperties.namespace" to "http://example.org/digitaltwin#"
    When I press "bim.add_brick"
    Then nothing happens

Scenario: Add brick - with a brick IFC library
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcChiller"
    And I press "bim.assign_class"
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And I press "bim.convert_brick_project"
    And the object "IfcChiller/Cube" is selected
    And I set "scene.BIMBrickProperties.namespace" to "http://example.org/digitaltwin#"
    When I press "bim.add_brick"
    Then nothing happens
