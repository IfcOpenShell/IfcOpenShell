@pset_template
Feature: Pset_Template
    Covers property sets and property templates creation, edition, deletion.

Scenario: Add pset template
    Given an empty IFC project
    When I load a new pset template file
    And I press "bim.add_pset_template"
    Then nothing happens

Scenario: Remove pset template
    Given an empty IFC project
    When I load a new pset template file
    And I press "bim.add_pset_template"
    And I press "bim.remove_pset_template"
    Then nothing happens

Scenario: Enable editing pset template
    Given an empty IFC project
    When I load a new pset template file
    And I press "bim.add_pset_template"
    And I press "bim.enable_editing_pset_template"
    Then nothing happens

Scenario: Edit pset template
    Given an empty IFC project
    When I load a new pset template file
    And I press "bim.add_pset_template"
    And I press "bim.enable_editing_pset_template"
    And I press "bim.edit_pset_template"
    Then nothing happens

Scenario: Disable editing pset template
    Given an empty IFC project
    When I load a new pset template file
    And I press "bim.add_pset_template"
    And I press "bim.enable_editing_pset_template"
    And I press "bim.disable_editing_pset_template"
    Then nothing happens

Scenario: Save pset template
    Given an empty IFC project
    When I load a new pset template file
    And I press "bim.save_pset_template_file"
    Then nothing happens

Scenario: Add prop template
    Given an empty IFC project
    When I load a new pset template file
    And I press "bim.add_pset_template"
    And I press "bim.add_prop_template"
    Then nothing happens

Scenario: Remove prop template
    Given an empty IFC project
    When I load a new pset template file
    And I press "bim.add_pset_template"
    And I press "bim.add_prop_template"
    And the variable "prop_template" is "{pset_ifc}.by_type('IfcSimplePropertyTemplate')[-1].id()"
    And I press "bim.remove_prop_template(prop_template={prop_template})"
    Then nothing happens

Scenario: Enable editing prop template
    Given an empty IFC project
    When I load a new pset template file
    And I press "bim.add_pset_template"
    And the variable "prop_template" is "{pset_ifc}.by_type('IfcSimplePropertyTemplate')[-1].id()"
    And I press "bim.enable_editing_prop_template(prop_template={prop_template})"
    Then nothing happens

Scenario: Edit prop template
    Given an empty IFC project
    When I load a new pset template file
    And I press "bim.add_pset_template"
    And the variable "prop_template" is "{pset_ifc}.by_type('IfcSimplePropertyTemplate')[-1].id()"
    And I press "bim.enable_editing_prop_template(prop_template={prop_template})"
    And I press "bim.edit_prop_template"
    Then nothing happens

Scenario: Edit prop template - enumeration property
    Given an empty IFC project
    When I load a new pset template file
    And I press "bim.add_pset_template"
    And the variable "prop_template" is "{pset_ifc}.by_type('IfcSimplePropertyTemplate')[-1].id()"
    And I press "bim.enable_editing_prop_template(prop_template={prop_template})"
    And I set "scene.BIMPsetTemplateProperties.active_prop_template.template_type" to "P_ENUMERATEDVALUE"
    And I press "bim.edit_prop_template"
    Then nothing happens

Scenario: Add prop enum
    Given an empty IFC project
    When I load a new pset template file
    And I press "bim.add_pset_template"
    And I press "bim.add_prop_template"
    And the variable "prop_template" is "{pset_ifc}.by_type('IfcSimplePropertyTemplate')[-1].id()"
    And I press "bim.enable_editing_prop_template(prop_template={prop_template})"
    And I set "scene.BIMPsetTemplateProperties.active_prop_template.template_type" to "P_ENUMERATEDVALUE"
    And I press "bim.add_prop_enum"
    And I press "bim.edit_prop_template"
    Then nothing happens

Scenario: Delete prop enum
    Given an empty IFC project
    When I load a new pset template file
    And I press "bim.add_pset_template"
    And I press "bim.add_prop_template"
    And the variable "prop_template" is "{pset_ifc}.by_type('IfcSimplePropertyTemplate')[-1].id()"
    And I press "bim.enable_editing_prop_template(prop_template={prop_template})"
    And I set "scene.BIMPsetTemplateProperties.active_prop_template.template_type" to "P_ENUMERATEDVALUE"
    And I press "bim.add_prop_enum"
    And I press "bim.delete_prop_enum(index=0)"
    And I press "bim.edit_prop_template"
    Then nothing happens

Scenario: Disable editing prop template
    Given an empty IFC project
    When I load a new pset template file
    And I press "bim.add_pset_template"
    And the variable "prop_template" is "{pset_ifc}.by_type('IfcSimplePropertyTemplate')[-1].id()"
    And I press "bim.enable_editing_prop_template(prop_template={prop_template})"
    And I press "bim.disable_editing_prop_template"
    Then nothing happens
