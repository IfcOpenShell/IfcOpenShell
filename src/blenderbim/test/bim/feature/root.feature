@root
Feature: Root

Scenario: Reassign class
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "object.duplicate_move"
    When the object "IfcWall/Cube.001" is selected
    And I press "bim.enable_reassign_class"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcSlab"
    And I press "bim.reassign_class"
    Then the object "IfcSlab/Cube" is an "IfcSlab"

Scenario: Unlink object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add a material
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_material"
    When I press "bim.unlink_object(obj='IfcWall/Cube')"
    Then the object "Cube" is not an IFC element
    And the material "Material" is not an IFC material
    And the material "Material" is not an IFC style

Scenario: Copy class
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When I press "bim.copy_class(obj='IfcWall/Cube')"
    Then the object "IfcWall/Cube" is an "IfcWall"

Scenario: Assign a class to a cube
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    Then the object "IfcWall/Cube" is an "IfcWall"
    And the object "IfcWall/Cube" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcWall/Cube" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"

Scenario: Assign a type class to a cube
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    Then the object "IfcWallType/Cube" is an "IfcWallType"
    And the object "IfcWallType/Cube" is in the collection "Types"
    And the object "IfcWallType/Cube" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"

Scenario: Assign a spatial class to a cube
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcSpatialElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcBuilding"
    And I press "bim.assign_class"
    Then the object "IfcBuilding/Cube" is an "IfcBuilding"
    And the object "IfcBuilding/Cube" is in the collection "IfcBuilding/Cube"
    And the object "IfcBuilding/Cube" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"

Scenario: Assign a spatial class to a cube already in a collection
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is placed in the collection "IfcBuildingStorey/My Storey"
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcSpatialElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcSpace"
    And I press "bim.assign_class"
    Then the object "IfcSpace/Cube" is an "IfcSpace"
    And the object "IfcSpace/Cube" is in the collection "IfcSpace/Cube"
    And the collection "IfcSpace/Cube" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcSpace/Cube" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"

Scenario: Assign an opening class to a cube
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
    And I press "bim.assign_class"
    Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
    And the object "IfcOpeningElement/Cube" should display as "WIRE"
    And the object "IfcOpeningElement/Cube" is in the collection "IfcOpeningElements"
    And the object "IfcOpeningElement/Cube" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"

Scenario: Assign a class to a cube in a collection
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And the object "Cube" is placed in the collection "IfcBuildingStorey/My Storey"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    Then the object "IfcWall/Cube" is contained in "My Storey"

Scenario: Copy a wall
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I duplicate the selected objects
    Then the object "IfcWall/Cube" and "IfcWall/Cube.001" are different elements

Scenario: Copy a storey
    Given an empty IFC project
    And the object "IfcBuildingStorey/My Storey" is selected
    When I duplicate the selected objects
    Then the object "IfcBuildingStorey/My Storey" and "IfcBuildingStorey/My Storey.001" are different elements
    And the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcBuildingStorey/My Storey.001" is in the collection "IfcBuildingStorey/My Storey.001"
    And the collection "IfcBuildingStorey/My Storey.001" is in the collection "IfcBuilding/My Building"
