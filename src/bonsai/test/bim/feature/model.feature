@model
Feature: Model

Scenario: Add type instance - add from a mesh
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "cube" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{cube}"
    When I press "bim.add_occurrence"
    Then the object "IfcWall/Wall" exists

Scenario: Add type instance - add from an empty
    Given an empty IFC project
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "empty" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{empty}"
    When I press "bim.add_occurrence"
    Then the object "IfcWall/Wall" exists

Scenario: Add type instance - add a mesh where existing instances have changed context
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "cube" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{cube}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" data is a "Tessellation" representation of "Model/Body/MODEL_VIEW"
    And the object "IfcWall/Wall" is selected
    And the variable "context" is "[c for c in {ifc}.by_type('IfcGeometricRepresentationSubContext') if c.ContextType == 'Plan' and c.ContextIdentifier == 'Body' and c.TargetView == 'PLAN_VIEW'][0].id()"
    And I set "active_object.BIMGeometryProperties.contexts" to "{context}"
    And I press "bim.add_representation"
    And the object "IfcWall/Wall" data is a "Annotation2D" representation of "Plan/Body/PLAN_VIEW"
    When I press "bim.add_occurrence"
    Then the object "IfcWall/Wall" data is a "Annotation2D" representation of "Plan/Body/PLAN_VIEW"
    And the object "IfcWall/Wall.001" data is a "Annotation2D" representation of "Plan/Body/PLAN_VIEW"

Scenario: Add one type from the Construction Type Browser
    Given an empty IFC project
    And I load the demo construction library
    When I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    Then the object "IfcColumn/Column" exists

Scenario: Add grid
    Given an empty IFC project
    When I press "bim.add_grid"
    Then the object "IfcGrid/Grid" is an "IfcGrid"
    And the object "IfcGridAxis/A" is an "IfcGridAxis"
    And the object "IfcGridAxis/B" is an "IfcGridAxis"
    And the object "IfcGridAxis/C" is an "IfcGridAxis"
    And the object "IfcGridAxis/01" is an "IfcGridAxis"
    And the object "IfcGridAxis/02" is an "IfcGridAxis"
    And the object "IfcGridAxis/03" is an "IfcGridAxis"

Scenario: Add a wall
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    When I press "bim.add_occurrence"
    Then the object "IfcWall/Wall" is an "IfcWall"
    And the object "IfcWall/Wall" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0,0,0"

Scenario: Extend a wall to the cursor
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And the cursor is at "2,0,0"
    When I press "bim.hotkey(hotkey='S_E')"
    Then the object "IfcWall/Wall" dimensions are "2,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0,0,0"

Scenario: Add a wall perpendicular to an existing wall
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the cursor is at "0.5,0,0"
    When I press "bim.add_occurrence"
    Then the object "IfcWall/Wall" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0,0,0"
    And the object "IfcWall/Wall.001" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall.001" bottom left corner is at "0.5,0,0"
    And the object "IfcWall/Wall.001" top right corner is at "0.6,-1,3"

Scenario: Extend one wall to another
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the cursor is at "0.5,0,0"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall.001" is moved to "0.5,-1,0"
    And the object "IfcWall/Wall.001" is selected
    And additionally the object "IfcWall/Wall" is selected
    When I press "bim.hotkey(hotkey='S_E')"
    Then the object "IfcWall/Wall" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0,0,0"
    And the object "IfcWall/Wall.001" dimensions are "2,0.1,3"
    And the object "IfcWall/Wall.001" bottom left corner is at "0.5,0,0"
    And the object "IfcWall/Wall.001" top right corner is at "0.6,-2,3"

Scenario: Join two walls with a mitre joint
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the cursor is at "0.7,0,0"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall.001" is selected
    And additionally the object "IfcWall/Wall" is selected
    When I press "bim.hotkey(hotkey='S_T')"
    Then the object "IfcWall/Wall" dimensions are "0.8,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0.0,0,0"
    And the object "IfcWall/Wall.001" dimensions are "1.1,0.1,3"
    And the object "IfcWall/Wall.001" bottom left corner is at "0.7,0.1,0"
    And the object "IfcWall/Wall.001" top right corner is at "0.8,-1,3"

Scenario: Change the height of a wall
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And I set "scene.BIMModelProperties.extrusion_depth" to "2.0"
    When I press "bim.change_extrusion_depth(depth=2.0)"
    Then the object "IfcWall/Wall" dimensions are "1,0.1,2"

