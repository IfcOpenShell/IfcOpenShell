@type
Feature: Type

Scenario: Assign type - assign to an empty type
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    When the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"

Scenario: Assign type - assign to a type with representation maps
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    When the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has a "MappedRepresentation" representation of "Model/Body/MODEL_VIEW"

Scenario: Assign type - assign to a type with a material layer set
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialLayerSet"
    And I press "bim.assign_material"
    And I press "bim.enable_editing_assigned_material"
    And the variable "layer_set" is "{ifc}.by_type("IfcMaterialLayerSet")[0].id()"
    And I press "bim.add_layer(layer_set={layer_set})"
    And the variable "layer" is "{ifc}.by_type("IfcMaterialLayer")[0].id()"
    And I press "bim.enable_editing_material_set_item(material_set_item={layer})"
    And I set "active_object.BIMObjectMaterialProperties.material_set_item_attributes[0].float_value" to "0.1"
    And I press "bim.edit_material_set_item(material_set_item={layer})"
    And I press "bim.edit_assigned_material(material_set={layer_set})"
    When the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has a "SweptSolid" representation of "Model/Body/MODEL_VIEW"

Scenario: Assign type - assign to a type with a material profile set
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialProfileSet"
    And I press "bim.assign_material"
    And I press "bim.enable_editing_assigned_material"
    And I press "bim.add_profile_def"
    And the variable "profile_set" is "{ifc}.by_type("IfcMaterialProfileSet")[0].id()"
    And I press "bim.add_profile(profile_set={profile_set})"
    And I press "bim.edit_assigned_material(material_set={profile_set})"
    When the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has a "SweptSolid" representation of "Model/Body/MODEL_VIEW"

Scenario: Select type objects
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    When the object "IfcWallType/Empty" is selected
    And I press "bim.select_type_objects"
    Then the object "IfcWall/Cube" is selected
