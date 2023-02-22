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
    When I press "bim.add_constr_type_instance"
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
    When I press "bim.add_constr_type_instance"
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
    And I press "bim.add_constr_type_instance"
    And the object "IfcWall/Wall" data is a "Tessellation" representation of "Model/Body/MODEL_VIEW"
    And the object "IfcWall/Wall" is selected
    And the variable "context" is "[c for c in {ifc}.by_type('IfcGeometricRepresentationSubContext') if c.ContextType == 'Plan' and c.ContextIdentifier == 'Body' and c.TargetView == 'PLAN_VIEW'][0].id()"
    And I set "scene.BIMRootProperties.contexts" to "{context}"
    And I press "bim.add_representation"
    And the object "IfcWall/Wall" data is a "Annotation2D" representation of "Plan/Body/PLAN_VIEW"
    When I press "bim.add_constr_type_instance"
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
    When I press "mesh.add_grid"
    Then the object "IfcGrid/Grid" is an "IfcGrid"
    And the object "IfcGridAxis/A" is an "IfcGridAxis"
    And the object "IfcGridAxis/B" is an "IfcGridAxis"
    And the object "IfcGridAxis/C" is an "IfcGridAxis"
    And the object "IfcGridAxis/01" is an "IfcGridAxis"
    And the object "IfcGridAxis/02" is an "IfcGridAxis"
    And the object "IfcGridAxis/03" is an "IfcGridAxis"

Scenario: Pie update container
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc')"
    Then the object "IfcSlab/Slab" is in the collection "IfcBuildingStorey/Ground Floor"
    When the object "IfcSlab/Slab" is placed in the collection "IfcBuildingStorey/Level 1"
    And I press "bim.pie_update_container"
    Then nothing happens

Scenario: Add a wall
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    When I press "bim.add_constr_type_instance"
    Then the object "IfcWall/Wall" is an "IfcWall"
    And the object "IfcWall/Wall" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0,0,0"

Scenario: Extend a wall to the cursor
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.hotkey(hotkey='S_A')"
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
    And I press "bim.hotkey(hotkey='S_A')"
    And the cursor is at "0.5,0,0"
    When I press "bim.hotkey(hotkey='S_A')"
    Then the object "IfcWall/Wall.001" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall.001" bottom left corner is at "0,0,0"
    And the object "IfcWall/Wall" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0.5,0,0"
    And the object "IfcWall/Wall" top right corner is at "0.6,-1,3"

Scenario: Extend one wall to another
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.hotkey(hotkey='S_A')"
    And the cursor is at "0.5,0,0"
    And I press "bim.hotkey(hotkey='S_A')"
    And the object "IfcWall/Wall" is moved to "0.5,-1,0"
    And the object "IfcWall/Wall" is selected
    And additionally the object "IfcWall/Wall.001" is selected
    When I press "bim.hotkey(hotkey='S_E')"
    Then the object "IfcWall/Wall.001" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall.001" bottom left corner is at "0,0,0"
    And the object "IfcWall/Wall" dimensions are "2,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0.5,0,0"
    And the object "IfcWall/Wall" top right corner is at "0.6,-2,3"

Scenario: Join two walls with a butt joint - first wall has priority
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.hotkey(hotkey='S_A')"
    And the cursor is at "0.5,0,0"
    And I press "bim.hotkey(hotkey='S_A')"
    And the object "IfcWall/Wall" is selected
    And additionally the object "IfcWall/Wall.001" is selected
    When I press "bim.hotkey(hotkey='S_T')"
    Then the object "IfcWall/Wall.001" dimensions are "0.4,0.1,3"
    And the object "IfcWall/Wall.001" bottom left corner is at "0.6,0,0"
    And the object "IfcWall/Wall" dimensions are "1.1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0.5,0.1,0"
    And the object "IfcWall/Wall" top right corner is at "0.6,-1,3"

Scenario: Join two walls with a butt joint - second wall has priority
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.hotkey(hotkey='S_A')"
    And the cursor is at "0.5,0,0"
    And I press "bim.hotkey(hotkey='S_A')"
    And the object "IfcWall/Wall.001" is selected
    And additionally the object "IfcWall/Wall" is selected
    When I press "bim.hotkey(hotkey='S_T')"
    Then the object "IfcWall/Wall.001" dimensions are "0.5,0.1,3"
    And the object "IfcWall/Wall.001" bottom left corner is at "0.5,0,0"
    And the object "IfcWall/Wall" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0.5,0,0"
    And the object "IfcWall/Wall" top right corner is at "0.6,-1,3"

Scenario: Join two walls with a mitre joint
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.hotkey(hotkey='S_A')"
    And the cursor is at "0.5,0,0"
    And I press "bim.hotkey(hotkey='S_A')"
    And the object "IfcWall/Wall" is selected
    And additionally the object "IfcWall/Wall.001" is selected
    When I press "bim.hotkey(hotkey='S_Y')"
    Then the object "IfcWall/Wall.001" dimensions are "0.5,0.1,3"
    And the object "IfcWall/Wall.001" bottom left corner is at "0.5,0,0"
    And the object "IfcWall/Wall" dimensions are "1.1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0.5,0.1,0"
    And the object "IfcWall/Wall" top right corner is at "0.6,-1,3"

Scenario: Change the height of a wall
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.hotkey(hotkey='S_A')"
    And the object "IfcWall/Wall" is selected
    And I set "scene.BIMModelProperties.extrusion_depth" to "2000.0"
    When I press "bim.change_extrusion_depth(depth=2000.0)"
    Then the object "IfcWall/Wall" dimensions are "1,0.1,2"

Scenario: Change the length of a wall
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.hotkey(hotkey='S_A')"
    And the object "IfcWall/Wall" is selected
    And I set "scene.BIMModelProperties.length" to "2000.0"
    When I press "bim.change_layer_length(length=2000.0)"
    Then the object "IfcWall/Wall" dimensions are "2,0.1,3"

Scenario: Flip a wall
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.hotkey(hotkey='S_A')"
    And the object "IfcWall/Wall" is selected
    When I press "bim.hotkey(hotkey='S_F')"
    Then the object "IfcWall/Wall" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "1,0,0"
    And the object "IfcWall/Wall" top right corner is at "0,-0.1,3"

Scenario: Split a wall
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.hotkey(hotkey='S_A')"
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
    And I press "bim.hotkey(hotkey='S_A')"
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
    And I press "bim.hotkey(hotkey='S_A')"
    And the object "IfcWall/Wall" is selected
    When I press "bim.hotkey(hotkey='S_G')"
    Then the object "IfcWall/Wall" is an "IfcWall"
    And the object "IfcWall/Wall" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0,0,0"
