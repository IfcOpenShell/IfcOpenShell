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

Scenario: Duplicate drawing - without duplicating annotations
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
    And I press "bim.add_annotation"
    And the variable "drawing" is "IfcStore.get_file().by_type('IfcAnnotation')[0].id()"
    When I press "bim.duplicate_drawing(drawing={drawing})"
    And I select the "PLAN_VIEW-X" item in the "BIM_UL_drawinglist" list
    And I click "OUTLINER_OB_CAMERA"
    Then the object "IfcAnnotation/TEXT" is not selected
    And the object "IfcAnnotation/TEXT.001" does not exist

Scenario: Duplicate drawing - with duplicating annotations
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
    And I press "bim.add_annotation"
    And the variable "drawing" is "IfcStore.get_file().by_type('IfcAnnotation')[0].id()"
    When I press "bim.duplicate_drawing(drawing={drawing}, should_duplicate_annotations=True)"
    And I select the "PLAN_VIEW-X" item in the "BIM_UL_drawinglist" list
    And I click "OUTLINER_OB_CAMERA"
    Then the object "IfcAnnotation/TEXT" is not selected
    And the object "IfcAnnotation/TEXT.001" exists

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
    Then the file "{ifc_dir}/drawings/PLAN_VIEW.svg" should contain "cut"
    And the file "{ifc_dir}/drawings/PLAN_VIEW.svg" should contain "IfcWall"

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

Scenario: Create drawing - using shapely fill mode
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
    And I set the "location_hint" property to "My Storey"
    And I click "ADD"
    And I press "bim.expand_target_view(target_view='PLAN_VIEW')"
    When I select the "MY STOREY PLAN" item in the "BIM_UL_drawinglist" list
    And I click "OUTLINER_OB_CAMERA"
    And I look at the "Active Drawing" panel
    And I set the "Fill Mode" property to "Shapely"
    And I look at the "Drawings" panel
    And I click "OUTPUT"
    Then the file "{ifc_dir}/drawings/MY STOREY PLAN.svg" should contain "IfcWall material-null surface"

Scenario: Add sheet
    Given an empty IFC project
    And I save sample test files
    And I look at the "Sheets" panel
    And I click "IMPORT"
    When I click "ADD"
    Then the file "{ifc_dir}/layouts/A00 - UNTITLED.svg" should contain "titleblocks/A1.svg"
    And the file "{ifc_dir}/layouts/A00 - UNTITLED.svg" should not contain "GRID NORTH"

Scenario: Create sheet
    Given an empty IFC project
    And I save sample test files
    And I look at the "Sheets" panel
    And I click "IMPORT"
    And I click "ADD"
    And I select the "UNTITLED" item in the "BIM_UL_sheets" list
    When I click "OUTPUT"
    Then the file "{ifc_dir}/sheets/A00 - UNTITLED.svg" should not contain "titleblocks/A1.svg"
    And the file "{ifc_dir}/sheets/A00 - UNTITLED.svg" should contain "GRID NORTH"
    And the file "{ifc_dir}/sheets/A00 - UNTITLED.svg" should not contain "IfcWall"

Scenario: Add drawing to sheet
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
    And I click "OUTPUT"
    And I look at the "Sheets" panel
    And I click "IMPORT"
    And I click "ADD"
    And the variable "sheet" is "tool.Ifc.get().by_type('IfcDocumentInformation')[-1].id()"
    And I select the "UNTITLED" item in the "BIM_UL_sheets" list
    And I press "bim.expand_sheet(sheet={sheet})"
    When I click "IMAGE_PLANE"
    Then I can select the "PLAN_VIEW.svg" item in the "BIM_UL_sheets" list

Scenario: Create sheet - with a drawing added to it
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
    And I click "OUTPUT"
    And I look at the "Sheets" panel
    And I click "IMPORT"
    And I click "ADD"
    And the variable "sheet" is "tool.Ifc.get().by_type('IfcDocumentInformation')[-1].id()"
    And I select the "UNTITLED" item in the "BIM_UL_sheets" list
    And I press "bim.expand_sheet(sheet={sheet})"
    And I click "IMAGE_PLANE"
    When I click "OUTPUT"
    Then the file "{ifc_dir}/sheets/A00 - UNTITLED.svg" should contain "IfcWall"