Scenario: Change the length of a wall
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And I set "scene.BIMModelProperties.length" to "2.0"
    When I press "bim.change_layer_length(length=2.0)"
    Then the object "IfcWall/Wall" dimensions are "2,0.1,3"

Scenario: Flip a wall
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    When I press "bim.hotkey(hotkey='S_F')"
    Then the object "IfcWall/Wall" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0,0,0"
    And the object "IfcWall/Wall" top right corner is at "1,0.1,3"

Scenario: Split a wall
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And the cursor is at "0.5,0,0"
    When I press "bim.hotkey(hotkey='S_K')"
    Then the object "IfcWall/Wall" is an "IfcWall"
    And the object "IfcWall/Wall.001" is an "IfcWall"
    And the object "IfcWall/Wall" dimensions are "0.5,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0,0,0"
    And the object "IfcWall/Wall" top right corner is at "0.5,0.1,3"
    And the object "IfcWall/Wall.001" dimensions are "0.5,0.1,3"
    And the object "IfcWall/Wall.001" bottom left corner is at "0.5,0,0"
    And the object "IfcWall/Wall.001" top right corner is at "1,0.1,3"

Scenario: Rotate a wall by 90 degrees
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    When I press "bim.hotkey(hotkey='S_R')"
    Then the object "IfcWall/Wall" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0,0,0"
    And the object "IfcWall/Wall" top right corner is at "-0.1,1,3"

Scenario: Regenerate a wall - after doing nothing interesting
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    When I press "bim.hotkey(hotkey='S_G')"
    Then the object "IfcWall/Wall" is an "IfcWall"
    And the object "IfcWall/Wall" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0,0,0"

Scenario: Insert door into wall
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And the cursor is at "10,0,0"
    # Extend the wall
    And I press "bim.hotkey(hotkey='S_E')"
    When I set "scene.BIMModelProperties.ifc_class" to "IfcDoorType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcDoorType') if e.Name == 'DT01'][0].id()"
    And the cursor is at "7,0,0"
    And I press "bim.add_occurrence"
    Then the object "IfcDoor/Door" is at "7,0,0"
    And the object "IfcWall/Wall" is filled by "IfcDoor/Door"

Scenario: Flip a door inserted in a wall
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And the cursor is at "10,0,0"
    # Extend the wall
    And I press "bim.hotkey(hotkey='S_E')"
    # Insert a door
    And I set "scene.BIMModelProperties.ifc_class" to "IfcDoorType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcDoorType') if e.Name == 'DT01'][0].id()"
    And the cursor is at "7,0,0"
    And I press "bim.add_occurrence"
    When the object "IfcDoor/Door" is selected
    And I press "bim.hotkey(hotkey='S_F')"
    Then the object "IfcDoor/Door" is at "8.01,0.1,0"

Scenario: Split a wall which has a flipped door
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And the cursor is at "10,0,0"
    # Extend the wall
    And I press "bim.hotkey(hotkey='S_E')"
    # Insert a door
    And I set "scene.BIMModelProperties.ifc_class" to "IfcDoorType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcDoorType') if e.Name == 'DT01'][0].id()"
    And the cursor is at "7,0,0"
    And I press "bim.add_occurrence"
    # Flip the door
    And the object "IfcDoor/Door" is selected
    And I press "bim.hotkey(hotkey='S_F')"
    When the cursor is at "5,0,0"
    And the object "IfcWall/Wall" is selected
    And I press "bim.hotkey(hotkey='S_K')"
    Then the object "IfcDoor/Door" is at "8.01,0.1,0"
    And the object "IfcWall/Wall.001" is filled by "IfcDoor/Door"

Scenario: Offset walls
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    When the object "IfcWall/Wall" is selected
    And I set "scene.BIMModelProperties.offset_type_vertical" to "EXTERIOR"
    And I press "bim.offset_walls"
    Then the object "IfcWall/Wall" bottom left corner is at "0,0,0"
    And the object "IfcWall/Wall" top right corner is at "1,0.1,3"
    When I set "scene.BIMModelProperties.offset_type_vertical" to "INTERIOR"
    And I press "bim.offset_walls"
    Then the object "IfcWall/Wall" bottom left corner is at "0,-0.1,0"
    And the object "IfcWall/Wall" top right corner is at "1,0,3"
    When I set "scene.BIMModelProperties.offset_type_vertical" to "CENTER"
    And I press "bim.offset_walls"
    Then the object "IfcWall/Wall" bottom left corner is at "0,-0.05,0"
    And the object "IfcWall/Wall" top right corner is at "1,0.05,3"

