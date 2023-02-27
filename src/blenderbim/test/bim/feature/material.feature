@material
Feature: Material

Scenario: Load materials
    Given an empty IFC project
    And I press "bim.add_material(obj='')"
    When I press "bim.load_materials"
    Then nothing happens

Scenario: Disable editing materials
    Given an empty IFC project
    And I press "bim.add_material(obj='')"
    And I press "bim.load_materials"
    When I press "bim.disable_editing_materials"
    Then nothing happens

Scenario: Load materials - then add material
    Given an empty IFC project
    And I press "bim.load_materials"
    When I press "bim.add_material(obj='')"
    Then the material "Default" exists

Scenario: Load materials - then add material set
    Given an empty IFC project
    And I set "scene.BIMMaterialProperties.material_type" to "IfcMaterialLayerSet"
    And I press "bim.load_materials"
    When I press "bim.add_material_set(set_type='IfcMaterialLayerSet')"
    Then nothing happens

Scenario: Add default material
    Given an empty IFC project
    When I press "bim.add_material(obj='')"
    Then the material "Default" exists

Scenario: Add material
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add a material
    When I press "bim.add_material(obj='Material')"
    Then the material "Material" is an IFC material

Scenario: Remove material
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add a material
    And I press "bim.add_material(obj='Material')"
    And the variable "material" is "{ifc}.by_type('IfcMaterial')[0].id()"
    When I press "bim.remove_material(material={material})"
    Then the material "Material" does not exist

Scenario: Remove material set
    Given an empty IFC project
    And I set "scene.BIMMaterialProperties.material_type" to "IfcMaterialLayerSet"
    And I press "bim.load_materials"
    And I press "bim.add_material_set(set_type='IfcMaterialLayerSet')"
    And the variable "material" is "{ifc}.by_type('IfcMaterialLayerSet')[0].id()"
    When I press "bim.remove_material_set(material={material})"
    Then nothing happens

Scenario: Unlink material
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add a material
    And I press "bim.add_material(obj='Material')"
    When I press "bim.unlink_material"
    Then the material "Material" is not an IFC material

Scenario: Assign material - single material
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    When I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterial"
    And I press "bim.assign_material"
    Then the object "IfcWall/Cube" has the material "Default"

Scenario: Unassign material - single material
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterial"
    And I press "bim.assign_material"
    When I press "bim.unassign_material"
    Then the object "IfcWall/Cube" does not have the material "Default"

Scenario: Enable editing assigned material - single material
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterial"
    And I press "bim.assign_material"
    When I press "bim.enable_editing_assigned_material"
    Then nothing happens

Scenario: Disable editing assigned material - single material
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterial"
    And I press "bim.assign_material"
    And I press "bim.enable_editing_assigned_material"
    When I press "bim.disable_editing_assigned_material"
    Then nothing happens

Scenario: Edit assigned material - single material
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterial"
    And I press "bim.assign_material"
    And I press "bim.enable_editing_assigned_material"
    And the variable "material_set" is "{ifc}.by_type('IfcMaterial')[0].id()"
    When I press "bim.edit_assigned_material(material_set={material_set})"
    Then nothing happens

Scenario: Assign material - material layer set
    Given an empty IFC project
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    When I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialLayerSet"
    And I press "bim.assign_material"
    Then the object "IfcWallType/Empty" does not have the material "Default"
    And the object "IfcWallType/Empty" has a "100" thick layered material containing the material "Default"

Scenario: Unassign material - material layer set
    Given an empty IFC project
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialLayerSet"
    And I press "bim.assign_material"
    When I press "bim.unassign_material"
    Then nothing happens

Scenario: Unassign material - material layer set usages will not be removed
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
    And the object "IfcWall/Cube" is selected
    When the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has a "100" thick layered material containing the material "Default"
    When I press "bim.unassign_material"
    Then the object "IfcWall/Cube" has a "100" thick layered material containing the material "Default"

Scenario: Enable editing assigned material - material layer set
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
    When I press "bim.enable_editing_assigned_material"
    Then nothing happens

Scenario: Disable editing assigned material - material layer set
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
    When I press "bim.disable_editing_assigned_material"
    Then nothing happens

Scenario: Edit assigned material - material layer set
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
    And the variable "material_set" is "{ifc}.by_type('IfcMaterialLayerSet')[0].id()"
    When I press "bim.edit_assigned_material(material_set={material_set})"
    Then nothing happens

