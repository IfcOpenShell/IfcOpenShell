@bsdd
Feature: bSDD

Scenario: Load bSDD dictionaries
    Given an empty IFC project
    And I look at the "buildingSMART Data Dictionary" panel
    When I click "Load bSDD Dictionaries"
    Then I see "Selected Dictionary:"
    And I see "LCA" in the "1st" list

Scenario: Add classification from bSDD - add all dictionaries
    Given an empty IFC project
    And I look at the "buildingSMART Data Dictionary" panel
    And I click "Load bSDD Dictionaries"
    When I click "is_active" in the row where I see "LCA" in the "1st" list
    And I click "is_active" in the row where I see "BonsaiTestDict" in the "1st" list
    And I look at the "Classifications" panel
    And I set the "classification_source" property to "All Active bSDDs"
    And I click "Add Classification From bSDD"
    Then I see "LCA"
    And I see "BonsaiTestDict"

Scenario: Add classification from bSDD - add single dictionary
    Given an empty IFC project
    And I look at the "buildingSMART Data Dictionary" panel
    And I click "Load bSDD Dictionaries"
    When I click "is_active" in the row where I see "BonsaiTestDict" in the "1st" list
    And I look at the "Classifications" panel
    And I set the "classification_source" property to "BonsaiTestDict"
    And I click "Add Classification From bSDD"
    Then I see "BonsaiTestDict"
    And I don't see "LCA"

Scenario: Search bSDD classifications - search all dictionaries
    Given an empty IFC project
    And I look at the "buildingSMART Data Dictionary" panel
    And I click "Load bSDD Dictionaries"
    When I click "is_active" in the row where I see "LCA" in the "1st" list
    And I click "is_active" in the row where I see "BonsaiTestDict" in the "1st" list
    And I select the object "IfcSite/My Site"
    And I look at the "Classification References" panel
    And I set the "classification_source" property to "All Active bSDDs"
    And I click "VIEWZOOM"
    Then I see "Acidification" in the "1st" list
    And I see "BonsaiReferenceA" in the "1st" list

Scenario: Search bSDD classifications - search single dictionary
    Given an empty IFC project
    And I look at the "buildingSMART Data Dictionary" panel
    And I click "Load bSDD Dictionaries"
    And I click "is_active" in the row where I see "BonsaiTestDict" in the "1st" list
    And I select the object "IfcSite/My Site"
    And I look at the "Classification References" panel
    When I set the "classification_source" property to "BonsaiTestDict"
    And I click "VIEWZOOM"
    Then I see "BonsaiReferenceA" in the "1st" list
    And I don't see "Acidification" in the "1st" list

Scenario: Add classification reference from bSDD - add classification only
    Given an empty IFC project
    And I look at the "buildingSMART Data Dictionary" panel
    And I click "Load bSDD Dictionaries"
    When I click "is_active" in the row where I see "LCA" in the "1st" list
    And I click "is_active" in the row where I see "BonsaiTestDict" in the "1st" list
    And I select the object "IfcSite/My Site"
    And I look at the "Classification References" panel
    And I set the "classification_source" property to "All Active bSDDs"
    And I click "VIEWZOOM"
    Then I see "Acidification" in the "1st" list
    When I select the row where I see "Acidification" in the "1st" list
    And I click "Add Classification Reference"
    Then I see "Acidification"
    And I don't see "BonsaiReferenceA"

Scenario: Get bSDD classification properties - get and add associated properties
    Given an empty IFC project
    And I look at the "buildingSMART Data Dictionary" panel
    And I click "Load bSDD Dictionaries"
    When I click "is_active" in the row where I see "LCA" in the "1st" list
    And I select the object "IfcSite/My Site"
    And I look at the "Property Sets" panel
    And I set the "pset_name" property to "All Data Dictionaries"
    And I click "FILE_REFRESH"
    When I select the row where I see "Height" in the "2nd" list
    And I click "is_selected" in the row where I see "Height" in the "2nd" list
    And I click "is_selected" in the row where I see "Volume" in the "2nd" list
    Then I look at the "Property Sets" panel
    And I set the "height" property to "42"
    And I set the "volume" property to "23"
    When I click "Add bSDD Properties"
    Then I look at the "Property Sets" panel
    And I see "height"
    And I see "42.0"
    And I see "volume"
    And I see "23.0"
