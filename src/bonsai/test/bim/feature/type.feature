@type
Feature: Type

Scenario: Add type - adding via manual class assignment
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    When I press "bim.assign_class"
    Then nothing happens

Scenario: Add type - add from empty template
    Given an empty IFC project
    And I press "bim.launch_type_manager"
    And I set "scene.BIMModelProperties.type_class" to "IfcWallType"
    And I set "scene.BIMModelProperties.type_predefined_type" to "SOLIDWALL"
    And I set "scene.BIMModelProperties.type_template" to "EMPTY"
    When I press "bim.add_type"
    Then the object "IfcWallType/TYPEX" is an "IfcWallType"
    And the object "IfcWallType/TYPEX" has no data

Scenario: Enable editing type
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When I press "bim.enable_editing_type"
    Then nothing happens

Scenario: Disable editing type
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.enable_editing_type"
    When I press "bim.disable_editing_type"
    Then nothing happens

Scenario: Assign type - assign to an empty type
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
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
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
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

Scenario: Assign type - assign to a type with a material layer set, which automatically recreates the shape
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.add_material()"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialLayerSet"
    And I press "bim.assign_material"
    When the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has a "SweptSolid" representation of "Model/Body/MODEL_VIEW"
    And the object "IfcWall/Cube" has a "100" thick layered material containing the material "Default"
    And the object "IfcWall/Cube" dimensions are "2,.1,3"

Scenario: Assign type - assign to a different type with a material layer set
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And the variable "type" is "{ifc}.by_type('IfcWallType')[-1].id()"
    And I press "bim.add_material()"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialLayerSet"
    And I press "bim.assign_material"
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialLayerSet"
    And I press "bim.assign_material"
    And the variable "type2" is "[w for w in {ifc}.by_type('IfcWallType') if w.id() != {type}][0].id()"
    And the variable "layer_set" is "ifcopenshell.util.element.get_material({ifc}.by_id({type2})).id()"
    And the variable "layer" is "{ifc}.by_id({layer_set}).MaterialLayers[0].id()"
    And I press "bim.enable_editing_material_set_item(material_set_item={layer})"
    And I set "active_object.BIMObjectMaterialProperties.material_set_item_attributes[0].float_value" to "200"
    And I press "bim.edit_material_set_item(material_set_item={layer})"
    And I press "bim.edit_assigned_material(material_set={layer_set})"
    When I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has a "SweptSolid" representation of "Model/Body/MODEL_VIEW"
    And the object "IfcWall/Cube" has a "100" thick layered material containing the material "Default"
    And the object "IfcWall/Cube" dimensions are "2,.1,3"
    When I press "bim.assign_type(relating_type={type2}, related_object='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has a "200" thick layered material containing the material "Default"
    And the object "IfcWall/Cube" dimensions are "2,.2,3"

Scenario: Assign type - assign to a type with a material profile set
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.add_material()"
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
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
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

Scenario: Select similar type
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube.001')"
    When the object "IfcWall/Cube" is selected
    And I press "bim.select_similar_type"
    Then the object "IfcWall/Cube" is selected
    And the object "IfcWall/Cube.001" is selected

Scenario: Purge unused types
    Given an empty IFC project
    And I press "bim.launch_type_manager"
    And I set "scene.BIMModelProperties.type_class" to "IfcWallType"
    And I set "scene.BIMModelProperties.type_predefined_type" to "SOLIDWALL"
    And I set "scene.BIMModelProperties.type_template" to "EMPTY"
    When I press "bim.add_type"
    Then the object "IfcWallType/TYPEX" is an "IfcWallType"
    And the object "IfcWallType/TYPEX" has no data
    When I press "bim.purge_unused_types"
    Then the object "IfcWallType/TYPEX" does not exist