Scenario: Assign material - material profile set
    Given an empty IFC project
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    When I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialProfileSet"
    And I press "bim.assign_material"
    Then the object "IfcWallType/Empty" does not have the material "Default"
    And the object "IfcWallType/Empty" has a profiled material containing the material "Default" and profile "New Profile"

Scenario: Unassign material - material profile set
    Given an empty IFC project
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialProfileSet"
    And I press "bim.assign_material"
    When I press "bim.unassign_material"
    Then nothing happens

Scenario: Enable editing assigned material - material profile set
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
    When I press "bim.enable_editing_assigned_material"
    Then nothing happens

Scenario: Disable editing assigned material - material profile set
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
    When I press "bim.disable_editing_assigned_material"
    Then nothing happens

Scenario: Edit assigned material - material profile set
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
    And the variable "material_set" is "{ifc}.by_type('IfcMaterialProfileSet')[0].id()"
    When I press "bim.edit_assigned_material(material_set={material_set})"
    Then nothing happens

Scenario: Assign material - material constituent set
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    When I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialConstituentSet"
    And I press "bim.assign_material"
    Then nothing happens

Scenario: Unassign material - material constituent set
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialConstituentSet"
    And I press "bim.assign_material"
    When I press "bim.unassign_material"
    Then nothing happens

Scenario: Enable editing assigned material - material constituent set
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialConstituentSet"
    And I press "bim.assign_material"
    When I press "bim.enable_editing_assigned_material"
    Then nothing happens

Scenario: Disable editing assigned material - material constituent set
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialConstituentSet"
    And I press "bim.assign_material"
    And I press "bim.enable_editing_assigned_material"
    When I press "bim.disable_editing_assigned_material"
    Then nothing happens

Scenario: Edit assigned material - material constituent set
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialConstituentSet"
    And I press "bim.assign_material"
    And I press "bim.enable_editing_assigned_material"
    And the variable "material_set" is "{ifc}.by_type('IfcMaterialConstituentSet')[0].id()"
    When I press "bim.edit_assigned_material(material_set={material_set})"
    Then nothing happens

Scenario: Select by material
    Given an empty IFC project
    And I press "bim.load_materials"
    And I press "bim.add_material(obj='')"
    And the variable "material" is "{ifc}.by_type('IfcMaterial')[0].id()"
    When I press "bim.select_by_material(material={material})"
    Then nothing happens

Scenario: Expand material category
    Given an empty IFC project
    And I press "bim.load_materials"
    And I press "bim.add_material(obj='')"
    When I press "bim.expand_material_category(category='')"
    Then nothing happens

Scenario: Contract material category
    Given an empty IFC project
    And I press "bim.load_materials"
    And I press "bim.add_material(obj='')"
    And I press "bim.expand_material_category(category='')"
    When I press "bim.contract_material_category(category='')"
    Then nothing happens

Scenario: Enable editing material set item
    Given an empty IFC project
    And I load the demo construction library
    When I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the variable "column" is "{ifc}.by_type('IfcColumn')[0].id()"
    And the object "IfcColumn/Column" is selected
    And the variable "column_type" is "{ifc}.by_id({column}).IsTypedBy[0].RelatingType.id()"
    And the variable "relating_material" is "{ifc}.by_id({column_type}).HasAssociations[0].RelatingMaterial.id()"
    And the variable "material_profile" is "{ifc}.by_id({column_type}).HasAssociations[0].RelatingMaterial.MaterialProfiles[0].id()"
    And I press "bim.enable_editing_assigned_material"
    When I press "bim.enable_editing_material_set_item(material_set_item={material_profile})"
    Then nothing happens

Scenario: Add material set layer
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
    And the variable "material_set" is "{ifc}.by_type('IfcMaterialLayerSet')[0].id()"
    When I press "bim.add_layer(layer_set={material_set})"
    Then nothing happens

Scenario: Remove material set layer
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
    And the variable "material_set" is "{ifc}.by_type('IfcMaterialLayerSet')[0].id()"
    And I press "bim.remove_layer(layer={ifc}.by_id({material_set}).MaterialLayers[0].id())"
    And I press "bim.add_layer(layer_set={material_set})"
    When I press "bim.remove_layer(layer={ifc}.by_id({material_set}).MaterialLayers[0].id())"
    Then nothing happens