Scenario: Align walls
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL300'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And the cursor is at "10,5,0"
    And I press "bim.add_occurrence"
    When the object "IfcWall/Wall.001" is selected
    And additionally the object "IfcWall/Wall" is selected
    And I press "bim.hotkey(hotkey='S_C')"
    Then the object "IfcWall/Wall" bottom left corner is at "0,0,0"
    And the object "IfcWall/Wall" top right corner is at "1,0.1,3"
    And the object "IfcWall/Wall.001" bottom left corner is at "10,-0.1,0"
    And the object "IfcWall/Wall.001" top right corner is at "11,0.2,3"
    When I press "bim.hotkey(hotkey='S_V')"
    Then the object "IfcWall/Wall" bottom left corner is at "0,0,0"
    And the object "IfcWall/Wall" top right corner is at "1,0.1,3"
    And the object "IfcWall/Wall.001" bottom left corner is at "10,-0.2,0"
    And the object "IfcWall/Wall.001" top right corner is at "11,0.1,3"
    When I press "bim.hotkey(hotkey='S_X')"
    Then the object "IfcWall/Wall" bottom left corner is at "0,0,0"
    And the object "IfcWall/Wall" top right corner is at "1,0.1,3"
    And the object "IfcWall/Wall.001" bottom left corner is at "10,0,0"
    And the object "IfcWall/Wall.001" top right corner is at "11,0.3,3"

Scenario: Align walls - centerline fail due to selection criteria
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    When the object "IfcWall/Wall" is selected
    Then I press "bim.hotkey(hotkey='S_C')" and expect error "Error: At least two vertically layered elements must be selected to match alignments."

Scenario: Align elements
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcDoorType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcDoorType') if e.Name == 'DT01'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the cursor is at "10,5,0"
    And I press "bim.add_occurrence"
    And the object "IfcDoor/Door.001" is rotated by "0,0,90" deg
    When the object "IfcDoor/Door.001" is selected
    And additionally the object "IfcDoor/Door" is selected
    And I press "bim.hotkey(hotkey='S_C')"
    Then the object "IfcDoor/Door" bottom left corner is at "0,0,0"
    And the object "IfcDoor/Door" top right corner is at "1.01,0.1,2.145"
    And the object "IfcDoor/Door.001" bottom left corner is at "10,-0.455,0"
    And the object "IfcDoor/Door.001" top right corner is at "9.9,0.555,2.145"
    When I press "bim.hotkey(hotkey='S_V')"
    Then the object "IfcDoor/Door" bottom left corner is at "0,0,0"
    And the object "IfcDoor/Door" top right corner is at "1.01,0.1,2.145"
    And the object "IfcDoor/Door.001" bottom left corner is at "10,-0.910,0"
    And the object "IfcDoor/Door.001" top right corner is at "9.9,0.1,2.145"
    When I press "bim.hotkey(hotkey='S_X')"
    Then the object "IfcDoor/Door" bottom left corner is at "0,0,0"
    And the object "IfcDoor/Door" top right corner is at "1.01,0.1,2.145"
    And the object "IfcDoor/Door.001" bottom left corner is at "10,0,0"
    And the object "IfcDoor/Door.001" top right corner is at "9.9,1.01,2.145"

Scenario: Align elements - fail due to selection criteria
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcDoorType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcDoorType') if e.Name == 'DT01'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    When the object "IfcDoor/Door" is selected
    Then I press "bim.hotkey(hotkey='S_C')" and expect error "Error: At least two objects must be selected to match alignments."

Scenario: Add a slab
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcSlabType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcSlabType') if e.Name == 'FLR200'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    When I press "bim.add_occurrence"
    Then the object "IfcSlab/Slab" is an "IfcSlab"
    And the object "IfcSlab/Slab" dimensions are "1,1,0.2"
    And the object "IfcSlab/Slab" bottom left corner is at "0,0,0"
    And the object "IfcSlab/Slab" top right corner is at "1,1,0.2"

