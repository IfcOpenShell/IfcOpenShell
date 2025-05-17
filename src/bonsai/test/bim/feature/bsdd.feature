@bsdd
Feature: bSDD

Scenario: Load bSDD dictionaries
    Given an empty Blender session
    And I look at the "buildingSMART Data Dictionary" panel
    When I click "Load bSDD Dictionaries"
    Then I see "Selected dictionary"
    And I see "LCA" in the "1st" list

Scenario: Add dictionaries as classification systems
    Given an empty IFC project
    And I look at the "buildingSMART Data Dictionary" panel
    And I click "Load bSDD Dictionaries"
    When I click "is_active" in the row where I see "LCA" in the "1st" list
    And I click "is_active" in the row where I see "BonsaiTestDict" in the "1st" list
    And I look at the "Classifications" panel
    And I set the "classification_source" property to "buildingSMART Data Dictionary"
    And I set the "active_dictionary" property to "All Dictionaries"
    And I click "Add Classification From bSDD"
    Then I see "LCA"
    And I see "BonsaiTestDict"

Scenario: Add a single dictionary as a classification systems
    Given an empty IFC project
    And I look at the "buildingSMART Data Dictionary" panel
    And I click "Load bSDD Dictionaries"
    When I click "is_active" in the row where I see "BonsaiTestDict" in the "1st" list
    And I look at the "Classifications" panel
    And I set the "classification_source" property to "buildingSMART Data Dictionary"
    And I set the "active_dictionary" property to "BonsaiTestDict"
    And I click "Add Classification From bSDD"
    Then I see "BonsaiTestDict"
    And I don't see "LCA"
