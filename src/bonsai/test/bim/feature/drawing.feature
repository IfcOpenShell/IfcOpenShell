@drawing
Feature: Drawing

Scenario: Duplicate drawing
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the variable "wall1" is "IfcStore.get_file().by_type('IfcWall')[-1].id()"
    And I press "bim.add_drawing"
    And the variable "drawing" is "IfcStore.get_file().by_type('IfcAnnotation')[0].id()"
    When I press "bim.duplicate_drawing(drawing={drawing})"
    Then nothing happens

Scenario: Create drawing
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the variable "wall1" is "IfcStore.get_file().by_type('IfcWall')[-1].id()"
    And I press "bim.add_drawing"
    And the variable "drawing" is "IfcStore.get_file().by_type('IfcAnnotation')[0].id()"
    And I set "scene.DocProperties.active_drawing_index" to "0"
    And I press "bim.activate_drawing(drawing={drawing})"
    When I press "bim.create_drawing"
    Then nothing happens

Scenario: Create drawing after deleting a duplicated object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the variable "wall1" is "IfcStore.get_file().by_type('IfcWall')[-1].id()"
    And I press "bim.copy_class(obj='IfcWall/Cube')"
    And the variable "wall2" is "IfcStore.get_file().by_type('IfcWall')[-1].id()"
    And I press "bim.load_drawings"
    # And I set "scene.DocProperties.location_hint" to "('My Storey', 'My Storey', '')"
    And I press "bim.add_drawing"
    And the variable "drawing" is "IfcStore.get_file().by_type('IfcAnnotation')[0].id()"
    And I set "scene.DocProperties.active_drawing_index" to "0"
    And I press "bim.activate_drawing(drawing={drawing})"
    And I press "bim.create_drawing"
    And the object "IfcWall/Cube" is selected
    And I press "object.delete(use_global=False)"
    When I press "bim.create_drawing"
    Then nothing happens

Scenario: Activate drawing preserves visibility for non-ifc objects
    Given an empty IFC project
    And I add a cube
    And I add a cube
    And the object "Cube" is visible
    And the object "Cube.001" is not visible
    And I press "bim.add_drawing"
    And the variable "drawing" is "IfcStore.get_file().by_type('IfcAnnotation')[0].id()"
    And I set "scene.DocProperties.active_drawing_index" to "0"
    When I press "bim.activate_drawing(drawing={drawing})"
    Then the object "Cube" is visible
    And the object "Cube.001" is not visible

Scenario: Activate drawing preserves selection
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I press "bim.add_drawing"
    And the variable "drawing" is "IfcStore.get_file().by_type('IfcAnnotation')[0].id()"
    And I set "scene.DocProperties.active_drawing_index" to "0"
    When I press "bim.activate_drawing(drawing={drawing})"
    Then the object "Cube" is selected

Scenario: Remove drawing
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the variable "wall1" is "IfcStore.get_file().by_type('IfcWall')[-1].id()"
    And I press "bim.add_drawing"
    And the variable "drawing" is "IfcStore.get_file().by_type('IfcAnnotation')[0].id()"
    And the collection "IfcAnnotation/PLAN_VIEW" exists
    When I press "bim.remove_drawing(drawing={drawing})"
    Then the collection "IfcAnnotation/PLAN_VIEW" does not exist

Scenario: Remove drawing - via object deletion
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the variable "wall1" is "IfcStore.get_file().by_type('IfcWall')[-1].id()"
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
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the variable "wall1" is "IfcStore.get_file().by_type('IfcWall')[-1].id()"
    And I press "bim.add_drawing"
    And the variable "drawing" is "IfcStore.get_file().by_type('IfcAnnotation')[0].id()"
    And the collection "IfcAnnotation/PLAN_VIEW" exists
    And I set "scene.DocProperties.active_drawing_index" to "0"
    And I press "bim.activate_drawing(drawing={drawing})"
    When the object "IfcAnnotation/PLAN_VIEW" is selected
    And I press "bim.override_object_delete"
    Then the collection "IfcAnnotation/PLAN_VIEW" does not exist
