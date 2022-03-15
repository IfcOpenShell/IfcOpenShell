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
    And I set "scene.BIMModelProperties.relating_type" to "{cube}"
    When I press "bim.add_type_instance"
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
    And I set "scene.BIMModelProperties.relating_type" to "{empty}"
    When I press "bim.add_type_instance"
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
    And I set "scene.BIMModelProperties.relating_type" to "{cube}"
    And I press "bim.add_type_instance"
    And the object "IfcWall/Wall" data is a "Tessellation" representation of "Model/Body/MODEL_VIEW"
    And the object "IfcWall/Wall" is selected
    And the variable "context" is "[c for c in {ifc}.by_type('IfcGeometricRepresentationSubContext') if c.TargetView == 'PLAN_VIEW'][0].id()"
    And I set "scene.BIMRootProperties.contexts" to "{context}"
    And I press "bim.add_representation"
    And the object "IfcWall/Wall" data is a "Annotation2D" representation of "Plan/Annotation/PLAN_VIEW"
    When I press "bim.add_type_instance"
    Then the object "IfcWall/Wall" data is a "Annotation2D" representation of "Plan/Annotation/PLAN_VIEW"
    And the object "IfcWall/Wall.001" data is a "Annotation2D" representation of "Plan/Annotation/PLAN_VIEW"

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
