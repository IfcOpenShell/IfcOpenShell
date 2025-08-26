@structural
Feature: Structural

Scenario: Add element - a structural point connection
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Name" property to "Foo"
    And I set the "Definition" property to "IfcStructuralItem"
    And I set the "Class" property to "IfcStructuralPointConnection"
    And I set the "Representation" property to "Vertex"
    When I click "OK"
    And I make the collection "IfcStructuralItem" visible
    And I select the object "IfcStructuralPointConnection/Foo"
    And I toggle edit mode
    Then the object "Item/IfcVertexPoint/69" exists

Scenario: Add element - a structural curve member
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Name" property to "Foo"
    And I set the "Definition" property to "IfcStructuralItem"
    And I set the "Class" property to "IfcStructuralCurveMember"
    And I set the "Representation" property to "Edge"
    When I click "OK"
    And I make the collection "IfcStructuralItem" visible
    And I select the object "IfcStructuralCurveMember/Foo"
    And I toggle edit mode
    Then the object "Item/IfcEdge/72" exists

Scenario: Add element - a structural surface member
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Name" property to "Foo"
    And I set the "Definition" property to "IfcStructuralItem"
    And I set the "Class" property to "IfcStructuralSurfaceMember"
    And I set the "Representation" property to "Face"
    When I click "OK"
    And I make the collection "IfcStructuralItem" visible
    And I select the object "IfcStructuralSurfaceMember/Foo"
    And I toggle edit mode
    Then the object "Item/IfcFace/74" exists

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
