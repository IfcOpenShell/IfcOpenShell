@bimtester
Feature: Bimtester

Scenario: Execute Bimtester
    Given an empty IFC project
    When I set "scene.BimTesterProperties.should_load_from_memory" to "True"
    And I set "scene.BimTesterProperties.feature" to "{cwd}/test/files/sample-ids.xml"
    And I press "bim.execute_bim_tester"
    Then nothing happens
    # IDS is continuously changing right now. Stable release scheduled for March 2022.
    #Then the file "{cwd}/test/files/sample-ids.xml.html" should contain "Tests passed: <strong>1 / 1</strong> (100%)"
