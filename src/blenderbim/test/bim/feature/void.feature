@void
Feature: Void
    Covers voids and fillings.

Scenario: Add an opening
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube
    And the object "IfcWall/Cube" is selected
    And additionally the object "Cube" is selected
    And I press "bim.add_opening(opening='Cube', obj='IfcWall/Cube')"
    Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
    And the object "IfcOpeningElement/Cube" should display as "WIRE"
    And the object "IfcWall/Cube" has a boolean difference by "IfcOpeningElement/Cube"
    And the object "IfcWall/Cube" is voided by "Cube"

Scenario: Add an opening on an opening
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
    And I press "bim.assign_class"
    And the object "IfcOpeningElement/Cube" is selected
    And additionally the object "IfcOpeningElement/Cube.001" is selected
    And I press "bim.add_opening(opening='IfcOpeningElement/Cube', obj='IfcOpeningElement/Cube.001')"
    Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
    And the object "IfcOpeningElement/Cube" should display as "WIRE"
    And the object "IfcOpeningElement/Cube" is not a void
    Then the object "IfcOpeningElement/Cube.001" is an "IfcOpeningElement"
    And the object "IfcOpeningElement/Cube.001" should display as "WIRE"
    Then the object "IfcOpeningElement/Cube.001" has no boolean difference by "IfcOpeningElement/Cube"
    And the object "IfcOpeningElement/Cube.001" is not voided by "Cube"

Scenario: Add an opening on a null object
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
    And I press "bim.assign_class"
    And I deselect all objects
    And I press "bim.add_opening(opening='IfcOpeningElement/Cube')"
    Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
    And the object "IfcOpeningElement/Cube" should display as "WIRE"
    And the object "IfcOpeningElement/Cube" is not a void

Scenario: Add an opening on a non IFC object
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I press "bim.add_opening(opening='IfcOpeningElement/Cube', obj='Cube')"
    Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
    And the object "IfcOpeningElement/Cube" should display as "WIRE"
    And the object "IfcOpeningElement/Cube" is not a void
    And the object "Cube" is not an IFC element

Scenario: Add an opening with a null object
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I deselect all objects
    And I press "bim.add_opening(obj='IfcWall/Cube')"
    Then the object "IfcWall/Cube" is an "IfcWall"
    And the object "IfcWall/Cube" is not voided

Scenario: Add an opening to Element B with a void that already voids Element A
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube
    And I press "bim.add_opening(opening='Cube', obj='IfcWall/Cube')"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_opening(opening='IfcOpeningElement/Cube', obj='IfcWall/Cube.001')"
    Then the object "IfcWall/Cube" is not voided
    And the object "IfcWall/Cube" has no boolean difference by "IfcOpeningElement/Cube"
    And the object "IfcWall/Cube.001" is voided by "Cube"
    And the object "IfcWall/Cube.001" has a boolean difference by "IfcOpeningElement/Cube"

Scenario: Remove an opening
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube of size "1" at "1,0,0"
    And the object "Cube" is selected
    And additionally the object "IfcWall/Cube" is selected
    And I press "bim.add_opening(opening='Cube', obj='IfcWall/Cube')"
    And the variable "opening_id" is "IfcStore.get_file().by_type('IfcOpeningElement')[0].id()"
    And I press "bim.remove_opening(opening_id={opening_id}, obj='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has no boolean difference by "IfcOpeningElement/Cube"
    And the object "IfcWall/Cube" is not voided by "Cube"
    And the object "Cube" is not an IFC element

Scenario: Remove a non dynamic opening manually
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube of size "1" at "1,0,0"
    And the object "IfcWall/Cube" is selected
    And additionally the object "Cube" is selected
    And I press "bim.add_opening(opening='Cube', obj='IfcWall/Cube')"
    And the object "IfcWall/Cube" is selected
    And the variable "representation" is "IfcStore.get_file().by_type('IfcWall')[0].Representation.Representations[1].id()"
    And I press "bim.switch_representation(ifc_definition_id={representation}, should_reload=True)"
    Then the object "IfcWall/Cube" has no boolean difference by "IfcOpeningElement/Cube"
    And the object "IfcWall/Cube" has "16" vertices
    And the variable "opening_id" is "IfcStore.get_file().by_type('IfcOpeningElement')[0].id()"
    When I press "bim.remove_opening(opening_id={opening_id}, obj='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has "8" vertices
    And the object "Cube" is not an IFC element

Scenario: Remove an opening using deletion
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube of size "1" at "1,0,0"
    And the object "IfcWall/Cube" is selected
    And additionally the object "Cube" is selected
    And I press "bim.add_opening(opening='Cube', obj='IfcWall/Cube')"
    And the object "IfcOpeningElement/Cube" is selected
    And I delete the selected objects
    Then the object "IfcWall/Cube" has no boolean difference by "IfcOpeningElement/Cube"
    And the object "IfcWall/Cube" is not voided by "Cube"

