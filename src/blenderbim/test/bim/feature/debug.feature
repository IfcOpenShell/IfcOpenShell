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
    Then nothing happens
