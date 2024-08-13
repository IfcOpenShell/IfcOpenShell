@context
Feature: Context
    Manages geometric representation contexts and subcontexts

Scenario: Add context
    Given an empty IFC project
    When I press "bim.add_context(context_type='Model', context_identifier='', target_view='', parent=0)"
    Then nothing happens

Scenario: Add a subcontext
    Given an empty IFC project
    When the variable "parent" is "IfcStore.get_file().by_type('IfcGeometricRepresentationContext', include_subtypes=False)[0].id()"
    When I press "bim.add_context(context_type='Model', context_identifier='Body', target_view='MODEL_VIEW', parent={parent})"
    Then nothing happens

Scenario: Remove context
    Given an empty IFC project
    When the variable "context" is "IfcStore.get_file().by_type('IfcGeometricRepresentationContext')[0].id()"
    And I press "bim.remove_context(context={context})"
    Then nothing happens

Scenario: Enable editing context
    Given an empty IFC project
    When I press "bim.add_context(context_type='Model', context_identifier='', target_view='', parent=0)"
    And the variable "context" is "IfcStore.get_file().by_type('IfcGeometricRepresentationContext')[0].id()"
    And I press "bim.enable_editing_context(context={context})"
    Then nothing happens

Scenario: Disable editing context
    Given an empty IFC project
    When I press "bim.add_context(context_type='Model', context_identifier='', target_view='', parent=0)"
    And the variable "context" is "IfcStore.get_file().by_type('IfcGeometricRepresentationContext')[0].id()"
    And I press "bim.enable_editing_context(context={context})"
    And I press "bim.disable_editing_context()"
    Then nothing happens

Scenario: Edit context
    Given an empty IFC project
    When I press "bim.add_context(context_type='Model', context_identifier='', target_view='', parent=0)"
    And the variable "context" is "IfcStore.get_file().by_type('IfcGeometricRepresentationContext')[0].id()"
    And I press "bim.enable_editing_context(context={context})"
    And I press "bim.edit_context"
    Then nothing happens