Scenario: Extend walls to underside
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And I set "scene.BIMModelProperties.ifc_class" to "IfcSlabType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcSlabType') if e.Name == 'FLR200'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcSlab/Slab" is moved to "0,0,2.5"
    When the object "IfcWall/Wall" is selected
    And additionally the object "IfcSlab/Slab" is selected
    And I look at the tool header
    And I click "Extend To Underside"
    Then the object "IfcWall/Wall" dimensions are "1,0.1,2.5"

Scenario: Extend walls to underside - extending to a tessellated gable roof
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    # Create gable roof: a cube turned into a prism with a ridge.
    And I add a cube of size "1" at "0.5,0.05,3"
    And the object "Cube" is selected
    And I evaluate expression "obj = bpy.context.active_object; [setattr(v.co, 'y', 0) for v in obj.data.vertices if v.co.z > 0]"
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcRoof"
    And I press "bim.assign_class"
    When the object "IfcWall/Wall" is selected
    And additionally the object "IfcRoof/Cube" is selected
    And I look at the tool header
    And I click "Extend To Underside"
    Then the object "IfcWall/Wall" dimensions are "1,0.1,2.5"

Scenario: Enable editing a slab profile
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcSlabType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcSlabType') if e.Name == 'FLR200'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcSlab/Slab" is selected
    When I press "bim.hotkey(hotkey='S_E')"
    Then the object "IfcSlab/Slab" dimensions are "1,1,0"
    And the object "IfcSlab/Slab" bottom left corner is at "0,0,0"
    And the object "IfcSlab/Slab" top right corner is at "1,1,0"

Scenario: Disable editing a slab profile
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcSlabType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcSlabType') if e.Name == 'FLR200'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcSlab/Slab" is selected
    And I press "bim.hotkey(hotkey='S_E')"
    When I press "bim.disable_editing_extrusion_profile"
    Then the object "IfcSlab/Slab" dimensions are "1,1,0.2"
    And the object "IfcSlab/Slab" bottom left corner is at "0,0,0"
    And the object "IfcSlab/Slab" top right corner is at "1,1,0.2"

Scenario: Edit a slab profile
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcSlabType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcSlabType') if e.Name == 'FLR200'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcSlab/Slab" is selected
    And I press "bim.hotkey(hotkey='S_E')"
    When I press "bim.edit_extrusion_profile"
    Then the object "IfcSlab/Slab" dimensions are "1,1,0.2"
    And the object "IfcSlab/Slab" bottom left corner is at "0,0,0"
    And the object "IfcSlab/Slab" top right corner is at "1,1,0.2"

Scenario: Add a beam
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcBeamType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcBeamType') if e.Name == 'B1'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    When I press "bim.add_occurrence"
    Then the object "IfcBeam/Beam" is an "IfcBeam"
    And the object "IfcBeam/Beam" dimensions are "0.1,0.2,3"
    And the object "IfcBeam/Beam" bottom left corner is at "0,-0.05,-0.1"
    And the object "IfcBeam/Beam" top right corner is at "3,0.05,0.1"

Scenario: Extend a beam to the cursor
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcBeamType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcBeamType') if e.Name == 'B1'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcBeam/Beam" is selected
    And the cursor is at "2,0,0"
    When I press "bim.hotkey(hotkey='S_E')"
    Then the object "IfcBeam/Beam" dimensions are "0.1,0.2,2"
    And the object "IfcBeam/Beam" bottom left corner is at "0,-0.05,-0.1"

Scenario: Extend one beam to another
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcBeamType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcBeamType') if e.Name == 'B1'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the cursor is at "1,1,0"
    And I press "bim.add_occurrence"
    And the object "IfcBeam/Beam.001" is selected
    And I press "bim.hotkey(hotkey='S_R')"
    And the object "IfcBeam/Beam.001" is selected
    And additionally the object "IfcBeam/Beam" is selected
    When I press "bim.hotkey(hotkey='S_E')"
    Then the object "IfcBeam/Beam" dimensions are "0.1,0.2,3"
    And the object "IfcBeam/Beam" bottom left corner is at "0,-0.05,-0.1"
    And the object "IfcBeam/Beam" top right corner is at "3,0.05,0.1"
    And the object "IfcBeam/Beam.001" dimensions are "0.1,0.2,3.95"
    And the object "IfcBeam/Beam.001" bottom left corner is at "1.05,0.05,-0.1"
    And the object "IfcBeam/Beam.001" top right corner is at "0.95,4,0.1"

