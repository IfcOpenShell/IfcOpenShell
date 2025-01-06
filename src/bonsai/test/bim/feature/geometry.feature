@geometry
Feature: Geometry

Scenario: Edit object placement
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When I press "bim.edit_object_placement"
    Then nothing happens

Scenario: Add representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    Then the object "IfcWall/Cube" data is a "Tessellation" representation of "Model/Body/MODEL_VIEW"
    When the variable "context" is "[c for c in {ifc}.by_type('IfcGeometricRepresentationSubContext') if c.ContextType == 'Plan' and c.ContextIdentifier == 'Body' and c.TargetView == 'PLAN_VIEW'][0].id()"
    And I set "active_object.BIMGeometryProperties.contexts" to "{context}"
    And I press "bim.add_representation"
    Then the object "IfcWall/Cube" data is a "Annotation2D" representation of "Plan/Body/PLAN_VIEW"

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
    And the variable "context" is "[c for c in {ifc}.by_type('IfcGeometricRepresentationSubContext') if c.ContextType == 'Plan' and c.ContextIdentifier == 'Body' and c.TargetView == 'PLAN_VIEW'][0].id()"
    And I set "active_object.BIMGeometryProperties.contexts" to "{context}"
    And I press "bim.add_representation"
    Then the object "IfcWall/Wall" data is a "Annotation2D" representation of "Plan/Body/PLAN_VIEW"
    And the object "IfcWall/Wall.001" data is a "Annotation2D" representation of "Plan/Body/PLAN_VIEW"

Scenario: Add representation - add a representation with a scale factor applied
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    When the object "Cube" is scaled to "2"
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
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
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    Then the object "IfcWall/Cube" has no scale
    And the object "IfcWall/Cube" dimensions are "2,2,2"

Scenario: Switch representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When the variable "representation" is "{ifc}.by_type('IfcShapeRepresentation')[0].id()"
    And I press "bim.switch_representation(obj='IfcWall/Cube', ifc_definition_id={representation})"
    Then nothing happens

Scenario: Switch representation - current edited representation is updated prior to switch
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the variable "context" is "[c for c in {ifc}.by_type('IfcGeometricRepresentationSubContext') if c.ContextType == 'Plan' and c.ContextIdentifier=='Annotation'][0].id()"
    And I set "active_object.BIMGeometryProperties.contexts" to "{context}"
    And I press "bim.add_representation"
    When the object "IfcWall/Cube" is scaled to "2"
    And the variable "representation" is "[r for r in {ifc}.by_type('IfcShapeRepresentation') if r.RepresentationType=='Tessellation'][0].id()"
    And I press "bim.switch_representation(ifc_definition_id={representation}, should_reload=True)"
    And the variable "representation" is "[r for r in {ifc}.by_type('IfcShapeRepresentation') if r.RepresentationType=='Annotation2D'][0].id()"
    And I press "bim.switch_representation(ifc_definition_id={representation}, should_reload=True)"
    When I press "bim.save_project(filepath='{cwd}/test/files/temp/export.ifc')"
    Then the object "IfcWall/Cube" dimensions are "4,4,0"

Scenario: Switch representation - current edited representation is discarded if switching to a box
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When the object "IfcWall/Cube" is scaled to "2"
    And the variable "representation" is "{ifc}.by_type('IfcShapeRepresentation')[-1].id()"
    And I press "bim.switch_representation(obj='IfcWall/Cube', ifc_definition_id={representation}, should_reload=True)"
    And the variable "representation" is "{ifc}.by_type('IfcShapeRepresentation')[0].id()"
    And I press "bim.switch_representation(obj='IfcWall/Cube', ifc_definition_id={representation}, should_reload=True)"
    When I press "bim.save_project(filepath='{cwd}/test/files/temp/export.ifc')"
    Then the object "IfcWall/Cube" dimensions are "2,2,2"

