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
    Then the object "IfcStructuralPointConnection/Foo" data is a "Vertex" representation of "Model/Reference/GRAPH_VIEW"
    When I make the collection "IfcStructuralItem" visible
    And I select the object "IfcStructuralPointConnection/Foo"
    And I toggle edit mode
    Then the object "Item/IfcVertexPoint/112" exists

Scenario: Add element - a structural curve member
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Name" property to "Foo"
    And I set the "Definition" property to "IfcStructuralItem"
    And I set the "Class" property to "IfcStructuralCurveMember"
    And I set the "Representation" property to "Edge"
    When I click "OK"
    Then the object "IfcStructuralCurveMember/Foo" data is a "Edge" representation of "Model/Reference/GRAPH_VIEW"
    When I make the collection "IfcStructuralItem" visible
    And I select the object "IfcStructuralCurveMember/Foo"
    And I toggle edit mode
    Then the object "Item/IfcEdge/115" exists

Scenario: Add element - a structural surface member
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Name" property to "Foo"
    And I set the "Definition" property to "IfcStructuralItem"
    And I set the "Class" property to "IfcStructuralSurfaceMember"
    And I set the "Representation" property to "Face"
    When I click "OK"
    Then the object "IfcStructuralSurfaceMember/Foo" data is a "Face" representation of "Model/Reference/GRAPH_VIEW"
    When I make the collection "IfcStructuralItem" visible
    And I select the object "IfcStructuralSurfaceMember/Foo"
    And I toggle edit mode
    Then the object "Item/IfcFaceSurface/134" exists

Scenario: Add structural item - a curve member of the chosen predefined type in the current model
    Given an empty IFC project
    And I press "bim.add_structural_analysis_model"
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralCurveMember"
    And I set "scene.BIMStructuralProperties.structural_item_predefined_type" to "PIN_JOINED_MEMBER"
    When I press "bim.add_structural_item"
    Then the object "IfcStructuralCurveMember/Unnamed" is an "IfcStructuralCurveMember"
    And the object "IfcStructuralCurveMember/Unnamed" data is a "Edge" representation of "Model/Reference/GRAPH_VIEW"
    And I evaluate expression "assert tool.Ifc.get().by_type('IfcStructuralCurveMember')[0].PredefinedType == 'PIN_JOINED_MEMBER'"
    And I evaluate expression "assert tool.Ifc.get().by_type('IfcStructuralCurveMember')[0].HasAssignments[0].RelatingGroup.is_a('IfcStructuralAnalysisModel')"

Scenario: Add structural item - a surface member
    Given an empty IFC project
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralSurfaceMember"
    When I press "bim.add_structural_item"
    Then the object "IfcStructuralSurfaceMember/Unnamed" data is a "Face" representation of "Model/Reference/GRAPH_VIEW"

Scenario: Add structural item - a point connection, which has no predefined type
    Given an empty IFC project
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralPointConnection"
    When I press "bim.add_structural_item"
    Then the object "IfcStructuralPointConnection/Unnamed" data is a "Vertex" representation of "Model/Reference/GRAPH_VIEW"

Scenario: Add structural item - a curve connection
    Given an empty IFC project
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralCurveConnection"
    When I press "bim.add_structural_item"
    Then the object "IfcStructuralCurveConnection/Unnamed" data is a "Edge" representation of "Model/Reference/GRAPH_VIEW"

Scenario: Add structural item - with the Structural Tool hotkey
    Given an empty IFC project
    And I set "scene.BIMStructuralProperties.structural_item_class" to "IfcStructuralPointConnection"
    When I press "bim.structural_hotkey(hotkey='S_A')"
    Then the object "IfcStructuralPointConnection/Unnamed" is an "IfcStructuralPointConnection"

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

Scenario: Enable editing structural load group activities
    Given an empty IFC project
    And the variable "member" is "ifcopenshell.api.root.create_entity({ifc}, ifc_class='IfcStructuralCurveMember', name='Beam').id()"
    And the variable "load" is "ifcopenshell.api.structural.add_structural_load({ifc}, name='Wind', ifc_class='IfcStructuralLoadLinearForce').id()"
    And the variable "activity" is "ifcopenshell.api.structural.add_structural_activity({ifc}, applied_load={ifc}.by_id({load}), structural_member={ifc}.by_id({member}), ifc_class='IfcStructuralCurveAction').id()"
    And the variable "load_group" is "ifcopenshell.api.structural.add_structural_load_group({ifc}, name='Wind').id()"
    And I evaluate expression "ifcopenshell.api.group.assign_group({ifc}, products=[{ifc}.by_id({activity})], group={ifc}.by_id({load_group}))"
    When I press "bim.enable_editing_structural_load_group_activities(load_group={load_group})"
    Then "scene.BIMStructuralProperties.load_group_activities[0].name" is "Wind on Beam"
    And "scene.BIMStructuralProperties.load_group_activities[0].applied_load_class" is "IfcStructuralLoadLinearForce"

Scenario: Enable editing structural load group activities - an activity assigned to no item
    Given an empty IFC project
    And the variable "load" is "ifcopenshell.api.structural.add_structural_load({ifc}, name='Wind', ifc_class='IfcStructuralLoadSingleForce').id()"
    And the variable "activity" is "ifcopenshell.api.root.create_entity({ifc}, ifc_class='IfcStructuralPointAction').id()"
    And I evaluate expression "{ifc}.by_id({activity}).AppliedLoad = {ifc}.by_id({load})"
    And the variable "load_group" is "ifcopenshell.api.structural.add_structural_load_group({ifc}, name='Wind').id()"
    And I evaluate expression "ifcopenshell.api.group.assign_group({ifc}, products=[{ifc}.by_id({activity})], group={ifc}.by_id({load_group}))"
    When I press "bim.enable_editing_structural_load_group_activities(load_group={load_group})"
    Then "scene.BIMStructuralProperties.load_group_activities[0].name" is "Wind on Unnamed"