Scenario: Join two beams with a butt joint - first beam has priority
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcBeamType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcBeamType') if e.Name == 'B1'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the cursor is at "1,1,0"
    And I press "bim.add_occurrence"
    And the object "IfcBeam/Beam.001" is selected
    And I press "bim.hotkey(hotkey='S_R')"
    And the object "IfcBeam/Beam.001" is selected
    And additionally the object "IfcBeam/Beam" is selected
    When I press "bim.hotkey(hotkey='S_T')"
    Then the object "IfcBeam/Beam" dimensions are "0.1,0.2,1.95"
    And the object "IfcBeam/Beam" bottom left corner is at "1.05,-0.05,-0.1"
    And the object "IfcBeam/Beam" top right corner is at "3,0.05,0.1"
    And the object "IfcBeam/Beam.001" dimensions are "0.1,0.2,4.05"
    And the object "IfcBeam/Beam.001" bottom left corner is at "1.05,-0.05,-0.1"
    And the object "IfcBeam/Beam.001" top right corner is at "0.95,4,0.1"

Scenario: Join two beams with a butt joint - second beam has priority
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcBeamType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcBeamType') if e.Name == 'B1'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the cursor is at "1,1,0"
    And I press "bim.add_occurrence"
    And the object "IfcBeam/Beam.001" is selected
    And I press "bim.hotkey(hotkey='S_R')"
    And the object "IfcBeam/Beam" is selected
    And additionally the object "IfcBeam/Beam.001" is selected
    When I press "bim.hotkey(hotkey='S_T')"
    Then the object "IfcBeam/Beam" dimensions are "0.1,0.2,2.05"
    And the object "IfcBeam/Beam" bottom left corner is at "0.95,-0.05,-0.1"
    And the object "IfcBeam/Beam" top right corner is at "3,0.05,0.1"
    And the object "IfcBeam/Beam.001" dimensions are "0.1,0.2,3.95"
    And the object "IfcBeam/Beam.001" bottom left corner is at "1.05,0.05,-0.1"
    And the object "IfcBeam/Beam.001" top right corner is at "0.95,4,0.1"

Scenario: Join two beams with a mitre joint
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcBeamType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcBeamType') if e.Name == 'B1'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the cursor is at "1,1,0"
    And I press "bim.add_occurrence"
    And the object "IfcBeam/Beam.001" is selected
    And I press "bim.hotkey(hotkey='S_R')"
    And the object "IfcBeam/Beam" is selected
    And additionally the object "IfcBeam/Beam.001" is selected
    When I press "bim.hotkey(hotkey='S_Y')"
    Then the object "IfcBeam/Beam" dimensions are "0.1,0.2,2.05"
    And the object "IfcBeam/Beam" bottom left corner is at "0.95,-0.05,-0.1"
    And the object "IfcBeam/Beam" top right corner is at "3,0.05,0.1"
    And the object "IfcBeam/Beam.001" dimensions are "0.1,0.2,4.05"
    And the object "IfcBeam/Beam.001" bottom left corner is at "1.05,-0.05,-0.1"
    And the object "IfcBeam/Beam.001" top right corner is at "0.95,4,0.1"

Scenario: Change the length of a beam
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcBeamType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcBeamType') if e.Name == 'B1'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcBeam/Beam" is selected
    And I set "scene.BIMModelProperties.extrusion_depth" to "2.0"
    When I press "bim.change_profile_depth(depth=2.0)"
    Then the object "IfcBeam/Beam" dimensions are "0.1,0.2,2"

Scenario: Rotate a beam by 90 degrees
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcBeamType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcBeamType') if e.Name == 'B1'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcBeam/Beam" is selected
    When I press "bim.hotkey(hotkey='S_R')"
    Then the object "IfcBeam/Beam" dimensions are "0.1,0.2,3"
    And the object "IfcBeam/Beam" bottom left corner is at "0.05,0,-0.1"
    And the object "IfcBeam/Beam" top right corner is at "-0.05,3,0.1"

