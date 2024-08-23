@library
Feature: Library

Scenario: Add library
    Given an empty IFC project
    When I press "bim.add_library"
    Then nothing happens

Scenario: Remove library
    Given an empty IFC project
    And I press "bim.add_library"
    And the variable "library" is "{ifc}.by_type('IfcLibraryInformation')[-1].id()"
    When I press "bim.remove_library(library={library})"
    Then nothing happens

Scenario: Enable editing library references
    Given an empty IFC project
    And I press "bim.add_library"
    And the variable "library" is "{ifc}.by_type('IfcLibraryInformation')[-1].id()"
    When I press "bim.enable_editing_library_references(library={library})"
    Then nothing happens

Scenario: Disable editing library references
    Given an empty IFC project
    And I press "bim.add_library"
    And the variable "library" is "{ifc}.by_type('IfcLibraryInformation')[-1].id()"
    And I press "bim.enable_editing_library_references(library={library})"
    When I press "bim.disable_editing_library_references"
    Then nothing happens

Scenario: Enable editing library
    Given an empty IFC project
    And I press "bim.add_library"
    And the variable "library" is "{ifc}.by_type('IfcLibraryInformation')[-1].id()"
    And I press "bim.enable_editing_library_references(library={library})"
    When I press "bim.enable_editing_library"
    Then nothing happens

Scenario: Disable editing library
    Given an empty IFC project
    And I press "bim.add_library"
    And the variable "library" is "{ifc}.by_type('IfcLibraryInformation')[-1].id()"
    And I press "bim.enable_editing_library_references(library={library})"
    And I press "bim.enable_editing_library"
    When I press "bim.disable_editing_library"
    Then nothing happens

Scenario: Edit library
    Given an empty IFC project
    And I press "bim.add_library"
    And the variable "library" is "{ifc}.by_type('IfcLibraryInformation')[-1].id()"
    And I press "bim.enable_editing_library_references(library={library})"
    And I press "bim.enable_editing_library"
    When I press "bim.edit_library"
    Then nothing happens

Scenario: Add library reference
    Given an empty IFC project
    And I press "bim.add_library"
    And the variable "library" is "{ifc}.by_type('IfcLibraryInformation')[-1].id()"
    And I press "bim.enable_editing_library_references(library={library})"
    When I press "bim.add_library_reference"
    Then nothing happens

Scenario: Remove library reference
    Given an empty IFC project
    And I press "bim.add_library"
    And the variable "library" is "{ifc}.by_type('IfcLibraryInformation')[-1].id()"
    And I press "bim.enable_editing_library_references(library={library})"
    And I press "bim.add_library_reference"
    And the variable "reference" is "{ifc}.by_type('IfcLibraryReference')[-1].id()"
    When I press "bim.remove_library_reference(reference={reference})"
    Then nothing happens

Scenario: Enable editing library reference
    Given an empty IFC project
    And I press "bim.add_library"
    And the variable "library" is "{ifc}.by_type('IfcLibraryInformation')[-1].id()"
    And I press "bim.enable_editing_library_references(library={library})"
    And I press "bim.add_library_reference"
    And the variable "reference" is "{ifc}.by_type('IfcLibraryReference')[-1].id()"
    When I press "bim.enable_editing_library_reference(reference={reference})"
    Then nothing happens

Scenario: Disable editing library reference
    Given an empty IFC project
    And I press "bim.add_library"
    And the variable "library" is "{ifc}.by_type('IfcLibraryInformation')[-1].id()"
    And I press "bim.enable_editing_library_references(library={library})"
    And I press "bim.add_library_reference"
    And the variable "reference" is "{ifc}.by_type('IfcLibraryReference')[-1].id()"
    And I press "bim.enable_editing_library_reference(reference={reference})"
    When I press "bim.disable_editing_library_reference()"
    Then nothing happens

Scenario: Edit library reference
    Given an empty IFC project
    And I press "bim.add_library"
    And the variable "library" is "{ifc}.by_type('IfcLibraryInformation')[-1].id()"
    And I press "bim.enable_editing_library_references(library={library})"
    And I press "bim.add_library_reference"
    And the variable "reference" is "{ifc}.by_type('IfcLibraryReference')[-1].id()"
    And I press "bim.enable_editing_library_reference(reference={reference})"
    When I press "bim.edit_library_reference()"
    Then nothing happens

Scenario: Assign library reference
    Given an empty IFC project
    And I press "bim.add_library"
    And the variable "library" is "{ifc}.by_type('IfcLibraryInformation')[-1].id()"
    And I press "bim.enable_editing_library_references(library={library})"
    And I press "bim.add_library_reference"
    And the variable "reference" is "{ifc}.by_type('IfcLibraryReference')[-1].id()"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When I press "bim.assign_library_reference(reference={reference})"
    Then nothing happens

Scenario: Unassign library reference
    Given an empty IFC project
    And I press "bim.add_library"
    And the variable "library" is "{ifc}.by_type('IfcLibraryInformation')[-1].id()"
    And I press "bim.enable_editing_library_references(library={library})"
    And I press "bim.add_library_reference"
    And the variable "reference" is "{ifc}.by_type('IfcLibraryReference')[-1].id()"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_library_reference(reference={reference})"
    When I press "bim.unassign_library_reference(reference={reference})"
    Then nothing happens
