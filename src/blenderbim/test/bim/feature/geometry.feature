@geometry
Feature: Geometry

Scenario: Edit object placement
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When I press "bim.edit_object_placement"
    Then nothing happens

Scenario: Add representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    Then the object "IfcWall/Cube" data is a "Tessellation" representation of "Model/Body/MODEL_VIEW"
    When the variable "context" is "[c for c in {ifc}.by_type('IfcGeometricRepresentationSubContext') if c.TargetView == 'PLAN_VIEW'][0].id()"
    And I set "scene.BIMRootProperties.contexts" to "{context}"
    And I press "bim.add_representation"
    Then the object "IfcWall/Cube" data is a "Annotation2D" representation of "Plan/Annotation/PLAN_VIEW"

Scenario: Add representation - add a new representation to a typed instance
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I press "bim.add_constr_type_instance"
    And I press "bim.add_constr_type_instance"
    Then the object "IfcWall/Wall" data is a "Tessellation" representation of "Model/Body/MODEL_VIEW"
    And the object "IfcWall/Wall.001" data is a "Tessellation" representation of "Model/Body/MODEL_VIEW"
    When the object "IfcWall/Wall" is selected
    And the variable "context" is "[c for c in {ifc}.by_type('IfcGeometricRepresentationSubContext') if c.TargetView == 'PLAN_VIEW'][0].id()"
    And I set "scene.BIMRootProperties.contexts" to "{context}"
    And I press "bim.add_representation"
    Then the object "IfcWall/Wall" data is a "Annotation2D" representation of "Plan/Annotation/PLAN_VIEW"
    And the object "IfcWall/Wall.001" data is a "Annotation2D" representation of "Plan/Annotation/PLAN_VIEW"

Scenario: Add representation - add a representation with a scale factor applied
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    When the object "Cube" is scaled to "2"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    Then the object "IfcWall/Cube" has no scale
    And the object "IfcWall/Cube" dimensions are "4,4,4"

Scenario: Add representation - add a representation with a scale factor removed due to multiple users
    Given an empty IFC project
    And I add a cube
    And I press "object.duplicate_move_linked"
    And the object "Cube" is selected
    When the object "Cube" is scaled to "2"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    Then the object "IfcWall/Cube" has no scale
    And the object "IfcWall/Cube" dimensions are "2,2,2"

Scenario: Switch representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When the variable "representation" is "{ifc}.by_type('IfcShapeRepresentation')[0].id()"
    And I press "bim.switch_representation(obj='IfcWall/Cube', ifc_definition_id={representation})"
    Then nothing happens

Scenario: Switch representation - current edited representation is updated prior to switch
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the variable "context" is "[c for c in {ifc}.by_type('IfcGeometricRepresentationSubContext') if c.ContextIdentifier=='Annotation'][0].id()"
    And I set "scene.BIMRootProperties.contexts" to "{context}"
    And I press "bim.add_representation"
    When the object "IfcWall/Cube" is scaled to "2"
    And the variable "representation" is "[r for r in {ifc}.by_type('IfcShapeRepresentation') if r.RepresentationType=='Tessellation'][0].id()"
    And I press "bim.switch_representation(ifc_definition_id={representation}, should_reload=True)"
    And the variable "representation" is "[r for r in {ifc}.by_type('IfcShapeRepresentation') if r.RepresentationType=='Annotation2D'][0].id()"
    And I press "bim.switch_representation(ifc_definition_id={representation}, should_reload=True)"
    When I press "export_ifc.bim(filepath='{cwd}/test/files/export.ifc')"
    Then the object "IfcWall/Cube" dimensions are "4,4,0"

Scenario: Switch representation - current edited representation is discarded if switching to a box
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When the object "IfcWall/Cube" is scaled to "2"
    And the variable "representation" is "{ifc}.by_type('IfcShapeRepresentation')[-1].id()"
    And I press "bim.switch_representation(obj='IfcWall/Cube', ifc_definition_id={representation}, should_reload=True)"
    And the variable "representation" is "{ifc}.by_type('IfcShapeRepresentation')[0].id()"
    And I press "bim.switch_representation(obj='IfcWall/Cube', ifc_definition_id={representation}, should_reload=True)"
    When I press "export_ifc.bim(filepath='{cwd}/test/files/export.ifc')"
    Then the object "IfcWall/Cube" dimensions are "2,2,2"

Scenario: Switch representation - existing Blender modifiers must be purged
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add an array modifier
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When the variable "representation" is "{ifc}.by_type('IfcShapeRepresentation')[0].id()"
    And I press "bim.switch_representation(obj='IfcWall/Cube', ifc_definition_id={representation})"
    Then the object "IfcWall/Cube" has no modifiers

