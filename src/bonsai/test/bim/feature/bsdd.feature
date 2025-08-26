@bsdd
Feature: bSDD

Scenario: Load bSDD dictionaries
    Given an empty Blender session
    And I look at the "buildingSMART Data Dictionary" panel
    When I click "Load bSDD Dictionaries"
    Then I see "Selected dictionary"
    And I see "LCA" in the "1st" list

Scenario: Add classification from bSDD - add all dictionaries
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

Scenario: Add classification from bSDD - add single dictionary
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

Scenario: Search bSDD classifications - search all dictionaries
    Given an empty IFC project
    And I look at the "buildingSMART Data Dictionary" panel
    And I click "Load bSDD Dictionaries"
    When I click "is_active" in the row where I see "LCA" in the "1st" list
    And I click "is_active" in the row where I see "BonsaiTestDict" in the "1st" list
    And I select the object "IfcSite/My Site"
    And I look at the "Classification References" panel
    And I set the "classification_source" property to "buildingSMART Data Dictionary"
    And I set the "active_dictionary" property to "All Dictionaries"
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
    When I set the "classification_source" property to "buildingSMART Data Dictionary"
    And I set the "active_dictionary" property to "BonsaiTestDict"
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
    And I set the "classification_source" property to "buildingSMART Data Dictionary"
    And I set the "active_dictionary" property to "All Dictionaries"
    And I click "VIEWZOOM"
    Then I see "Acidification" in the "1st" list
    When I select the row where I see "Acidification" in the "1st" list
    And I click "Add Classification Reference"
    Then I see "Acidification"
    And I don't see "BonsaiReferenceA"

Scenario: Get bSDD classification properties - get associated properties then add classification
    Given an empty IFC project
    And I look at the "buildingSMART Data Dictionary" panel
    And I click "Load bSDD Dictionaries"
    When I click "is_active" in the row where I see "LCA" in the "1st" list
    And I select the object "IfcSite/My Site"
    And I look at the "Classification References" panel
    And I set the "classification_source" property to "buildingSMART Data Dictionary"
    And I set the "active_dictionary" property to "All Dictionaries"
    And I click "VIEWZOOM"
    When I select the row where I see "Acidification" in the "1st" list
    And I click "COPY_ID"
    Then I see "SizeSet"
    And I see "Height"
    And I see "Volume"
    And I see "No References"
    When I set the "Height" property to "42"
    And I click "Add Classification Reference"
    Then I see "Acidification"
    And I don't see "No References"
    When I look at the "Property Sets" panel
    Then I see "SizeSet"
    And I see "Height"
    And I see "42"
    And I see "Volume"
    And I see "0"
