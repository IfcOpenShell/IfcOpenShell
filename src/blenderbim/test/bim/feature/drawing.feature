@drawing
Feature: Drawing

Scenario: Create drawing
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the variable "wall1" is "IfcStore.get_file().by_type('IfcWall')[-1].id()"
    And I press "bim.add_drawing"
    And the variable "drawing" is "IfcStore.get_file().by_type('IfcAnnotation')[0].id()"
    And I set "scene.DocProperties.active_drawing_index" to "0"
    And I press "bim.activate_view(drawing={drawing})"
    And I press "bim.create_drawing"
    Then nothing happens

Scenario: Create drawing after deleting a duplicated object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
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
    And I press "bim.activate_view(drawing={drawing})"
    And I press "bim.create_drawing"
    And the object "IfcWall/Cube" is selected
    And I press "object.delete(use_global=False)"
    And I press "bim.create_drawing"
    Then nothing happens