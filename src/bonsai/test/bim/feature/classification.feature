@classification
Feature: Classification

Scenario: Load classification library
    Given an empty IFC project
    When I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    Then nothing happens

Scenario: Add classification
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    When I press "bim.add_classification"
    Then nothing happens

Scenario: Add classification - IFC2X3
    Given an empty IFC2X3 project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    When I press "bim.add_classification"
    Then nothing happens

Scenario: Enable editing classification
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And the variable "classification" is "{ifc}.by_type('IfcClassification')[0].id()"
    When I press "bim.enable_editing_classification(classification={classification})"
    Then nothing happens

Scenario: Disable editing classification
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And the variable "classification" is "{ifc}.by_type('IfcClassification')[0].id()"
    And I press "bim.enable_editing_classification(classification={classification})"
    When I press "bim.disable_editing_classification"
    Then nothing happens

Scenario: Remove classification
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And the variable "classification" is "{ifc}.by_type('IfcClassification')[0].id()"
    When I press "bim.remove_classification(classification={classification})"
    Then nothing happens

Scenario: Edit classification
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And the variable "classification" is "{ifc}.by_type('IfcClassification')[0].id()"
    And I press "bim.enable_editing_classification(classification={classification})"
    When I press "bim.edit_classification"
    Then nothing happens

Scenario: Add classification reference - object
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.change_classification_level(parent_id={classification})"
    And the variable "reference" is "{classification_ifc}.by_type('IfcClassificationReference')[0].id()"
    When I press "bim.add_classification_reference(reference={reference}, obj='IfcWallType/Cube', obj_type='Object')"
    Then nothing happens

Scenario: Change classification level
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.change_classification_level(parent_id={classification})"
    And the variable "reference" is "{classification_ifc}.by_type('IfcClassificationReference')[0].id()"
    When I press "bim.change_classification_level(parent_id={reference})"
    Then nothing happens

Scenario: Disable editing classification references
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.change_classification_level(parent_id={classification})"
    When I press "bim.disable_editing_classification_references"
    Then nothing happens

Scenario: Enable editing classification reference
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.change_classification_level(parent_id={classification})"
    And the variable "reference" is "{classification_ifc}.by_type('IfcClassificationReference')[0].id()"
    And I press "bim.add_classification_reference(reference={reference}, obj='IfcWallType/Cube', obj_type='Object')"
    And the variable "reference" is "{ifc}.by_type('IfcClassificationReference')[0].id()"
    When I press "bim.enable_editing_classification_reference(reference={reference})"
    Then nothing happens

Scenario: Disable editing classification reference
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.change_classification_level(parent_id={classification})"
    And the variable "reference" is "{classification_ifc}.by_type('IfcClassificationReference')[0].id()"
    And I press "bim.add_classification_reference(reference={reference}, obj='IfcWallType/Cube', obj_type='Object')"
    And the variable "reference" is "{ifc}.by_type('IfcClassificationReference')[0].id()"
    And I press "bim.enable_editing_classification_reference(reference={reference})"
    When I press "bim.disable_editing_classification_reference"
    Then nothing happens

Scenario: Remove classification reference - object
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.change_classification_level(parent_id={classification})"
    And the variable "reference" is "{classification_ifc}.by_type('IfcClassificationReference')[0].id()"
    And I press "bim.add_classification_reference(reference={reference}, obj='IfcWallType/Cube', obj_type='Object')"
    And the variable "reference" is "{ifc}.by_type('IfcClassificationReference')[0].id()"
    And I press "bim.enable_editing_classification_reference(reference={reference})"
    When I press "bim.remove_classification_reference(reference={reference}, obj='IfcWallType/Cube', obj_type='Object')"
    Then nothing happens

Scenario: Edit classification reference
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.change_classification_level(parent_id={classification})"
    And the variable "reference" is "{classification_ifc}.by_type('IfcClassificationReference')[0].id()"
    And I press "bim.add_classification_reference(reference={reference}, obj='IfcWallType/Cube', obj_type='Object')"
    And the variable "reference" is "{ifc}.by_type('IfcClassificationReference')[0].id()"
    And I press "bim.enable_editing_classification_reference(reference={reference})"
    When I press "bim.edit_classification_reference"
    Then nothing happens

Scenario: Add classification reference - material
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And I press "bim.add_material(name='Material')"
    And I press "bim.load_materials"
    And I press "bim.expand_material_category(category='Uncategorised')"
    And I set "scene.BIMMaterialProperties.active_material_index" to "1"
    And the variable "material" is "{ifc}.by_type('IfcMaterial')[0].id()"
    And I press "bim.change_classification_level(parent_id={classification})"
    And the variable "reference" is "{classification_ifc}.by_type('IfcClassificationReference')[0].id()"
    When I press "bim.add_classification_reference(reference={reference}, obj_type='Material')"
    Then nothing happens

Scenario: Remove classification reference - material
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And I press "bim.add_material(name='Material')"
    And I press "bim.load_materials"
    And I press "bim.expand_material_category(category='Uncategorised')"
    And I set "scene.BIMMaterialProperties.active_material_index" to "1"
    And I press "bim.change_classification_level(parent_id={classification})"
    And the variable "reference" is "{classification_ifc}.by_type('IfcClassificationReference')[0].id()"
    And I press "bim.add_classification_reference(reference={reference}, obj_type='Material')"
    When I press "bim.remove_classification_reference(reference={reference}, obj_type='Material')"
    Then nothing happens

Scenario: Add classification reference - cost
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And I press "bim.change_classification_level(parent_id={classification})"
    And the variable "reference" is "{classification_ifc}.by_type('IfcClassificationReference')[0].id()"
    When I press "bim.add_classification_reference(reference={reference}, obj='', obj_type='Cost')"
    Then nothing happens

Scenario: Remove classification reference - cost
    Given an empty IFC project
    And I press "bim.load_classification_library(filepath='{cwd}/test/files/classification.ifc')"
    And the variable "classification" is "{classification_ifc}.by_type('IfcClassification')[0].id()"
    And I set "scene.BIMClassificationProperties.available_classifications" to "{classification}"
    And I press "bim.add_classification"
    And I press "bim.add_cost_schedule"
    And the variable "cost_schedule" is "{ifc}.by_type('IfcCostSchedule')[0].id()"
    And I press "bim.enable_editing_cost_items(cost_schedule={cost_schedule})"
    And I press "bim.add_summary_cost_item()"
    And I press "bim.change_classification_level(parent_id={classification})"
    And the variable "reference" is "{classification_ifc}.by_type('IfcClassificationReference')[0].id()"
    And I press "bim.add_classification_reference(reference={reference}, obj='', obj_type='Cost')"
    When I press "bim.remove_classification_reference(reference={reference}, obj='', obj_type='Cost')"
    Then nothing happens
