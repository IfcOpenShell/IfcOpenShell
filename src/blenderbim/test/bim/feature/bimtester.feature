@bimtester
Feature: Bimtester

Scenario: Execute Bimtester
    Given an empty IFC project
    When I set "scene.BimTesterProperties.should_load_from_memory" to "True"
    And I set "scene.BimTesterProperties.feature" to "{cwd}/test/files/sample.feature"
    And I press "bim.execute_bim_tester"
    Then nothing happens
