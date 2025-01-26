@root
Feature: Root

Scenario: Reassign class
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class(ifc_class='IfcWall', predefined_type='SOLIDWALL')"
    And I press "object.duplicate_move"
    When the object "IfcWall/Cube.001" is selected
    And I press "bim.enable_reassign_class"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcSlab"
    And I set "scene.BIMRootProperties.ifc_predefined_type" to "BASESLAB"
    And I press "bim.reassign_class"
    Then the object "IfcSlab/Cube" is an "IfcSlab"

Scenario: Unlink object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.load_styles(style_type='IfcSurfaceStyle')"
    And I press "bim.enable_adding_presentation_style"
    And I set "scene.BIMStylesProperties.style_name" to "Style"
    And I press "bim.add_presentation_style"
    And the object "IfcWall/Cube" is selected
    And the variable "style" is "{ifc}.by_type('IfcSurfaceStyle')[0].id()"
    And I press "bim.assign_style_to_selected(style_id={style})"
    When I press "bim.unlink_object(obj='IfcWall/Cube')"
    Then the object "Cube" is not an IFC element
    And the material "Style" is an IFC style
    And the material "Style.001" is not an IFC style

Scenario: Copy class
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When I press "bim.copy_class(obj='IfcWall/Cube')"
    Then the object "IfcWall/Cube" is an "IfcWall"

Scenario: Assign a class to a cube
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
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
    And the object "IfcWallType/Cube" is in the collection "IfcTypeProduct"
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
    And the object "IfcSpace/Cube" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"

Scenario: Assign a class to a cube in a collection
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And the object "Cube" is placed in the collection "IfcBuildingStorey/My Storey"
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    Then the object "IfcWall/Cube" is contained in "My Storey"

Scenario: Copy a wall
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I duplicate the selected objects
    Then the object "IfcWall/Cube" and "IfcWall/Cube.001" are different elements

Scenario: Copy a storey - when locked
    Given an empty IFC project
    And the object "IfcBuildingStorey/My Storey" is selected
    When I duplicate the selected objects
    Then the object "IfcBuildingStorey/My Storey.001" does not exist

Scenario: Copy a storey - when unlocked
    Given an empty IFC project
    And the object "IfcBuildingStorey/My Storey" is selected
    And I set "scene.BIMSpatialDecompositionProperties.is_locked" to "False"
    When I duplicate the selected objects
    Then the object "IfcBuildingStorey/My Storey" and "IfcBuildingStorey/My Storey.001" are different elements
    And the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcBuildingStorey/My Storey.001" is in the collection "IfcBuildingStorey/My Storey.001"
