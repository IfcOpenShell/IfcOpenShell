@context
Feature: Context
    Manages geometric representation contexts and subcontexts

Scenario: Add subcontext
    Given an empty IFC project
    When I press "bim.add_subcontext(context='Model')"
    Then nothing happens

Scenario: Remove subcontext
    Given an empty IFC project
    When the variable "context_id" is "IfcStore.get_file().by_type('IfcGeometricRepresentationContext')[0].id()"
    And I press "bim.remove_subcontext(ifc_definition_id={context_id})"
    Then nothing happens