Scenario: Switch representation - existing Blender modifiers must be purged
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add an array modifier
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
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
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When the variable "representation_body" is "{ifc}.by_type('IfcShapeRepresentation')[0].id()"
    And the variable "representation_bbox" is "{ifc}.by_type('IfcShapeRepresentation')[1].id()"
    And I press "bim.remove_representation(representation_id={representation_body})"
    And I press "bim.remove_representation(representation_id={representation_bbox})"
    Then the object "IfcWall/Cube" has no data

Scenario: Remove representation - remove an unloaded representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add an array modifier
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
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
    When the variable "representation_body" is "{ifc}.by_type('IfcWallType')[0].RepresentationMaps[1].MappedRepresentation.id()"
    And the variable "representation_bbox" is "{ifc}.by_type('IfcWallType')[0].RepresentationMaps[0].MappedRepresentation.id()"
    And I press "bim.remove_representation(representation_id={representation_body})"
    And I press "bim.remove_representation(representation_id={representation_bbox})"
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
    When the variable "representation_body" is "{ifc}.by_type('IfcWall')[0].Representation.Representations[1].id()"
    And the variable "representation_bbox" is "{ifc}.by_type('IfcWall')[0].Representation.Representations[0].id()"
    And I press "bim.remove_representation(representation_id={representation_body})"
    And I press "bim.remove_representation(representation_id={representation_bbox})"
    Then the object "IfcWallType/Cube" has no data
    Then the object "IfcWall/Wall" has no data
    Then the object "IfcWall/Wall.001" has no data

Scenario: Update representation - updating a tessellation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.update_representation(obj='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"

Scenario: Update representation - updating a layered extrusion
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
    And the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    Then the object "IfcWall/Cube" has a "SweptSolid" representation of "Model/Body/MODEL_VIEW"

Scenario: Get representation IFC parameters
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.update_representation(ifc_representation_class='IfcExtrudedAreaSolid/IfcRectangleProfileDef')"
    When I press "bim.get_representation_ifc_parameters"
    Then nothing happens

Scenario: Copy representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
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
    When I press "bim.override_object_delete"
    Then the object "Cube" does not exist

Scenario: Override delete - with active IFC data
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When I press "bim.override_object_delete"
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
    When I duplicate the selected objects
    Then the object "Cube" exists
    And the object "Cube.001" exists

Scenario: Override duplicate move - with active IFC data
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcBuildingStorey/My Storey" is selected
    When I duplicate the selected objects
    Then the object "IfcWall/Cube" exists
    And the object "IfcWall/Cube" is an "IfcWall"
    And the object "IfcWall/Cube.001" exists
    And the object "IfcWall/Cube.001" is an "IfcWall"
    And the object "IfcWall/Cube.001" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"
    And the object "IfcBuildingStorey/My Storey.001" does not exist

Scenario: Override duplicate move - with unlocked elements
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcBuildingStorey/My Storey" is selected
    And I set "scene.BIMSpatialDecompositionProperties.is_locked" to "False"
    When I duplicate the selected objects
    Then the object "IfcBuildingStorey/My Storey.001" exists
    And the object "IfcBuildingStorey/My Storey.001" is an "IfcBuildingStorey"

Scenario: Override duplicate move - copying a coloured representation
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.load_styles(style_type='IfcSurfaceStyle')"
    And I press "bim.enable_adding_presentation_style"
    And I set "scene.BIMStylesProperties.style_name" to "Style"
    And I set "scene.BIMStylesProperties.surface_colour" to "[1.0,0.0,0.0]"
    And I press "bim.add_presentation_style"
    And the variable "style" is "{ifc}.by_type('IfcSurfaceStyle')[0].id()"
    And I press "bim.assign_style_to_selected(style_id={style})"
    When I duplicate the selected objects
    And I press "bim.save_project(filepath='{cwd}/test/files/temp/export.ifc')"
    And an empty Blender session is started
    And I press "bim.load_project(filepath='{cwd}/test/files/temp/export.ifc', should_start_fresh_session=False)"
    Then the material "Style" colour is "1,0,0,1"
    And the object "IfcWall/Cube" has the material "Style"
    And the object "IfcWall/Cube.001" has the material "Style"

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
    When I duplicate the selected objects
    Then the object "IfcWall/Wall.001" exists
    And the object "IfcWall/Wall.001" has a "MappedRepresentation" representation of "Model/Body/MODEL_VIEW"

Scenario: Override duplicate move - copying a layered extrusion
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
    When I duplicate the selected objects
    Then the object "IfcWall/Cube.001" exists
    Then the object "IfcWall/Cube.001" has a "SweptSolid" representation of "Model/Body/MODEL_VIEW"

Scenario: Override duplicate move - copying a profiled extrusion
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
    And the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object='IfcWall/Cube')"
    And the object "IfcWall/Cube" is selected
    When I duplicate the selected objects
    Then the object "IfcWall/Cube.001" exists
    Then the object "IfcWall/Cube.001" has a "SweptSolid" representation of "Model/Body/MODEL_VIEW"