Scenario: Regenerate a beam - after doing nothing interesting
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcBeamType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcBeamType') if e.Name == 'B1'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcBeam/Beam" is selected
    When I press "bim.hotkey(hotkey='S_G')"
    Then the object "IfcBeam/Beam" dimensions are "0.1,0.2,3"
    And the object "IfcBeam/Beam" bottom left corner is at "0,-0.05,-0.1"
    And the object "IfcBeam/Beam" top right corner is at "3,0.05,0.1"

Scenario: Undo test - create a wall and couple windows and undo the last window
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And I press "bim.add_occurrence"
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWindowType"
    And I press "bim.add_occurrence"
    And I prepare to undo
    And the object "IfcWall/Wall" is selected
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWindowType"
    And I press "bim.add_occurrence"
    And I undo
    Then nothing happens

Scenario: Undo test - create a wall with window opening, flip it and undo
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And I press "bim.add_occurrence"
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWindowType"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And I prepare to undo
    And I press "bim.hotkey(hotkey='S_F')"
    And I undo
    Then nothing happens

Scenario: Create window type based on window modifier, add an occurrence of it and edit it
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Class" property to "IfcWindowType"
    And I set the "Predefined Type" property to "WINDOW"
    And I set the "Representation" property to "Window"
    When I click "OK"
    And I press "bim.add_occurrence"
    And I press "bim.enable_editing_window()"
    And I press "bim.finish_editing_window()"
    Then nothing happens

Scenario: Create door type based on door modifier, add an occurrence of it and edit it
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Class" property to "IfcDoorType"
    And I set the "Predefined Type" property to "DOOR"
    And I set the "Representation" property to "Door"
    When I click "OK"
    And I press "bim.add_occurrence"
    And I press "bim.enable_editing_door()"
    And I press "bim.finish_editing_door()"
    Then nothing happens

Scenario: Saving with a door mid-edit auto-commits the draft value to the IFC pset
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Class" property to "IfcDoorType"
    And I set the "Predefined Type" property to "DOOR"
    And I set the "Representation" property to "Door"
    When I click "OK"
    And I press "bim.add_occurrence"
    And I press "bim.enable_editing_door()"
    And I set "active_object.BIMDoorProperties.overall_height" to "2.5"
    Then "active_object.BIMDoorProperties.is_editing" is "True"
    When I press "bim.save_project(filepath='{temp_project_path}', should_save_as=True)"
    Then "active_object.BIMDoorProperties.is_editing" is "False"
    # BBIM_<Type> psets store project units, not raw Blender SI. The empty project
    # used in an_empty_blender_session is METRIC_MM, so 2.5 m → 2500 mm in the pset.
    And the variable "saved_height" is "__import__('json').loads(ifcopenshell.util.element.get_pset({ifc}.by_type('IfcDoor')[0], 'BBIM_Door', 'Data'))['overall_height']"
    And the variable "saved_height" equals "2500.0"

Scenario: Saving with no parametric edits in progress leaves the door pset unchanged
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Class" property to "IfcDoorType"
    And I set the "Predefined Type" property to "DOOR"
    And I set the "Representation" property to "Door"
    When I click "OK"
    And I press "bim.add_occurrence"
    And the variable "pre_save_height" is "__import__('json').loads(ifcopenshell.util.element.get_pset({ifc}.by_type('IfcDoor')[0], 'BBIM_Door', 'Data'))['overall_height']"
    When I press "bim.save_project(filepath='{temp_project_path}', should_save_as=True)"
    Then the variable "post_save_height" is "__import__('json').loads(ifcopenshell.util.element.get_pset({ifc}.by_type('IfcDoor')[0], 'BBIM_Door', 'Data'))['overall_height']"
    And the variable "post_save_height" equals "{pre_save_height}"

Scenario: Saving with a wall mid-edit auto-commits the draft to IFC
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And I press "bim.enable_editing_wall()"
    Then "active_object.BIMWallProperties.is_editing" is "True"
    When I press "bim.save_project(filepath='{temp_project_path}', should_save_as=True)"
    Then "active_object.BIMWallProperties.is_editing" is "False"

Scenario: Enabling and finishing a wall edit with no drag is a no-op
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And the variable "entity_count_before" is "len(list({ifc}))"
    When I press "bim.enable_editing_wall()"
    And I press "bim.finish_editing_wall()"
    Then "active_object.BIMWallProperties.is_editing" is "False"
    And the variable "entity_count_after" is "len(list({ifc}))"
    And the variable "entity_count_after" equals "{entity_count_before}"