Scenario: Remove representation - remove an active representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add an array modifier
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When the variable "representation" is "{ifc}.by_type('IfcShapeRepresentation')[0].id()"
    And I press "bim.remove_representation(representation_id={representation})"
    Then the object "IfcWall/Cube" has no data

Scenario: Remove representation - remove an unloaded representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add an array modifier
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When the variable "representation" is "{ifc}.by_type('IfcShapeRepresentation')[1].id()"
    And I press "bim.remove_representation(representation_id={representation})"
    Then the object "IfcWall/Cube" has data which is an IFC representation

Scenario: Remove representation - remove an instanced representation from an active type object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "cube" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{cube}"
    And I press "bim.add_constr_type_instance"
    And I press "bim.add_constr_type_instance"
    And the object "IfcWallType/Cube" is selected
    When the variable "representation" is "{ifc}.by_type('IfcWallType')[0].RepresentationMaps[1].MappedRepresentation.id()"
    And I press "bim.remove_representation(representation_id={representation})"
    Then the object "IfcWallType/Cube" has no data
    Then the object "IfcWall/Wall" has no data
    Then the object "IfcWall/Wall.001" has no data

Scenario: Remove representation - remove an instanced representation from an active instance object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "cube" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{cube}"
    And I press "bim.add_constr_type_instance"
    And I press "bim.add_constr_type_instance"
    And the object "IfcWall/Wall" is selected
    When the variable "representation" is "{ifc}.by_type('IfcWall')[0].Representation.Representations[1].id()"
    And I press "bim.remove_representation(representation_id={representation})"
    Then the object "IfcWallType/Cube" has no data
    Then the object "IfcWall/Wall" has no data
    Then the object "IfcWall/Wall.001" has no data

