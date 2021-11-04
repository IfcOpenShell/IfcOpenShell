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
