@boundary
Feature: Boundary

Scenario: Add boundary from space
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
    And the cursor is at "0.5,0.5,0"
    And I deselect all objects
    And I press "bim.generate_space"
    And I look at the "Spatial Decomposition" panel
    And I set the "is_visible" property to "TRUE"
    When I select the object "IfcSpace/Space"
    And I press "bim.add_boundary"
    Then the object "IfcRelSpaceBoundary/None" exists
    And the object "IfcRelSpaceBoundary/None.001" exists
    And the object "IfcRelSpaceBoundary/None.002" exists
    And the object "IfcRelSpaceBoundary/None.003" exists

Scenario: Regenerate boundaries after moving a wall
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
    And the cursor is at "0.5,0.5,0"
    And I deselect all objects
    And I press "bim.generate_space"
    And I look at the "Spatial Decomposition" panel
    And I set the "is_visible" property to "TRUE"
    And I select the object "IfcSpace/Space"
    And I press "bim.add_boundary"
    And the object "IfcWall/Wall" is moved to "0,0,1"
    And I select the object "IfcSpace/Space"
    And I press "bim.add_boundary"
    And the variable "lowest_z" is "min((o.matrix_world @ v.co).z for o in [tool.Ifc.get_object(b) for b in {ifc}.by_type('IfcRelSpaceBoundary') if b.RelatedBuildingElement == tool.Ifc.get_entity(bpy.data.objects['IfcWall/Wall'])] for v in o.data.vertices)"
    Then the variable "lowest_z" equals "1.0"

Scenario: Regenerate boundaries keeps the boundary of an unrelated element
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
    And the cursor is at "0.5,0.5,0"
    And I deselect all objects
    And I press "bim.generate_space"
    And I look at the "Spatial Decomposition" panel
    And I set the "is_visible" property to "TRUE"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcMember"
    And I press "bim.assign_class"
    And the object "IfcSpace/Space" is selected
    And additionally the object "IfcMember/Cube" is selected
    And I press "bim.add_boundary"
    And the variable "before" is "[b.id() for b in {ifc}.by_type('IfcRelSpaceBoundary') if b.RelatedBuildingElement.is_a('IfcMember')]"
    And the object "IfcSpace/Space" is selected
    And I press "bim.add_boundary"
    And the variable "after" is "[b.id() for b in {ifc}.by_type('IfcRelSpaceBoundary') if b.RelatedBuildingElement.is_a('IfcMember')]"
    Then the variable "after" equals "{before}"
