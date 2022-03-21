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

Scenario: Assign material - Assign a material
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    When I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterial"
    And I press "bim.assign_material"
    Then the object "IfcWall/Cube" has the material "Default"

Scenario: Assign material - Assign a material layer set
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
    When I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialLayerSet"
    And I press "bim.assign_material"
    Then nothing happens

Scenario: Assign material - Assign a material profile set
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
    When I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterialProfileSet"
    And I press "bim.assign_material"
    Then nothing happens
