@drawing
Feature: Drawing

Scenario: Duplicate drawing
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And I save sample test files
    And I look at the "Drawings" panel
    And I click "IMPORT"
    And I click "ADD"
    And I press "bim.expand_target_view(target_view='PLAN_VIEW')"
    When I select the "PLAN_VIEW" item in the "BIM_UL_drawinglist" list
    And the variable "drawing" is "IfcStore.get_file().by_type('IfcAnnotation')[0].id()"
    When I press "bim.duplicate_drawing(drawing={drawing})"
    Then nothing happens

Scenario: Create drawing
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And I save sample test files
    And I look at the "Drawings" panel
    And I click "IMPORT"
    And I click "ADD"
    And I press "bim.expand_target_view(target_view='PLAN_VIEW')"
    When I select the "PLAN_VIEW" item in the "BIM_UL_drawinglist" list
    And I click "OUTLINER_OB_CAMERA"
    And I click "OUTPUT"
    Then nothing happens

Scenario: Create drawing after deleting a duplicated object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And I duplicate the selected objects
    And I save sample test files
    And I look at the "Drawings" panel
    And I click "IMPORT"
    And I click "ADD"
    And I press "bim.expand_target_view(target_view='PLAN_VIEW')"
    And I select the "PLAN_VIEW" item in the "BIM_UL_drawinglist" list
    And I click "OUTLINER_OB_CAMERA"
    And I click "OUTPUT"
    And the object "IfcWall/Cube" is selected
    And I delete the selected objects
    When I click "OUTPUT"
    Then nothing happens

Scenario: Activate drawing preserves visibility for non-ifc objects
    Given an empty IFC project
    And I add a cube
    And I add a cube
    And the object "Cube" is visible
    And the object "Cube.001" is not visible
    And I save sample test files
    And I look at the "Drawings" panel
    And I click "IMPORT"
    And I click "ADD"
    And I press "bim.expand_target_view(target_view='PLAN_VIEW')"
    And I select the "PLAN_VIEW" item in the "BIM_UL_drawinglist" list
    And I click "OUTLINER_OB_CAMERA"
    Then the object "Cube" is visible
    And the object "Cube.001" is not visible

Scenario: Activate drawing preserves selection
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I save sample test files
    And I look at the "Drawings" panel
    And I click "IMPORT"
    And I click "ADD"
    And I press "bim.expand_target_view(target_view='PLAN_VIEW')"
    And I select the "PLAN_VIEW" item in the "BIM_UL_drawinglist" list
    When I click "OUTLINER_OB_CAMERA"
    Then the object "Cube" is selected

Scenario: Remove drawing
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And I save sample test files
    And I look at the "Drawings" panel
    And I click "IMPORT"
    And I click "ADD"
    And I press "bim.expand_target_view(target_view='PLAN_VIEW')"
    And I select the "PLAN_VIEW" item in the "BIM_UL_drawinglist" list
    When I click "OUTLINER_OB_CAMERA"
    Then the collection "IfcAnnotation/PLAN_VIEW" exists
    When I press "bim.remove_drawing(drawing={drawing})"
    Then the collection "IfcAnnotation/PLAN_VIEW" does not exist

Scenario: Remove drawing - via object deletion
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And I press "bim.add_drawing"
    And the variable "drawing" is "IfcStore.get_file().by_type('IfcAnnotation')[0].id()"
    And the collection "IfcAnnotation/PLAN_VIEW" exists
    And the object "IfcAnnotation/PLAN_VIEW" is selected
    When I press "bim.override_object_delete"
    Then the collection "IfcAnnotation/PLAN_VIEW" does not exist

Scenario: Remove drawing - deleting active drawing
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And I save sample test files
    And I look at the "Drawings" panel
    And I click "IMPORT"
    And I click "ADD"
    And I press "bim.expand_target_view(target_view='PLAN_VIEW')"
    And I select the "PLAN_VIEW" item in the "BIM_UL_drawinglist" list
    And I click "OUTLINER_OB_CAMERA"
    When the object "IfcAnnotation/PLAN_VIEW" is selected
    And I delete the selected objects
    Then the collection "IfcAnnotation/PLAN_VIEW" does not exist

Scenario: Add annotation - text
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I save sample test files
    And I look at the "Drawings" panel
    And I click "IMPORT"
    And I click "ADD"
    And I press "bim.expand_target_view(target_view='PLAN_VIEW')"
    And I select the "PLAN_VIEW" item in the "BIM_UL_drawinglist" list
    And I click "OUTLINER_OB_CAMERA"
    When I press "bim.add_annotation"
    Then the object "IfcAnnotation/TEXT" is selected

Scenario: Add annotation - auto create context if it doesn't exist
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I save sample test files
    And I look at the "Geometric Representation Contexts" panel
    And I see "Plan"
    And I click the "X" after the text "Plan"
    And I look at the "Drawings" panel
    And I click "IMPORT"
    And I click "ADD"
    And I press "bim.expand_target_view(target_view='PLAN_VIEW')"
    And I select the "PLAN_VIEW" item in the "BIM_UL_drawinglist" list
    And I click "OUTLINER_OB_CAMERA"
    When I press "bim.add_annotation"
    Then the object "IfcAnnotation/TEXT" is selected
