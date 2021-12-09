@structural
Feature: Structural

Scenario: Load structural analysis models
    Given an empty IFC project
    When I press "bim.load_structural_analysis_models"
    Then nothing happens

Scenario: Add structural analysis model
    Given an empty IFC project
    And I press "bim.load_structural_analysis_models"
    When I press "bim.add_structural_analysis_model"
    Then nothing happens

Scenario: Disable structural analysis model editing UI
    Given an empty IFC project
    And I press "bim.load_structural_analysis_models"
    When I press "bim.disable_structural_analysis_model_editing_ui"
    Then nothing happens
