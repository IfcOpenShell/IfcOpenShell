@debug
Feature: Debug

Scenario: Select express file
    Given an empty Blender session
    When I press "bim.select_express_file(filepath='{cwd}/test/files/test.exp')"
    Then nothing happens

Scenario: Parse express
    Given an empty Blender session
    And I press "bim.select_express_file(filepath='{cwd}/test/files/test.exp')"
    When I press "bim.parse_express"
    And I evaluate expression "os.remove('{cwd}/test/files/test.exp.cache.dat')"
    Then nothing happens

Scenario: Use the inspector - inspect from STEP ID
    Given an empty Blender session
    And I press "bim.create_project"
    When I set "scene.BIMDebugProperties.active_step_id" to "1"
    And I press "bim.inspect_from_step_id(step_id=1)"
    Then nothing happens

Scenario: Use the inspector - inspect from object
    Given an empty Blender session
    And I press "bim.create_project"
    When the object "IfcProject/My Project" is selected
    And I press "bim.inspect_from_object"
    Then nothing happens