Scenario: Cancelling a wall edit clears is_editing
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "cube" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{cube}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And I press "bim.enable_editing_wall()"
    When I press "bim.cancel_editing_wall()"
    Then "active_object.BIMWallProperties.is_editing" is "False"

Scenario: Wall parametric edit works on IFC2X3 projects
    Given an empty IFC2X3 project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    When I press "bim.enable_editing_wall()"
    Then "active_object.BIMWallProperties.is_editing" is "True"
    When I press "bim.finish_editing_wall()"
    Then "active_object.BIMWallProperties.is_editing" is "False"

Scenario: Rotate a wall 90° via bim.rotate_wall_90
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    When I press "bim.rotate_wall_90()"
    Then the object "IfcWall/Wall" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0,0,0"
    And the object "IfcWall/Wall" top right corner is at "-0.1,1,3"

Scenario: Splitting a wall with another wall mid-edit commits the pending edit first
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And I press "bim.enable_editing_wall()"
    Then "active_object.BIMWallProperties.is_editing" is "True"
    When I press "bim.split_wall()"
    Then "active_object.BIMWallProperties.is_editing" is "False"

Scenario: Create a door, undo and create a new door
    Given an empty IFC project
    And I prepare to undo
    And I press "mesh.add_door()"
    And I undo
    And I press "mesh.add_door()"
    Then nothing happens
    And the object "IfcDoor/IfcDoor" exists

Scenario: Create a MEP transition
    Given an empty IFC project
    And I create default MEP types
    And the variable "segment_types" is "[str(e.id()) for e in {ifc}.by_type('IfcDuctSegmentType')]"

    And I set "scene.BIMModelProperties.ifc_class" to "IfcDuctSegmentType"
    And I set "scene.BIMModelProperties.relating_type_id" to "{segment_types}[0]"
    And I press "bim.add_occurrence"
    And I rename the object "IfcDuctSegment/DuctSegment" to "IfcDuctSegment/RectSegment"

    And I set "scene.BIMModelProperties.relating_type_id" to "{segment_types}[1]"
    And I press "bim.add_occurrence"
    And I rename the object "IfcDuctSegment/DuctSegment" to "IfcDuctSegment/CircleSegment"

    And the object "IfcDuctSegment/RectSegment" is moved to "0,0,0"
    And the object "IfcDuctSegment/CircleSegment" is moved to "2.5,0,0"
    And the object "IfcDuctSegment/CircleSegment" is selected
    And additionally the object "IfcDuctSegment/RectSegment" is selected
    And I press "bim.mep_add_transition"

    Then the object "IfcDuctFitting/DuctFitting" exists
    And the object "IfcDuctFittingType/Transition" exists
    And the object "IfcDuctSegment/RectSegment" is at "0,0,0"
    And the object "IfcDuctSegment/RectSegment" dimensions are "0.4,0.2,2.370096"
    And the object "IfcDuctSegment/CircleSegment" is at "3.1299,0,0"
    And the object "IfcDuctSegment/CircleSegment" dimensions are "0.1000, 0.09927, 2.370096"
    And the object "IfcDuctFitting/DuctFitting" is at "2.370096, 0.0000, 0.0000"
    And the object "IfcDuctFitting/DuctFitting" dimensions are "0.4000, 0.2000, 0.759807"

Scenario: Create a MEP bend between intersecting with different locations
    Given an empty IFC project
    And I create default MEP types
    And the variable "segment_types" is "[str(e.id()) for e in {ifc}.by_type('IfcDuctSegmentType')]"

    And I set "scene.BIMModelProperties.ifc_class" to "IfcDuctSegmentType"
    And I set "scene.BIMModelProperties.relating_type_id" to "{segment_types}[0]"
    And I set "scene.BIMModelProperties.extrusion_depth" to "5.0"
    And I press "bim.add_occurrence"
    And I rename the object "IfcDuctSegment/DuctSegment" to "IfcDuctSegment/Seg1"

    And I set "scene.BIMModelProperties.relating_type_id" to "{segment_types}[0]"
    And I press "bim.add_occurrence"
    And I rename the object "IfcDuctSegment/DuctSegment" to "IfcDuctSegment/Seg2"
    And the object "IfcDuctSegment/Seg2" is rotated by "0,0,90" deg

    And the object "IfcDuctSegment/Seg2" is moved to "6,1,1"
    And the object "IfcDuctSegment/Seg1" is selected
    And additionally the object "IfcDuctSegment/Seg2" is selected
    And I press "bim.mep_add_bend"

    Then the object "IfcDuctFitting/DuctFitting" exists
    And the object "IfcDuctFittingType/Bend" exists
    And the object "IfcDuctSegment/Seg1" is at "0,0,1.0"
    And the object "IfcDuctSegment/Seg1" dimensions are "0.4,0.2,5.5"
    And the object "IfcDuctSegment/Seg2" is at "6.0,0.5,1.0"
    And the object "IfcDuctSegment/Seg2" dimensions are "0.4,0.2,5.5"
    And the object "IfcDuctFitting/DuctFitting" is at "6.0, 0.5, 1.0"
    And the object "IfcDuctFitting/DuctFitting" dimensions are "0.7, 0.2, 0.7"