Scenario: Override duplicate move - copying an aggregate
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When I press "bim.add_aggregate(aggregate_name='Assembly')"
    When the object "IfcWall/Cube" is selected
    And additionally the object "IfcElementAssembly/Assembly" is selected
    When I duplicate the selected objects
    Then the object "IfcWall/Cube.001" exists
    And the object "IfcElementAssembly/Assembly.001" exists
    And the object "IfcWall/Cube.001" is aggregated by object "IfcElementAssembly/Assembly.001"
    And the object "IfcElementAssembly/Assembly.001" is contained in object "IfcBuildingStorey/My Storey"

Scenario: Override duplicate move - copying objects with connection
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    When I press "bim.add_constr_type_instance"
    Then the object "IfcWall/Wall" is an "IfcWall"
    And the object "IfcWall/Wall" dimensions are "1,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0,0,0"
    When I set "scene.BIMModelProperties.ifc_class" to "IfcSlabType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcSlabType') if e.Name == 'FLR200'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    When I press "bim.add_constr_type_instance"
    Then the object "IfcSlab/Slab" is an "IfcSlab"
    When the object "IfcSlab/Slab" is selected
    And the object "IfcSlab/Slab" is moved to "0,0,4"
    When I deselect all objects
    And the object "IfcWall/Wall" is selected
    And additionally the object "IfcSlab/Slab" is selected
    When I press "bim.hotkey(hotkey='S_E')"
    Then the object "IfcWall/Wall" dimensions are "1,0.1,4"
    When I duplicate the selected objects
    Then the object "IfcWall/Wall.001" exists
    And the variable "wall_name" is "[o.name for o in bpy.context.selected_objects if o.name == 'IfcWall/Wall.001'][0]"
    Then the object "IfcSlab/Slab.001" exists
    And the variable "slab_name" is "[o.name for o in bpy.context.selected_objects if o.name == 'IfcSlab/Slab.001'][0]"
    Then the object "{wall_name}" has a connection with "{slab_name}"

