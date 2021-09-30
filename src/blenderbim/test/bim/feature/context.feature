@context
Feature: Context
    Manages geometric representation contexts and subcontexts

Scenario: Add subcontext
    Given an empty IFC project
    When I press "bim.add_subcontext(context='Model', subcontext='Body', target_view='MODEL_VIEW')"
    Then nothing happens

Scenario: Remove subcontext
    Given an empty IFC project
    When the variable "context" is "IfcStore.get_file().by_type('IfcGeometricRepresentationContext')[0].id()"
    And I press "bim.remove_subcontext(context={context})"
    Then nothing happens