Scenario: Create a MEP bend between intersecting segments at the same location
    Given an empty IFC project
    And I create default MEP types
    And the variable "segment_types" is "[str(e.id()) for e in {ifc}.by_type('IfcDuctSegmentType')]"

    And I set "scene.BIMModelProperties.ifc_class" to "IfcDuctSegmentType"
    And I set "scene.BIMModelProperties.relating_type_id" to "{segment_types}[0]"
    And I set "scene.BIMModelProperties.extrusion_depth" to "5.0"
    And I press "bim.add_occurrence"
    And I rename the object "IfcDuctSegment/DuctSegment" to "IfcDuctSegment/Seg1"

    And I set "scene.BIMModelProperties.relating_type_id" to "{segment_types}[0]"
    And I press "bim.add_occurrence"
    And I rename the object "IfcDuctSegment/DuctSegment" to "IfcDuctSegment/Seg2"
    And the object "IfcDuctSegment/Seg2" is rotated by "0,0,90" deg

    And the object "IfcDuctSegment/Seg1" is selected
    And additionally the object "IfcDuctSegment/Seg2" is selected
    And I press "bim.mep_add_bend"

    Then the object "IfcDuctFitting/DuctFitting" exists
    And the object "IfcDuctFittingType/Bend" exists
    And the object "IfcDuctSegment/Seg1" is at "0.5,0,1.0"
    And the object "IfcDuctSegment/Seg1" dimensions are "0.4,0.2,4.5"
    And the object "IfcDuctSegment/Seg2" is at "0.0,0.5,1.0"
    And the object "IfcDuctSegment/Seg2" dimensions are "0.4,0.2,4.5"
    And the object "IfcDuctFitting/DuctFitting" is at "0.0, 0.5, 1.0"
    And the object "IfcDuctFitting/DuctFitting" dimensions are "0.7, 0.2, 0.7"

Scenario: Generate a space from cursor location
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the cursor is at "1.1,0,0"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall.001" is selected
    And I press "bim.hotkey(hotkey='S_R')"
    And the cursor is at "0,.9,0"
    And I press "bim.add_occurrence"
    And the cursor is at "-1,0,0"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall.003" is selected
    And I press "bim.hotkey(hotkey='S_R')"
    And the object "IfcWall/Wall.003" is moved to "0,0,0"
    When the cursor is at "0.5,0.5,0"
    And I deselect all objects
    And I press "bim.generate_space"
    Then the object "IfcSpace/Space" exists
    And the object "IfcSpace/Space" dimensions are "1,0.8,3"

Scenario: Add and edit parametric stair
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcStairFlight"
    And I click "Assign IFC Class"
    And I look at the "Stair" panel
    And I click "ADD"
    And I look at the "Stair" panel
    And I click "GREASEPENCIL"
    And I look at the "Stair" panel
    And I click "CHECKMARK"

Scenario: Add and edit parametric window
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWindow"
    And I click "Assign IFC Class"
    And I look at the "BIM_PT_window" panel
    And I click "ADD"
    And I look at the "BIM_PT_window" panel
    And I click "GREASEPENCIL"
    And I look at the "BIM_PT_window" panel
    And I click "CHECKMARK"

Scenario: Add and edit parametric door
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcDoor"
    And I click "Assign IFC Class"
    And I look at the "Door" panel
    And I click "ADD"
    And I look at the "Door" panel
    And I click "GREASEPENCIL"
    And I look at the "Door" panel
    And I click "CHECKMARK"