Scenario: Remove and opening indirectly by deleting its building Element
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube of size "1" at "1,0,0"
    And the object "IfcWall/Cube" is selected
    And additionally the object "Cube" is selected
    And I press "bim.add_opening(opening='Cube', obj='IfcWall/Cube')"
    And the object "IfcWall/Cube" is selected
    And I delete the selected objects
    Then the object "Cube" is not an IFC element

Scenario: Add a filling
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
    And I press "bim.assign_class"
    And the object "IfcOpeningElement/Cube" is selected
    And I press "bim.add_filling(opening='IfcOpeningElement/Cube', obj='IfcDoor/Cube')"
    Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
    And the object "IfcOpeningElement/Cube" should display as "WIRE"
    And the object "IfcDoor/Cube" is an "IfcDoor"
    And the void "IfcOpeningElement/Cube" is filled by "Cube"

Scenario: Add a filling on a null object
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
    And I press "bim.assign_class"
    And the object "IfcDoor/Cube" is selected
    And I press "bim.add_filling(obj='IfcDoor/Cube')"
    Then the object "IfcDoor/Cube" is an "IfcDoor"
    And the object "IfcDoor/Cube" is not a filling

Scenario: Add a filling on itself
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
    And I press "bim.assign_class"
    And the object "IfcOpeningElement/Cube" is selected
    And I press "bim.add_filling(opening='IfcOpeningElement/Cube', obj='IfcOpeningElement/Cube')"
    Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
    And the void "IfcOpeningElement/Cube" is not filled by "Cube"
    And the object "IfcOpeningElement/Cube" is not a filling

Scenario: Add a filling with a non IFC object
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
    And I press "bim.assign_class"
    And I add a cube
    And the object "IfcOpeningElement/Cube" is selected
    And I press "bim.add_filling(opening='IfcOpeningElement/Cube', obj='Cube')"
    Then the object "Cube" is not an IFC element
    And the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
    And the void "IfcOpeningElement/Cube" is not filled by "Cube"

Scenario: Add a filling on a non IFC object
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I press "bim.add_filling(opening='Cube', obj='IfcDoor/Cube')"
    Then the object "Cube" is not an IFC element
    And the object "IfcDoor/Cube" is an "IfcDoor"

Scenario: Add a filling on Opening B with a filling that already fills Opening A
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
    And I press "bim.assign_class"
    And I press "bim.add_filling(opening='IfcOpeningElement/Cube', obj='IfcDoor/Cube')"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
    And I press "bim.assign_class"
    And I press "bim.add_filling(opening='IfcOpeningElement/Cube.001', obj='IfcDoor/Cube')"
    Then the void "IfcOpeningElement/Cube" is not filled by "Cube"
    And the void "IfcOpeningElement/Cube.001" is filled by "Cube"

Scenario: Remove a filling
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
    And I press "bim.assign_class"
    And I press "bim.add_filling(opening='IfcOpeningElement/Cube', obj='IfcDoor/Cube')"
    And I press "bim.remove_filling(obj='IfcDoor/Cube')"
    Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
    And the object "IfcDoor/Cube" is an "IfcDoor"
    And the void "IfcOpeningElement/Cube" is not filled by "Cube"

Scenario: Remove a filling which is not an IFC object
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I press "bim.remove_filling(obj='Cube')"
    Then the object "Cube" is not an IFC element

Scenario: Remove a filling which is not a filling
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
    And I press "bim.assign_class"
    And the object "IfcDoor/Cube" is not a filling
    And I press "bim.remove_filling(obj='IfcDoor/Cube')"
    Then the object "IfcDoor/Cube" is an "IfcDoor"
    And the object "IfcDoor/Cube" is not a filling

Scenario: Remove a filling which is null
    Given an empty IFC project
    When I press "bim.remove_filling()"
    Then nothing happens

Scenario: Remove a filling using deletion on the filling
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
    And I press "bim.assign_class"
    And I press "bim.add_filling(opening='IfcOpeningElement/Cube', obj='IfcDoor/Cube')"
    And the object "IfcDoor/Cube" is selected
    And I delete the selected objects
    Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
    And the void "IfcOpeningElement/Cube" is not filled by "Cube"

Scenario: Remove a filling using deletion on the opening
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
    And I press "bim.assign_class"
    And I press "bim.add_filling(opening='IfcOpeningElement/Cube', obj='IfcDoor/Cube')"
    And the object "IfcOpeningElement/Cube" is selected
    And I delete the selected objects
    Then the object "IfcDoor/Cube" is an "IfcDoor"
    And the object "IfcDoor/Cube" is not a filling
