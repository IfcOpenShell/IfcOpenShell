@geometry
Feature: Geometry

Scenario: Edit object placement
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When I press "bim.edit_object_placement"
    Then nothing happens

Scenario: Add representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When the variable "context" is "{ifc}.by_type('IfcGeometricRepresentationSubContext')[-1].id()"
    And I set "scene.BIMProperties.contexts" to "{context}"
    And I press "bim.add_representation"
    Then nothing happens

Scenario: Switch representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When the variable "representation" is "{ifc}.by_type('IfcShapeRepresentation')[0].id()"
    And I press "bim.switch_representation(obj='IfcWall/Cube', ifc_definition_id={representation})"
    Then nothing happens

Scenario: Copy representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcWall/Cube.001" is selected
    When I press "bim.copy_representation"
    Then nothing happens

Scenario: Override delete - without active IFC data
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "object.delete"
    Then the object "Cube" does not exist

Scenario: Override delete - with active IFC data
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When I press "object.delete"
    Then the object "IfcWall/Cube" does not exist

Scenario: Override duplicate move - without active IFC data
    Given an empty Blender session
    And I add a cube
    And I add an empty
    And the object "Cube" is selected
    And additionally the object "Empty" is selected
    When I press "object.duplicate_move"
    Then the object "Cube" exists
    And the object "Cube.001" exists

Scenario: Override duplicate move - with active IFC data
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcBuildingStorey/My Storey" is selected
    When I press "object.duplicate_move"
    Then the object "IfcWall/Cube" exists
    And the object "IfcWall/Cube" is an "IfcWall"
    And the object "IfcWall/Cube.001" exists
    And the object "IfcWall/Cube.001" is an "IfcWall"
    And the object "IfcWall/Cube.001" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"
    And the object "IfcBuildingStorey/My Storey.001" exists
    And the object "IfcBuildingStorey/My Storey.001" is an "IfcBuildingStorey"

Scenario: Override duplicate move - copying a type instance with a representation map
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I set "scene.BIMTypeProperties.ifc_class" to "IfcWallType"
    And the variable "cube" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I set "scene.BIMTypeProperties.relating_type" to "{cube}"
    And I press "bim.add_type_instance"
    And the object "IfcWall/Instance" is selected
    When I press "object.duplicate_move"
    Then the object "IfcWall/Instance.001" exists
    And the object "IfcWall/Instance.001" has a "MappedRepresentation" representation of "Model/Body/MODEL_VIEW"