Scenario: Override duplicate move - copying walls with mitre joint
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.hotkey(hotkey='S_A')"
    And the cursor is at "0.5,0,0"
    And I press "bim.hotkey(hotkey='S_A')"
    And the object "IfcWall/Wall.001" is selected
    And additionally the object "IfcWall/Wall" is selected
    When I press "bim.hotkey(hotkey='S_Y')"
    Then the object "IfcWall/Wall" dimensions are "0.5,0.1,3"
    And the object "IfcWall/Wall" bottom left corner is at "0.5,0,0"
    And the object "IfcWall/Wall.001" dimensions are "1.1,0.1,3"
    And the object "IfcWall/Wall.001" bottom left corner is at "0.5,0.1,0"
    And the object "IfcWall/Wall.001" top right corner is at "0.6,-1,3"
    When I deselect all objects
    And the object "IfcWall/Wall.001" is selected
    And additionally the object "IfcWall/Wall" is selected
    When I duplicate the selected objects
    Then the object "IfcWall/Wall.002" exists
    And the variable "wall_name1" is "[o.name for o in bpy.context.selected_objects if o.name == 'IfcWall/Wall.002'][0]"
    Then the object "IfcWall/Wall.003" exists
    And the variable "wall_name2" is "[o.name for o in bpy.context.selected_objects if o.name == 'IfcWall/Wall.003'][0]"
    Then the object "{wall_name1}" has a connection with "{wall_name2}"

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
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
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
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcBuildingStorey/My Storey" is selected
    When I press "view3d.copybuffer"
    # IFC elements unlinked on paste for safety
    And I press "bim.override_paste_buffer"
    Then the object "IfcWall/Cube" exists
    And the object "IfcWall/Cube" is an "IfcWall"
    And the object "Cube.001" exists
    And the object "Cube.001" is not an IFC element
    And the object "My Storey.001" exists
    And the object "My Storey.001" is not an IFC element

Scenario: Duplicate linked aggregate
    Given I load the IFC test file "/test/files/linked-aggregates.ifc"
    And the object "IfcWall/Wall_01" is selected
    When I duplicate linked aggregate the selected objects
    Then the object "IfcWall/Wall_01.001" exists
    And the object "IfcWall/Wall_02.001" exists
    And the object "IfcElementAssembly/Assembly_01" exists
    Then the object "IfcElementAssembly/Assembly" and "IfcElementAssembly/Assembly_01" belong to the same Linked Aggregate Group

Scenario: Refresh linked aggregate
    Given I load the IFC test file "/test/files/linked-aggregates.ifc"
    And the object "IfcWall/Wall_01" is selected
    When I duplicate linked aggregate the selected objects
    Then the object "IfcWall/Wall_01.001" exists
    When I deselect all objects
    And the object "IfcWall/Wall_01.001" is selected
    When the object layer length is set to "3"
    Then the object "IfcWall/Wall_01.001" dimensions are "3,0.1,3"
    When I refresh linked aggregate the selected object
    Then the object "IfcWall/Wall_01" exists
    And the object "IfcWall/Wall_01" dimensions are "3,0.1,3"

Scenario: Refresh linked aggregate - after deleting an object
    Given I load the IFC test file "/test/files/linked-aggregates.ifc"
    And the object "IfcWall/Wall_01" is selected
    When I duplicate linked aggregate the selected objects
    Then the object "IfcWall/Wall_01.001" exists
    When I deselect all objects
    And the object "IfcWall/Wall_01.001" is selected
    And I delete the selected objects
    When I deselect all objects
    And the object "IfcWall/Wall_02.001" is selected
    When I refresh linked aggregate the selected object
    Then the object "IfcWall/Wall_01" does not exist
    And the object "IfcWall/Wall_02" exists

Scenario: Refresh linked aggregate - after duplicating an object
    Given I load the IFC test file "/test/files/linked-aggregates.ifc"
    And the object "IfcWall/Wall_01" is selected
    When I duplicate linked aggregate the selected objects
    Then the object "IfcWall/Wall_01.001" exists
    And the object "IfcWall/Wall_02.001" exists
    When I deselect all objects
    And the object "IfcWall/Wall_01" is selected
    When I duplicate the selected objects
    Then the object "IfcWall/Wall_01.002" exists
    When I rename the object "IfcWall/Wall_01.002" to "IfcWall/Wall_03"
    And I deselect all objects
    And the object "IfcWall/Wall_03" is selected
    When I refresh linked aggregate the selected object
    Then the object "IfcWall/Wall_01.001" exists
    And the object "IfcWall/Wall_02.001" exists
    And the object "IfcWall/Wall_03.001" exists