Scenario: Update representation - updating a tessellation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.update_representation(obj='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"

Scenario: Update representation - updating a layered extrusion
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
    And the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    When I press "bim.update_representation(obj='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has a "SweptSolid" representation of "Model/Body/MODEL_VIEW"

Scenario: Update representation - updating a profiled extrusion
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
    And the variable "profile_set" is "{ifc}.by_type("IfcMaterialProfileSet")[0].id()"
    And I press "bim.add_profile(profile_set={profile_set})"
    And the variable "profile" is "{ifc}.by_type("IfcMaterialProfile")[0].id()"
    And I press "bim.enable_editing_material_set_item(material_set_item={profile})"
    And I set "active_object.BIMObjectMaterialProperties.profile_classes" to "IfcParameterizedProfileDef"
    And I set "active_object.BIMObjectMaterialProperties.parameterized_profile_classes" to "IfcCircleProfileDef"
    And I press "bim.assign_parameterized_profile(ifc_class='IfcCircleProfileDef', material_profile={profile})"
    And I set "active_object.BIMObjectMaterialProperties.material_set_item_profile_attributes[2].float_value" to "0.2"
    And I press "bim.edit_material_set_item(material_set_item={profile})"
    And I press "bim.edit_assigned_material(material_set={profile_set})"
    And the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    When I press "bim.update_representation(obj='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has a "SweptSolid" representation of "Model/Body/MODEL_VIEW"

Scenario: Get representation IFC parameters
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.update_representation(ifc_representation_class='IfcExtrudedAreaSolid/IfcRectangleProfileDef')"
    When I press "bim.get_representation_ifc_parameters"
    Then nothing happens

Scenario: Copy representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcWall/Cube.001" is selected
    When I press "bim.copy_representation"
    Then nothing happens

Scenario: Override delete - without active IFC data
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "object.delete"
    Then the object "Cube" does not exist

Scenario: Override delete - with active IFC data
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When I press "object.delete"
    Then the object "IfcWall/Cube" does not exist

Scenario: Override outliner delete
    Given an untestable scenario
    Then nothing happens

Scenario: Override duplicate move - without active IFC data
    Given an empty Blender session
    And I add a cube
    And I add an empty
    And the object "Cube" is selected
    And additionally the object "Empty" is selected
    When I press "object.duplicate_move"
    Then the object "Cube" exists
    And the object "Cube.001" exists

Scenario: Override duplicate move - with active IFC data
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcBuildingStorey/My Storey" is selected
    When I press "object.duplicate_move"
    Then the object "IfcWall/Cube" exists
    And the object "IfcWall/Cube" is an "IfcWall"
    And the object "IfcWall/Cube.001" exists
    And the object "IfcWall/Cube.001" is an "IfcWall"
    And the object "IfcWall/Cube.001" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"
    And the object "IfcBuildingStorey/My Storey.001" exists
    And the object "IfcBuildingStorey/My Storey.001" is an "IfcBuildingStorey"

Scenario: Override duplicate move - copying a coloured representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add a material
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And the material "Material" colour is set to "1,0,0,1"
    When I press "object.duplicate_move"
    And I press "export_ifc.bim(filepath='{cwd}/test/files/export.ifc')"
    And an empty Blender session is started
    And I press "bim.load_project(filepath='{cwd}/test/files/export.ifc')"
    Then the material "Material" colour is "1,0,0,1"
    And the object "IfcWall/Cube" has the material "Material"
    And the object "IfcWall/Cube.001" has the material "Material"

Scenario: Override duplicate move - copying a type instance with a representation map
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "cube" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{cube}"
    And I press "bim.add_constr_type_instance"
    And the object "IfcWall/Wall" is selected
    When I press "object.duplicate_move"
    Then the object "IfcWall/Wall.001" exists
    And the object "IfcWall/Wall.001" has a "MappedRepresentation" representation of "Model/Body/MODEL_VIEW"

Scenario: Override duplicate move - copying a layered extrusion
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
    And the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    And the object "IfcWall/Cube" is selected
    When I press "object.duplicate_move"
    Then the object "IfcWall/Cube.001" exists
    Then the object "IfcWall/Cube.001" has a "SweptSolid" representation of "Model/Body/MODEL_VIEW"

Scenario: Override duplicate move - copying a profiled extrusion
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
    And the variable "profile_set" is "{ifc}.by_type("IfcMaterialProfileSet")[0].id()"
    And I press "bim.add_profile(profile_set={profile_set})"
    And the variable "profile" is "{ifc}.by_type("IfcMaterialProfile")[0].id()"
    And I press "bim.enable_editing_material_set_item(material_set_item={profile})"
    And I set "active_object.BIMObjectMaterialProperties.profile_classes" to "IfcParameterizedProfileDef"
    And I set "active_object.BIMObjectMaterialProperties.parameterized_profile_classes" to "IfcCircleProfileDef"
    And I press "bim.assign_parameterized_profile(ifc_class='IfcCircleProfileDef', material_profile={profile})"
    And I set "active_object.BIMObjectMaterialProperties.material_set_item_profile_attributes[2].float_value" to "0.2"
    And I press "bim.edit_material_set_item(material_set_item={profile})"
    And I press "bim.edit_assigned_material(material_set={profile_set})"
    And the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    And the object "IfcWall/Cube" is selected
    When I press "object.duplicate_move"
    Then the object "IfcWall/Cube.001" exists
    Then the object "IfcWall/Cube.001" has a "SweptSolid" representation of "Model/Body/MODEL_VIEW"

Scenario: Override duplicate move linked - without active IFC data
    Given an empty Blender session
    And I add a cube
    And I add an empty
    And the object "Cube" is selected
    And additionally the object "Empty" is selected
    When I press "object.duplicate_move_linked"
    Then the object "Cube" exists
    And the object "Cube.001" exists

Scenario: Override duplicate move linked - with active IFC data
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcBuildingStorey/My Storey" is selected
    When I press "object.duplicate_move_linked"
    Then the object "IfcWall/Cube" exists
    And the object "IfcWall/Cube" is an "IfcWall"
    And the object "IfcWall/Cube.001" exists
    And the object "IfcWall/Cube.001" is an "IfcWall"
    And the object "IfcWall/Cube.001" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"
    And the object "IfcBuildingStorey/My Storey.001" exists
    And the object "IfcBuildingStorey/My Storey.001" is an "IfcBuildingStorey"

Scenario: Override paste buffer - without active IFC data
    Given an empty Blender session
    And I add a cube
    And I add an empty
    And the object "Cube" is selected
    And additionally the object "Empty" is selected
    When I press "view3d.copybuffer"
    And I press "bim.override_paste_buffer"
    Then the object "Cube" exists
    And the object "Cube.001" exists

Scenario: Override paste buffer - with active IFC data
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcBuildingStorey/My Storey" is selected
    When I press "view3d.copybuffer"
    And I press "bim.override_paste_buffer"
    Then the object "IfcWall/Cube" exists
    And the object "IfcWall/Cube" is an "IfcWall"
    And the object "IfcWall/Cube.001" exists
    And the object "IfcWall/Cube.001" is an "IfcWall"
    And the object "IfcWall/Cube.001" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"
    And the object "IfcBuildingStorey/My Storey.001" exists
    And the object "IfcBuildingStorey/My Storey.001" is an "IfcBuildingStorey"
