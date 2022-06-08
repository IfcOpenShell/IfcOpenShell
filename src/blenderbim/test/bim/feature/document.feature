@document
Feature: Document

Scenario: Load project documents
    Given an empty IFC project
    When I press "bim.load_project_documents"
    Then nothing happens

Scenario: Load document
    Given an empty IFC project
    And I press "bim.load_project_documents"
    And I press "bim.add_information"
    And the variable "information" is "{ifc}.by_type('IfcDocumentInformation')[-1].id()"
    When I press "bim.load_document(document={information})"
    Then nothing happens

Scenario: Load parent document
    Given an empty IFC project
    And I press "bim.load_project_documents"
    And I press "bim.add_information"
    And the variable "information" is "{ifc}.by_type('IfcDocumentInformation')[-1].id()"
    And I press "bim.load_document(document={information})"
    When I press "bim.load_parent_document"
    Then nothing happens

Scenario: Disable document editing UI
    Given an empty IFC project
    And I press "bim.load_project_documents"
    When I press "bim.disable_document_editing_ui"
    Then nothing happens

Scenario: Enable editing document
    Given an empty IFC project
    And I press "bim.load_project_documents"
    And I press "bim.add_information"
    And the variable "information" is "{ifc}.by_type('IfcDocumentInformation')[-1].id()"
    When I press "bim.enable_editing_document(document={information})"
    Then nothing happens

Scenario: Disable editing document
    Given an empty IFC project
    And I press "bim.load_project_documents"
    And I press "bim.add_information"
    And the variable "information" is "{ifc}.by_type('IfcDocumentInformation')[-1].id()"
    And I press "bim.enable_editing_document(document={information})"
    When I press "bim.disable_editing_document"
    Then nothing happens

Scenario: Add information
    Given an empty IFC project
    And I press "bim.load_project_documents"
    When I press "bim.add_information"
    Then nothing happens

Scenario: Add document reference
    Given an empty IFC project
    And I press "bim.load_project_documents"
    And I press "bim.add_information"
    And the variable "information" is "{ifc}.by_type('IfcDocumentInformation')[-1].id()"
    And I press "bim.load_document(document={information})"
    When I press "bim.add_document_reference"
    Then nothing happens

Scenario: Edit document
    Given an empty IFC project
    And I press "bim.load_project_documents"
    And I press "bim.add_information"
    And the variable "information" is "{ifc}.by_type('IfcDocumentInformation')[-1].id()"
    And I press "bim.enable_editing_document(document={information})"
    When I press "bim.edit_document"
    Then nothing happens

Scenario: Remove document
    Given an empty IFC project
    And I press "bim.load_project_documents"
    And I press "bim.add_information"
    And the variable "information" is "{ifc}.by_type('IfcDocumentInformation')[-1].id()"
    When I press "bim.remove_document(document={information})"
    Then nothing happens

Scenario: Assign document
    Given an empty IFC project
    And I press "bim.load_project_documents"
    And I press "bim.add_information"
    And the variable "information" is "{ifc}.by_type('IfcDocumentInformation')[-1].id()"
    And I press "bim.load_document(document={information})"
    And I press "bim.add_document_reference"
    And the variable "reference" is "{ifc}.by_type('IfcDocumentReference')[-1].id()"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When I press "bim.assign_document(document={reference})"
    Then nothing happens

Scenario: Unassign document
    Given an empty IFC project
    And I press "bim.load_project_documents"
    And I press "bim.add_information"
    And the variable "information" is "{ifc}.by_type('IfcDocumentInformation')[-1].id()"
    And I press "bim.load_document(document={information})"
    And I press "bim.add_document_reference"
    And the variable "reference" is "{ifc}.by_type('IfcDocumentReference')[-1].id()"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.assign_document(document={reference})"
    When I press "bim.unassign_document(document={reference})"
    Then nothing happens
