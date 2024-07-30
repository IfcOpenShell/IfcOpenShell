@project
Feature: Project

Scenario: Create project
    Given an empty Blender session
    When I press "bim.create_project"
    Then an IFC file exists
    And the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" is an "IfcSite"
    And the object "IfcBuilding/My Building" is an "IfcBuilding"
    And the object "IfcBuildingStorey/My Storey" is an "IfcBuildingStorey"
    And the object "IfcProject/My Project" is in the collection "IfcProject/My Project"
    And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
    And the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"

Scenario: Create project - IFC2X3
    Given an empty Blender session
    And I set "scene.BIMProjectProperties.export_schema" to "IFC2X3"
    When I press "bim.create_project"
    Then an IFC file exists
    And the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" is an "IfcSite"
    And the object "IfcBuilding/My Building" is an "IfcBuilding"
    And the object "IfcBuildingStorey/My Storey" is an "IfcBuildingStorey"
    And the object "IfcProject/My Project" is in the collection "IfcProject/My Project"
    And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
    And the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"

Scenario: New project - metric (m) preset
    Given an empty Blender session
    When I press "bim.new_project(preset='metric_m')"
    Then an IFC file exists
    And the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" is an "IfcSite"
    And the object "IfcBuilding/My Building" is an "IfcBuilding"
    And the object "IfcBuildingStorey/My Storey" is an "IfcBuildingStorey"
    And the object "IfcProject/My Project" is in the collection "IfcProject/My Project"
    And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
    And the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"

Scenario: New project - metric (mm) preset
    Given an empty Blender session
    When I press "bim.new_project(preset='metric_mm')"
    Then an IFC file exists
    And the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" is an "IfcSite"
    And the object "IfcBuilding/My Building" is an "IfcBuilding"
    And the object "IfcBuildingStorey/My Storey" is an "IfcBuildingStorey"
    And the object "IfcProject/My Project" is in the collection "IfcProject/My Project"
    And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
    And the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"

Scenario: New project - imperial (ft) preset
    Given an empty Blender session
    When I press "bim.new_project(preset='imperial_ft')"
    Then an IFC file exists
    And the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" is an "IfcSite"
    And the object "IfcBuilding/My Building" is an "IfcBuilding"
    And the object "IfcBuildingStorey/My Storey" is an "IfcBuildingStorey"
    And the object "IfcProject/My Project" is in the collection "IfcProject/My Project"
    And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
    And the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"

Scenario: New project - demo preset
    Given an empty Blender session
    When I press "bim.new_project(preset='demo')"
    Then an IFC file exists
    And the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" is an "IfcSite"
    And the object "IfcBuilding/My Building" is an "IfcBuilding"
    And the object "IfcBuildingStorey/My Storey" is an "IfcBuildingStorey"
    And the object "IfcProject/My Project" is in the collection "IfcProject/My Project"
    And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
    And the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcBeamType/B1" is an "IfcBeamType"
    And the object "IfcWallType/WAL50" is an "IfcWallType"

Scenario: New project - wizard
    Given an empty Blender session
    When I press "bim.new_project(preset='wizard')"
    Then an IFC file does not exist
    And the object "IfcProject/My Project" does not exist

Scenario: Append library element
    Given an empty IFC project
    When I press "bim.select_library_file(filepath='{cwd}/test/files/basic.ifc')"
    And I press "bim.change_library_element(element_name='IfcTypeProduct')"
    And I press "bim.change_library_element(element_name='IfcSlabType')"
    And I press "bim.append_library_element(definition=242, prop_index=0)"
    Then the object "IfcSlabType/Slab" is an "IfcSlabType"
    And the object "IfcSlabType/Slab" is in the collection "IfcTypeProduct"

Scenario: Append library element - append two elements sharing a material
    Given an empty IFC project
    And I press "bim.select_library_file(filepath='{cwd}/test/files/basic.ifc')"
    And I press "bim.change_library_element(element_name='IfcTypeProduct')"
    And I press "bim.change_library_element(element_name='IfcSlabType')"
    And I press "bim.append_library_element(definition=242, prop_index=0)"
    When I press "bim.rewind_library"
    And I press "bim.change_library_element(element_name='IfcWallType')"
    And I press "bim.append_library_element(definition=291, prop_index=0)"
    Then the object "IfcSlabType/Slab" is an "IfcSlabType"
    And the object "IfcSlabType/Slab" is in the collection "IfcTypeProduct"
    And the object "IfcWallType/Wall" is an "IfcWallType"
    And the object "IfcWallType/Wall" is in the collection "IfcTypeProduct"
    And the object "IfcSlabType/Slab" has the material "SurfaceStyle"
    And the object "IfcWallType/Wall" has the material "SurfaceStyle"

Scenario: Load project
    Given an empty Blender session
    When I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc')"
    Then an IFC file exists
    And the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" is an "IfcSite"
    And the object "IfcBuilding/My Building" is an "IfcBuilding"
    And the object "IfcBuildingStorey/Ground Floor" is an "IfcBuildingStorey"
    And the object "IfcBuildingStorey/Level 1" is an "IfcBuildingStorey"
    And the object "IfcSlab/Slab" is an "IfcSlab"
    And the object "IfcWall/Wall" is an "IfcWall"
    And the object "IfcElementAssembly/Empty" is an "IfcElementAssembly"
    And the object "IfcBeam/Beam" is an "IfcBeam"
    And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
    And the object "IfcBuildingStorey/Ground Floor" is in the collection "IfcBuildingStorey/Ground Floor"
    And the object "IfcBuildingStorey/Level 1" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcElementAssembly/Empty" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcBeam/Beam" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcSlab/Slab" is in the collection "IfcBuildingStorey/Ground Floor"
    And the object "IfcWall/Wall" is in the collection "IfcBuildingStorey/Level 1"
    And "scene.BIMProjectProperties.is_loading" is "False"

Scenario: Load project - IfcZip
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifczip')"
    Then the object "IfcProject/My Project" is an "IfcProject"

Scenario: Load project - advanced mode
    Given an empty Blender session
    When I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
    Then an IFC file exists
    And "scene.BIMProjectProperties.is_loading" is "True"
    And the object "IfcProject/My Project" does not exist

Scenario: Load project elements - load all project elements
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.filter_mode" to "NONE"
    And I press "bim.load_project_elements"
    Then the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" is an "IfcSite"
    And the object "IfcBuilding/My Building" is an "IfcBuilding"
    And the object "IfcBuildingStorey/Ground Floor" is an "IfcBuildingStorey"
    And the object "IfcBuildingStorey/Level 1" is an "IfcBuildingStorey"
    And the object "IfcSlab/Slab" is an "IfcSlab"
    And the object "IfcWall/Wall" is an "IfcWall"
    And the object "IfcElementAssembly/Empty" is an "IfcElementAssembly"
    And the object "IfcBeam/Beam" is an "IfcBeam"
    And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
    And the object "IfcBuildingStorey/Ground Floor" is in the collection "IfcBuildingStorey/Ground Floor"
    And the object "IfcBuildingStorey/Level 1" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcElementAssembly/Empty" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcBeam/Beam" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcSlab/Slab" is in the collection "IfcBuildingStorey/Ground Floor"
    And the object "IfcWall/Wall" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcSlab/Slab" has data which is an IFC representation
    And the object "IfcBeam/Beam" has data which is an IFC representation
    And the object "IfcWall/Wall" has data which is an IFC representation
    And the object "IfcSlabType/Slab" has data which is an IFC representation
    And the object "IfcWallType/Wall" has data which is an IFC representation
    And "scene.BIMProjectProperties.is_loading" is "False"

Scenario: Load project elements - load objects filtered by decomposition
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.filter_mode" to "DECOMPOSITION"
    And I set "scene.BIMProjectProperties.should_filter_spatial_elements" to "True"
    Then "scene.BIMProjectProperties.filter_categories['IfcSite/My Site'].total_elements" is "0"
    Then "scene.BIMProjectProperties.filter_categories['IfcBuilding/My Building'].total_elements" is "0"
    Then "scene.BIMProjectProperties.filter_categories['IfcBuildingStorey/Ground Floor'].total_elements" is "1"
    Then "scene.BIMProjectProperties.filter_categories['IfcBuildingStorey/Level 1'].total_elements" is "2"
    When I set "scene.BIMProjectProperties.filter_categories['IfcBuildingStorey/Level 1'].is_selected" to "True"
    And I press "bim.load_project_elements"
    Then the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" is an "IfcSite"
    And the object "IfcBuilding/My Building" is an "IfcBuilding"
    And the object "IfcBuildingStorey/Level 1" is an "IfcBuildingStorey"
    And the object "IfcWall/Wall" is an "IfcWall"
    And the object "IfcElementAssembly/Empty" is an "IfcElementAssembly"
    And the object "IfcBeam/Beam" is an "IfcBeam"
    And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
    And the object "IfcBuildingStorey/Level 1" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcWall/Wall" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcElementAssembly/Empty" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcBeam/Beam" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcBuildingStorey/Ground Floor" does not exist
    And the object "IfcSlab/Slab" does not exist

Scenario: Load project elements - load objects filtered by IFC class
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.filter_mode" to "IFC_CLASS"
    And I set "scene.BIMProjectProperties.should_filter_spatial_elements" to "True"
    Then "scene.BIMProjectProperties.filter_categories['IfcWall'].total_elements" is "1"
    And "scene.BIMProjectProperties.filter_categories['IfcSlab'].total_elements" is "1"
    And "scene.BIMProjectProperties.filter_categories['IfcElementAssembly'].total_elements" is "1"
    And "scene.BIMProjectProperties.filter_categories['IfcBeam'].total_elements" is "1"
    When I set "scene.BIMProjectProperties.filter_categories['IfcSlab'].is_selected" to "True"
    And I press "bim.load_project_elements"
    Then the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" is an "IfcSite"
    And the object "IfcBuilding/My Building" is an "IfcBuilding"
    And the object "IfcBuildingStorey/Ground Floor" is an "IfcBuildingStorey"
    And the object "IfcSlab/Slab" is an "IfcSlab"
    And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
    And the object "IfcBuildingStorey/Ground Floor" is in the collection "IfcBuildingStorey/Ground Floor"
    And the object "IfcSlab/Slab" is in the collection "IfcBuildingStorey/Ground Floor"
    And the object "IfcBuildingStorey/Level 1" does not exist
    And the object "IfcWall/Wall" does not exist

Scenario: Load project elements - load objects filtered by whitelist
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.filter_mode" to "WHITELIST"
    And I set "scene.BIMProjectProperties.filter_query" to "IfcSlab"
    And I set "scene.BIMProjectProperties.should_filter_spatial_elements" to "True"
    And I press "bim.load_project_elements"
    Then the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" is an "IfcSite"
    And the object "IfcBuilding/My Building" is an "IfcBuilding"
    And the object "IfcBuildingStorey/Ground Floor" is an "IfcBuildingStorey"
    And the object "IfcSlab/Slab" is an "IfcSlab"
    And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
    And the object "IfcBuildingStorey/Ground Floor" is in the collection "IfcBuildingStorey/Ground Floor"
    And the object "IfcSlab/Slab" is in the collection "IfcBuildingStorey/Ground Floor"
    And the object "IfcBuildingStorey/Level 1" does not exist
    And the object "IfcWall/Wall" does not exist

Scenario: Load project elements - load objects filtered by blacklist
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.filter_mode" to "BLACKLIST"
    And I set "scene.BIMProjectProperties.filter_query" to "IfcSlab"
    And I set "scene.BIMProjectProperties.should_filter_spatial_elements" to "True"
    And I press "bim.load_project_elements"
    Then the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" is an "IfcSite"
    And the object "IfcBuilding/My Building" is an "IfcBuilding"
    And the object "IfcBuildingStorey/Level 1" is an "IfcBuildingStorey"
    And the object "IfcWall/Wall" is an "IfcWall"
    And the object "IfcElementAssembly/Empty" is an "IfcElementAssembly"
    And the object "IfcBeam/Beam" is an "IfcBeam"
    And the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuilding/My Building" is in the collection "IfcBuilding/My Building"
    And the object "IfcBuildingStorey/Level 1" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcWall/Wall" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcElementAssembly/Empty" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcBeam/Beam" is in the collection "IfcBuildingStorey/Level 1"
    And the object "IfcBuildingStorey/Ground Floor" does not exist
    And the object "IfcSlab/Slab" does not exist

Scenario: Load project elements - load no objects due to filter
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.filter_mode" to "IFC_CLASS"
    And I set "scene.BIMProjectProperties.should_filter_spatial_elements" to "True"
    And I press "bim.load_project_elements"
    Then the object "IfcProject/My Project" is an "IfcProject"
    And the object "IfcSite/My Site" does not exist
    And the object "IfcBuilding/My Building" does not exist
    And the object "IfcBuildingStorey/Ground Floor" does not exist
    And the object "IfcBuildingStorey/Level 1" does not exist
    And the object "IfcSlab/Slab" does not exist
    And the object "IfcWall/Wall" does not exist

Scenario: Load project elements - manual offset of object placements
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/manual-geolocation.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.false_origin_mode" to "MANUAL"
    And I set "scene.BIMProjectProperties.false_origin" to "268388500, 5774506000, 21900"
    And I press "bim.load_project_elements"
    Then the object "IfcPlate/1780 x 270 PRECAST WALL" is at "0,0,0"

Scenario: Load project elements - manual offset of cartesian points
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/manual-geolocation-coords.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.false_origin_mode" to "MANUAL"
    And I set "scene.BIMProjectProperties.false_origin" to "1990711,5971553,22700"
    And I press "bim.load_project_elements"
    Then the object "IfcBuildingElementProxy/NAME" has a vertex at "0,0,0"
    And the object "IfcBuildingElementProxy/NAME" has a vertex at "-1,0,0"
    And the object "IfcBuildingElementProxy/NAME" has a vertex at "0,.5,0"
    And the object "IfcBuildingElementProxy/NAME" has a vertex at "-1,.5,0"
    And the object "IfcBuildingElementProxy/NAME" has a vertex at "-1,.5,2.2"

Scenario: Load project elements - auto offset of object placements
    Given an empty Blender session
    When I press "bim.load_project(filepath='{cwd}/test/files/auto-geolocation.ifc')"
    Then the object "IfcPlate/1780 x 270 PRECAST WALL" is at "0,0,0"

Scenario: Load project elements - auto offset of cartesian points
    Given an empty Blender session
    When I press "bim.load_project(filepath='{cwd}/test/files/manual-geolocation-coords.ifc')"
    Then the object "IfcBuildingElementProxy/NAME" is at "0,0,0"

Scenario: Load project elements - all georeferencing coordinate situations - disabled false origin mode
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/geolocation.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.false_origin_mode" to "DISABLED"
    When I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I press "bim.load_project_elements"
    Then "scene.BIMGeoreferenceProperties.has_blender_offset" is "False"
    And the object "IfcSite/My Site" is at "0,0,0"
    And the object "IfcBuilding/My Building" is at "0,0,0"
    And the object "IfcBuildingStorey/My Storey" is at "0,0,0"
    And the object "IfcActuator/A" is at "7,3,0"
    And the object "IfcActuator/B" is at "6,1,0"
    And the object "IfcActuator/C" is at "0,0,0"
    And the object "IfcActuator/D" is at "13,4,-1"
    And the object "IfcActuator/E" is at "6,3,0"
    And the object "IfcActuator/F" is at "3,3,0"
    And the object "IfcActuator/G" is at "15,6,-1"
    And the object "IfcActuator/H" is at "9,2,0"
    And the object "IfcActuator/I" is at "3,3,0"
    And the object "IfcActuator/J" is at "11,3,-1"
    And the object "IfcActuator/K" is at "10,0,0"

Scenario: Load project elements - all georeferencing coordinate situations - automatic false origin mode
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/geolocation.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.false_origin_mode" to "AUTOMATIC"
    When I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I press "bim.load_project_elements"
    Then "scene.BIMGeoreferenceProperties.has_blender_offset" is "True"
    And "scene.BIMGeoreferenceProperties.model_origin" is "13000.0,4000.0,-1000.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_x" is "13000.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_y" is "4000.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_z" is "-1000.0"
    And the object "IfcSite/My Site" is at "0,0,0"
    And the object "IfcBuilding/My Building" is at "0,0,0"
    And the object "IfcBuildingStorey/My Storey" is at "0,0,0"
    And the object "IfcActuator/A" is at "-6,-1,1"
    And the object "IfcActuator/B" is at "-7,-3,1"
    And the object "IfcActuator/C" is at "0,0,0"
    And the object "IfcActuator/D" is at "0,0,0"
    And the object "IfcActuator/E" is at "-7,-1,1"
    And the object "IfcActuator/F" is at "-10,-1,1"
    And the object "IfcActuator/G" is at "2,2,0"
    And the object "IfcActuator/H" is at "-4,-2,1"
    And the object "IfcActuator/I" is at "-10,-1,1"
    And the object "IfcActuator/J" is at "-2,-1,0"
    And the object "IfcActuator/K" is at "-3,-4,1"

Scenario: Load project elements - all georeferencing coordinate situations - manual false origin mode
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/geolocation.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.false_origin_mode" to "MANUAL"
    When I set "scene.BIMProjectProperties.false_origin" to "10000,0,0"
    When I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I press "bim.load_project_elements"
    Then "scene.BIMGeoreferenceProperties.has_blender_offset" is "True"
    And "scene.BIMGeoreferenceProperties.model_origin" is "10000.0,0.0,0.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_x" is "10000.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_y" is "0.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_z" is "0.0"
    And the object "IfcSite/My Site" is at "0,0,0"
    And the object "IfcBuilding/My Building" is at "0,0,0"
    And the object "IfcBuildingStorey/My Storey" is at "0,0,0"
    And the object "IfcActuator/A" is at "-3,3,0"
    And the object "IfcActuator/B" is at "-4,1,0"
    And the object "IfcActuator/C" is at "0,0,0"
    And the object "IfcActuator/D" is at "3,4,-1"
    And the object "IfcActuator/E" is at "-4,3,0"
    And the object "IfcActuator/F" is at "-7,3,0"
    And the object "IfcActuator/G" is at "5,6,-1"
    And the object "IfcActuator/H" is at "-1,2,0"
    And the object "IfcActuator/I" is at "-7,3,0"
    And the object "IfcActuator/J" is at "1,3,-1"
    And the object "IfcActuator/K" is at "0,0,0"
    And the object "IfcActuator/D" has a cartesian point offset of "31,4,-1"
    And the object "IfcActuator/G" has a cartesian point offset of "-25,6,-1"
    And the object "IfcActuator/J" has a cartesian point offset of "11,3,-1"
    And the object "IfcActuator/D" has a vertex at "3,2,-1"
    And the object "IfcActuator/D" has a vertex at "5,2,-1"
    And the object "IfcActuator/G" has a vertex at "5,4,-1"
    And the object "IfcActuator/G" has a vertex at "7,4,-1"
    And the object "IfcActuator/J" has a vertex at "1,1,-1"
    And the object "IfcActuator/J" has a vertex at "3,1,-1"

Scenario: Load project elements - all georeferencing coordinate situations with an offset site - disabled false origin mode
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/geolocation-offsetsite.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.false_origin_mode" to "DISABLED"
    When I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I press "bim.load_project_elements"
    Then "scene.BIMGeoreferenceProperties.has_blender_offset" is "False"
    And the object "IfcSite/My Site" is at "0,10,0"
    And the object "IfcBuilding/My Building" is at "0,10,0"
    And the object "IfcBuildingStorey/My Storey" is at "0,10,0"
    And the object "IfcActuator/A" is at "5.985,14.71,0"
    And the object "IfcActuator/B" is at "5.5367,12.519,0"
    And the object "IfcActuator/C" is at "0,10,0"
    And the object "IfcActuator/D" is at "11.522,17.228,-1"
    And the object "IfcActuator/E" is at "5.0191,14.451,0"
    And the object "IfcActuator/F" is at "2.1213,13.674,0"
    And the object "IfcActuator/G" is at "12.936,19.678,-1"
    And the object "IfcActuator/H" is at "8.1757,14.261,0"
    And the object "IfcActuator/I" is at "2.1213,13.674,0"
    And the object "IfcActuator/J" is at "9.8487,15.745,-1"
    And the object "IfcActuator/K" is at "9.6593,12.588,0"

Scenario: Load project elements - all georeferencing coordinate situations with an offset site - automatic false origin mode
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/geolocation-offsetsite.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.false_origin_mode" to "AUTOMATIC"
    When I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I press "bim.load_project_elements"
    Then "scene.BIMGeoreferenceProperties.has_blender_offset" is "True"
    And "scene.BIMGeoreferenceProperties.model_origin" is "0.0,10000.0,0.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_x" is "0.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_y" is "10000.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_z" is "0.0"
    And the object "IfcSite/My Site" is at "0,0,0"
    And the object "IfcBuilding/My Building" is at "0,0,0"
    And the object "IfcBuildingStorey/My Storey" is at "0,0,0"
    And the object "IfcActuator/A" is at "7,3,0"
    And the object "IfcActuator/B" is at "6,1,0"
    And the object "IfcActuator/C" is at "0,0,0"
    And the object "IfcActuator/D" is at "13,4,-1"
    And the object "IfcActuator/E" is at "6,3,0"
    And the object "IfcActuator/F" is at "3,3,0"
    And the object "IfcActuator/G" is at "15,6,-1"
    And the object "IfcActuator/H" is at "9,2,0"
    And the object "IfcActuator/I" is at "3,3,0"
    And the object "IfcActuator/J" is at "11,3,-1"
    And the object "IfcActuator/K" is at "10,0,0"

Scenario: Load project elements - all georeferencing coordinate situations with an offset site - manual false origin mode
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/geolocation-offsetsite.ifc', is_advanced=True)"
    And I set "scene.BIMProjectProperties.false_origin_mode" to "MANUAL"
    And I set "scene.BIMProjectProperties.false_origin" to "0,10000,0"
    And I set "scene.BIMProjectProperties.distance_limit" to "5"
    When I press "bim.load_project_elements"
    Then "scene.BIMGeoreferenceProperties.has_blender_offset" is "True"
    And "scene.BIMGeoreferenceProperties.model_origin" is "0.0,10000.0,0.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_x" is "0.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_y" is "10000.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_z" is "0.0"
    And the object "IfcSite/My Site" is at "0,0,0"
    And the object "IfcBuilding/My Building" is at "0,0,0"
    And the object "IfcBuildingStorey/My Storey" is at "0,0,0"
    And the object "IfcActuator/A" is at "5.985,4.71,0"
    And the object "IfcActuator/B" is at "5.5367,2.519,0"
    And the object "IfcActuator/C" is at "0,0,0"
    And the object "IfcActuator/D" is at "11.522,7.228,-1"
    And the object "IfcActuator/E" is at "5.0191,4.451,0"
    And the object "IfcActuator/F" is at "2.1213,3.674,0"
    And the object "IfcActuator/G" is at "12.936,9.678,-1"
    And the object "IfcActuator/H" is at "8.1757,4.261,0"
    And the object "IfcActuator/I" is at "2.1213,3.674,0"
    And the object "IfcActuator/J" is at "9.8487,5.745,-1"
    And the object "IfcActuator/K" is at "9.6593,2.588,0"
    And the object "IfcActuator/D" has a cartesian point offset of "31,4,-1"
    And the object "IfcActuator/G" has a cartesian point offset of "-25,6,-1"
    And the object "IfcActuator/J" has a cartesian point offset of "11,3,-1"
    And the object "IfcActuator/D" has a vertex at "12.039,5.296,-1"
    And the object "IfcActuator/D" has a vertex at "13.971,5.814,-1"
    And the object "IfcActuator/G" has a vertex at "13.454,7.746,-1"
    And the object "IfcActuator/G" has a vertex at "15.385,8.264,-1"
    And the object "IfcActuator/J" has a vertex at "10.366,3.813,-1"
    And the object "IfcActuator/J" has a vertex at "12.298,4.331,-1"

Scenario: Load project elements - all georeferencing coordinate situations with an offset site - manual false origin mode - with custom project north
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/geolocation-offsetsite.ifc', is_advanced=True)"
    And I set "scene.BIMProjectProperties.false_origin_mode" to "MANUAL"
    And I set "scene.BIMProjectProperties.false_origin" to "0,10000,0"
    And I set "scene.BIMProjectProperties.project_north" to "-15"
    And I set "scene.BIMProjectProperties.distance_limit" to "5"
    When I press "bim.load_project_elements"
    Then "scene.BIMGeoreferenceProperties.has_blender_offset" is "True"
    And "scene.BIMGeoreferenceProperties.model_origin" is "0.0,10000.0,0.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_x" is "0.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_y" is "10000.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_z" is "0.0"
    And the object "IfcSite/My Site" is at "0,0,0"
    And the object "IfcBuilding/My Building" is at "0,0,0"
    And the object "IfcBuildingStorey/My Storey" is at "0,0,0"
    And the object "IfcActuator/A" is at "7,3,0"
    And the object "IfcActuator/B" is at "6,1,0"
    And the object "IfcActuator/C" is at "0,0,0"
    And the object "IfcActuator/D" is at "13,4,-1"
    And the object "IfcActuator/E" is at "6,3,0"
    And the object "IfcActuator/F" is at "3,3,0"
    And the object "IfcActuator/G" is at "15,6,-1"
    And the object "IfcActuator/H" is at "9,2,0"
    And the object "IfcActuator/I" is at "3,3,0"
    And the object "IfcActuator/J" is at "11,3,-1"
    And the object "IfcActuator/K" is at "10,0,0"

Scenario: Load project elements - all georeferencing coordinate situations with a map conversion - disabled false origin mode (this should be identical to the situation with no map conversion)
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/geolocation-mapconversion.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.false_origin_mode" to "DISABLED"
    When I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I press "bim.load_project_elements"
    Then "scene.BIMGeoreferenceProperties.has_blender_offset" is "False"
    And the object "IfcSite/My Site" is at "0,0,0"
    And the object "IfcBuilding/My Building" is at "0,0,0"
    And the object "IfcBuildingStorey/My Storey" is at "0,0,0"
    And the object "IfcActuator/A" is at "7,3,0"
    And the object "IfcActuator/B" is at "6,1,0"
    And the object "IfcActuator/C" is at "0,0,0"
    And the object "IfcActuator/D" is at "13,4,-1"
    And the object "IfcActuator/E" is at "6,3,0"
    And the object "IfcActuator/F" is at "3,3,0"
    And the object "IfcActuator/G" is at "15,6,-1"
    And the object "IfcActuator/H" is at "9,2,0"
    And the object "IfcActuator/I" is at "3,3,0"
    And the object "IfcActuator/J" is at "11,3,-1"
    And the object "IfcActuator/K" is at "10,0,0"

Scenario: Load project elements - all georeferencing coordinate situations with a map conversion - automatic false origin mode (this should affect the Blender eastings and northings, which is now different to the Blender offset XYZ, but is otherwise identical to the non-map conversion variant)
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/geolocation-mapconversion.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.false_origin_mode" to "AUTOMATIC"
    When I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I press "bim.load_project_elements"
    Then "scene.BIMGeoreferenceProperties.has_blender_offset" is "True"
    And "scene.BIMGeoreferenceProperties.model_origin" is "28000.0,4000.0,-1000.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_x" is "13000.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_y" is "4000.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_z" is "-1000.0"
    And the object "IfcSite/My Site" is at "0,0,0"
    And the object "IfcBuilding/My Building" is at "0,0,0"
    And the object "IfcBuildingStorey/My Storey" is at "0,0,0"
    And the object "IfcActuator/A" is at "-6,-1,1"
    And the object "IfcActuator/B" is at "-7,-3,1"
    And the object "IfcActuator/C" is at "0,0,0"
    And the object "IfcActuator/D" is at "0,0,0"
    And the object "IfcActuator/E" is at "-7,-1,1"
    And the object "IfcActuator/F" is at "-10,-1,1"
    And the object "IfcActuator/G" is at "2,2,0"
    And the object "IfcActuator/H" is at "-4,-2,1"
    And the object "IfcActuator/I" is at "-10,-1,1"
    And the object "IfcActuator/J" is at "-2,-1,0"
    And the object "IfcActuator/K" is at "-3,-4,1"

Scenario: Load project elements - all georeferencing coordinate situations with a map conversion - manual false origin mode (this should affect the Blender eastings and northings, which is now different to the Blender offset XYZ, but is otherwise identical to the non-map conversion variant)
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/geolocation-mapconversion.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.false_origin_mode" to "MANUAL"
    When I set "scene.BIMProjectProperties.false_origin" to "25000,0,0"
    When I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I press "bim.load_project_elements"
    Then "scene.BIMGeoreferenceProperties.has_blender_offset" is "True"
    And "scene.BIMGeoreferenceProperties.model_origin" is "25000.0,0.0,0.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_x" is "10000.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_y" is "0.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_z" is "0.0"
    And the object "IfcSite/My Site" is at "0,0,0"
    And the object "IfcBuilding/My Building" is at "0,0,0"
    And the object "IfcBuildingStorey/My Storey" is at "0,0,0"
    And the object "IfcActuator/A" is at "-3,3,0"
    And the object "IfcActuator/B" is at "-4,1,0"
    And the object "IfcActuator/C" is at "0,0,0"
    And the object "IfcActuator/D" is at "3,4,-1"
    And the object "IfcActuator/E" is at "-4,3,0"
    And the object "IfcActuator/F" is at "-7,3,0"
    And the object "IfcActuator/G" is at "5,6,-1"
    And the object "IfcActuator/H" is at "-1,2,0"
    And the object "IfcActuator/I" is at "-7,3,0"
    And the object "IfcActuator/J" is at "1,3,-1"
    And the object "IfcActuator/K" is at "0,0,0"
    And the object "IfcActuator/D" has a cartesian point offset of "31,4,-1"
    And the object "IfcActuator/G" has a cartesian point offset of "-25,6,-1"
    And the object "IfcActuator/J" has a cartesian point offset of "11,3,-1"
    And the object "IfcActuator/D" has a vertex at "3,2,-1"
    And the object "IfcActuator/D" has a vertex at "5,2,-1"
    And the object "IfcActuator/G" has a vertex at "5,4,-1"
    And the object "IfcActuator/G" has a vertex at "7,4,-1"
    And the object "IfcActuator/J" has a vertex at "1,1,-1"
    And the object "IfcActuator/J" has a vertex at "3,1,-1"

Scenario: Load project elements - all georeferencing coordinate situations with map conversion and an offset site - disabled false origin mode
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/geolocation-mapconversion-offsetsite.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.false_origin_mode" to "DISABLED"
    When I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I press "bim.load_project_elements"
    Then "scene.BIMGeoreferenceProperties.has_blender_offset" is "False"
    And the object "IfcSite/My Site" is at "0,10,0"
    And the object "IfcBuilding/My Building" is at "0,10,0"
    And the object "IfcBuildingStorey/My Storey" is at "0,10,0"
    And the object "IfcActuator/A" is at "5.985,14.71,0"
    And the object "IfcActuator/B" is at "5.5367,12.519,0"
    And the object "IfcActuator/C" is at "0,10,0"
    And the object "IfcActuator/D" is at "11.522,17.228,-1"
    And the object "IfcActuator/E" is at "5.0191,14.451,0"
    And the object "IfcActuator/F" is at "2.1213,13.674,0"
    And the object "IfcActuator/G" is at "12.936,19.678,-1"
    And the object "IfcActuator/H" is at "8.1757,14.261,0"
    And the object "IfcActuator/I" is at "2.1213,13.674,0"
    And the object "IfcActuator/J" is at "9.8487,15.745,-1"
    And the object "IfcActuator/K" is at "9.6593,12.588,0"

Scenario: Load project elements - all georeferencing coordinate situations with map conversion and an offset site - automatic false origin mode
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/geolocation-mapconversion-offsetsite.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.false_origin_mode" to "AUTOMATIC"
    When I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I press "bim.load_project_elements"
    Then "scene.BIMGeoreferenceProperties.has_blender_offset" is "True"
    And "scene.BIMGeoreferenceProperties.model_origin" is "15000.0,10000.0,0.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_x" is "0.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_y" is "10000.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_z" is "0.0"
    And the object "IfcSite/My Site" is at "0,0,0"
    And the object "IfcBuilding/My Building" is at "0,0,0"
    And the object "IfcBuildingStorey/My Storey" is at "0,0,0"
    And the object "IfcActuator/A" is at "7,3,0"
    And the object "IfcActuator/B" is at "6,1,0"
    And the object "IfcActuator/C" is at "0,0,0"
    And the object "IfcActuator/D" is at "13,4,-1"
    And the object "IfcActuator/E" is at "6,3,0"
    And the object "IfcActuator/F" is at "3,3,0"
    And the object "IfcActuator/G" is at "15,6,-1"
    And the object "IfcActuator/H" is at "9,2,0"
    And the object "IfcActuator/I" is at "3,3,0"
    And the object "IfcActuator/J" is at "11,3,-1"
    And the object "IfcActuator/K" is at "10,0,0"

Scenario: Load project elements - all georeferencing coordinate situations with map conversion and an offset site - manual false origin mode
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/geolocation-mapconversion-offsetsite.ifc', is_advanced=True)"
    When I set "scene.BIMProjectProperties.false_origin_mode" to "MANUAL"
    When I set "scene.BIMProjectProperties.false_origin" to "15000,10000,0"
    When I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I press "bim.load_project_elements"
    Then "scene.BIMGeoreferenceProperties.has_blender_offset" is "True"
    And "scene.BIMGeoreferenceProperties.model_origin" is "15000.0,10000.0,0.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_x" is "0.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_y" is "10000.0"
    And "scene.BIMGeoreferenceProperties.blender_offset_z" is "0.0"
    And the object "IfcSite/My Site" is at "0,0,0"
    And the object "IfcBuilding/My Building" is at "0,0,0"
    And the object "IfcBuildingStorey/My Storey" is at "0,0,0"
    And the object "IfcActuator/A" is at "5.985,4.71,0"
    And the object "IfcActuator/B" is at "5.5367,2.519,0"
    And the object "IfcActuator/C" is at "0,0,0"
    And the object "IfcActuator/D" is at "11.522,7.228,-1"
    And the object "IfcActuator/E" is at "5.0191,4.451,0"
    And the object "IfcActuator/F" is at "2.1213,3.674,0"
    And the object "IfcActuator/G" is at "12.936,9.678,-1"
    And the object "IfcActuator/H" is at "8.1757,4.261,0"
    And the object "IfcActuator/I" is at "2.1213,3.674,0"
    And the object "IfcActuator/J" is at "9.8487,5.745,-1"
    And the object "IfcActuator/K" is at "9.6593,2.588,0"
    And the object "IfcActuator/D" has a cartesian point offset of "31,4,-1"
    And the object "IfcActuator/G" has a cartesian point offset of "-25,6,-1"
    And the object "IfcActuator/J" has a cartesian point offset of "11,3,-1"
    And the object "IfcActuator/D" has a vertex at "12.039,5.296,-1"
    And the object "IfcActuator/D" has a vertex at "13.971,5.814,-1"
    And the object "IfcActuator/G" has a vertex at "13.454,7.746,-1"
    And the object "IfcActuator/G" has a vertex at "15.385,8.264,-1"
    And the object "IfcActuator/J" has a vertex at "10.366,3.813,-1"
    And the object "IfcActuator/J" has a vertex at "12.298,4.331,-1"

Scenario: Link IFC
    Given an empty IFC project
    When I press "bim.link_ifc(filepath='{cwd}/test/files/basic.ifc')"
    Then "scene.BIMProjectProperties.links['{cwd}/test/files/basic.ifc'].is_loaded" is "True"
    And the collection "IfcProject/basic.ifc" exists
    And the object "Chunk" exists
    And the object "Chunk" is placed in the collection "IfcProject/basic.ifc"

Scenario: Link IFC - disabled false origin mode
    Given an empty IFC project
    # Not currently possible via UI
    And I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I set "scene.BIMProjectProperties.false_origin_mode" to "DISABLED"
    When I press "bim.link_ifc(filepath='{cwd}/test/files/geolocation.ifc', use_cache=False)"
    Then the object "Chunk" exists
    And the object "Chunk" has a vertex at "2,2,-1"
    And the object "Chunk" has a vertex at "9,-1,-1"
    And the object "Chunk" has a vertex at "17,4,-1"

Scenario: Link IFC - from an empty IFC project - automatic false origin mode (0,0,0 will be the false origin)
    Given an empty IFC project
    # Not currently possible via UI
    And I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I set "scene.BIMProjectProperties.false_origin_mode" to "AUTOMATIC"
    When I press "bim.link_ifc(filepath='{cwd}/test/files/geolocation.ifc', use_cache=False)"
    Then the object "Chunk" exists
    And the object "Chunk" has a vertex at "2,2,-1"
    And the object "Chunk" has a vertex at "9,-1,-1"
    And the object "Chunk" has a vertex at "17,4,-1"

Scenario: Link IFC - from an empty Blender session - automatic false origin mode (a new false origin will be detected)
    Given an empty Blender session
    # Not currently possible via UI
    And I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I set "scene.BIMProjectProperties.false_origin_mode" to "AUTOMATIC"
    When I press "bim.link_ifc(filepath='{cwd}/test/files/geolocation.ifc', use_cache=False)"
    Then the object "Chunk" exists
    And the object "Chunk" has a vertex at "-11,-2,0"
    And the object "Chunk" has a vertex at "-4,-5,0"
    And the object "Chunk" has a vertex at "4,0,0"

Scenario: Link IFC - manual false origin mode
    Given an empty Blender session
    # Not currently possible via UI
    And I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I set "scene.BIMProjectProperties.false_origin_mode" to "MANUAL"
    And I set "scene.BIMProjectProperties.false_origin" to "10000,0,0"
    When I press "bim.link_ifc(filepath='{cwd}/test/files/geolocation.ifc', use_cache=False)"
    Then the object "Chunk" exists
    And the object "Chunk" has a vertex at "-8,2,-1"
    And the object "Chunk" has a vertex at "-1,-1,-1"
    And the object "Chunk" has a vertex at "7,4,-1"

Scenario: Link IFC - automatic false origin mode - two different false origins and project norths - grid north is up because we start with geolocation.ifc
    Given an empty Blender session
    # Not currently possible via UI
    And I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I set "scene.BIMProjectProperties.false_origin_mode" to "AUTOMATIC"
    When I press "bim.link_ifc(filepath='{cwd}/test/files/geolocation.ifc', use_cache=False)"
    And I press "bim.link_ifc(filepath='{cwd}/test/files/geolocation-mapconversion-angle.ifc', use_cache=False)"
    Then the object "Col:IfcProject/geolocation.ifc:Chunk" exists
    And the object "Col:IfcProject/geolocation-mapconversion-angle.ifc:Chunk" exists
    And the object "Col:IfcProject/geolocation.ifc:Chunk" has a vertex at "-11,-2,0"
    And the object "Col:IfcProject/geolocation.ifc:Chunk" has a vertex at "-4,-5,0"
    And the object "Col:IfcProject/geolocation.ifc:Chunk" has a vertex at "4,0,0"
    And the object "Col:IfcProject/geolocation-mapconversion-angle.ifc:Chunk" has a vertex at "4.732,-3.268,0"
    And the object "Col:IfcProject/geolocation-mapconversion-angle.ifc:Chunk" has a vertex at "9.294,-9.366,0"
    And the object "Col:IfcProject/geolocation-mapconversion-angle.ifc:Chunk" has a vertex at "18.722,-9.036,0"

Scenario: Link IFC - automatic false origin mode - two different false origins and project norths - project north is up because we start with geolocation-mapconversion-angle.ifc
    Given an empty Blender session
    # Not currently possible via UI
    And I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I set "scene.BIMProjectProperties.false_origin_mode" to "AUTOMATIC"
    When I press "bim.link_ifc(filepath='{cwd}/test/files/geolocation-mapconversion-angle.ifc', use_cache=False)"
    And I press "bim.link_ifc(filepath='{cwd}/test/files/geolocation.ifc', use_cache=False)"
    Then the object "Col:IfcProject/geolocation.ifc:Chunk" exists
    And the object "Col:IfcProject/geolocation-mapconversion-angle.ifc:Chunk" exists
    And the object "Col:IfcProject/geolocation-mapconversion-angle.ifc:Chunk" has a vertex at "-11,-2,0"
    And the object "Col:IfcProject/geolocation-mapconversion-angle.ifc:Chunk" has a vertex at "-4,-5,0"
    And the object "Col:IfcProject/geolocation-mapconversion-angle.ifc:Chunk" has a vertex at "4,0,0"
    And the object "Col:IfcProject/geolocation.ifc:Chunk" has a vertex at "-25.258,-8.768,0"
    And the object "Col:IfcProject/geolocation.ifc:Chunk" has a vertex at "-17.696,-7.866,0"
    And the object "Col:IfcProject/geolocation.ifc:Chunk" has a vertex at "-13.268,0.464,0"

Scenario: Link IFC - automatic false origin mode - three identical false origins but different project and map units
    Given an empty Blender session
    # Not currently possible via UI
    And I set "scene.BIMProjectProperties.distance_limit" to "5"
    And I set "scene.BIMProjectProperties.false_origin_mode" to "AUTOMATIC"
    When I press "bim.link_ifc(filepath='{cwd}/test/files/geolocation-unit1.ifc', use_cache=False)"
    And I press "bim.link_ifc(filepath='{cwd}/test/files/geolocation-unit2.ifc', use_cache=False)"
    And I press "bim.link_ifc(filepath='{cwd}/test/files/geolocation-unit3.ifc', use_cache=False)"
    Then the object "Col:IfcProject/geolocation-unit1.ifc:Chunk" exists
    And the object "Col:IfcProject/geolocation-unit2.ifc:Chunk" exists
    And the object "Col:IfcProject/geolocation-unit3.ifc:Chunk" exists
    And the object "Col:IfcProject/geolocation-unit1.ifc:Chunk" has a vertex at "7.294,-5.366,-1"
    And the object "Col:IfcProject/geolocation-unit2.ifc:Chunk" has a vertex at "7.294,-5.366,-1"
    And the object "Col:IfcProject/geolocation-unit3.ifc:Chunk" has a vertex at "7.294,-5.366,-1"

Scenario: Toggle link visibility - wireframe mode
    Given an empty IFC project
    And I press "bim.link_ifc(filepath='{cwd}/test/files/basic.ifc')"
    When I press "bim.toggle_link_visibility(link='{cwd}/test/files/basic.ifc', mode='WIREFRAME')"
    Then "scene.BIMProjectProperties.links['{cwd}/test/files/basic.ifc'].is_wireframe" is "True"
    And the object "Chunk" should display as "WIRE"
    When I press "bim.toggle_link_visibility(link='{cwd}/test/files/basic.ifc', mode='WIREFRAME')"
    Then "scene.BIMProjectProperties.links['{cwd}/test/files/basic.ifc'].is_wireframe" is "False"
    And the object "Chunk" should display as "TEXTURED"

Scenario: Toggle link selectability
    Given an empty IFC project
    And I press "bim.link_ifc(filepath='{cwd}/test/files/basic.ifc')"
    When I press "bim.toggle_link_selectability(link='{cwd}/test/files/basic.ifc')"
    Then "scene.BIMProjectProperties.links['{cwd}/test/files/basic.ifc'].is_selectable" is "False"
    And the collection "IfcProject/basic.ifc" is unselectable
    When I press "bim.toggle_link_selectability(link='{cwd}/test/files/basic.ifc')"
    Then "scene.BIMProjectProperties.links['{cwd}/test/files/basic.ifc'].is_selectable" is "True"
    And the collection "IfcProject/basic.ifc" is selectable

Scenario: Toggle link visibility - visible mode
    Given an empty IFC project
    And I press "bim.link_ifc(filepath='{cwd}/test/files/basic.ifc')"
    When I press "bim.toggle_link_visibility(link='{cwd}/test/files/basic.ifc', mode='VISIBLE')"
    Then "scene.BIMProjectProperties.links['{cwd}/test/files/basic.ifc'].is_hidden" is "True"
    And the collection "IfcProject/basic.ifc" exclude status is "True"
    When I press "bim.toggle_link_visibility(link='{cwd}/test/files/basic.ifc', mode='VISIBLE')"
    Then "scene.BIMProjectProperties.links['{cwd}/test/files/basic.ifc'].is_hidden" is "False"
    And the collection "IfcProject/basic.ifc" exclude status is "False"

Scenario: Unload link
    Given an empty Blender session
    And I press "bim.link_ifc(filepath='{cwd}/test/files/basic.ifc')"
    When I press "bim.unload_link(filepath='{cwd}/test/files/basic.ifc')"
    Then "scene.BIMProjectProperties.links['{cwd}/test/files/basic.ifc'].is_loaded" is "False"
    And the collection "IfcProject/basic.ifc" does not exist

Scenario: Load link
    Given an empty Blender session
    And I press "bim.link_ifc(filepath='{cwd}/test/files/basic.ifc')"
    And I press "bim.unload_link(filepath='{cwd}/test/files/basic.ifc')"
    When I press "bim.load_link(filepath='{cwd}/test/files/basic.ifc')"
    Then "scene.BIMProjectProperties.links['{cwd}/test/files/basic.ifc'].is_loaded" is "True"
    And the collection "IfcProject/basic.ifc" exists in viewlayer

Scenario: Unlink IFC
    Given an empty Blender session
    And I press "bim.link_ifc(filepath='{cwd}/test/files/basic.ifc')"
    And I press "bim.unload_link(filepath='{cwd}/test/files/basic.ifc')"
    When I press "bim.unlink_ifc(filepath='{cwd}/test/files/basic.ifc')"
    Then "scene.BIMProjectProperties.links.get('{cwd}/test/files/basic.ifc')" is "None"
    And "scene.collection.children.get('IfcProject/basic.ifc')" is "None"
    And the object "Chunk" does not exist

Scenario: Export IFC - blank project
    Given an empty IFC project
    When I press "bim.save_project(filepath='{cwd}/test/files/temp/export.ifc')"
    Then nothing happens

Scenario: Export IFC - with basic contents
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc')"
    When I press "bim.save_project(filepath='{cwd}/test/files/temp/export.ifc')"
    Then "scene.BIMProperties.ifc_file" is "{cwd}/test/files/temp/export.ifc"

Scenario: Export IFC - with basic contents and saving as another file
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc')"
    When I press "bim.save_project(filepath='{cwd}/test/files/temp/export.ifc', should_save_as=True)"
    Then "scene.BIMProperties.ifc_file" is "{cwd}/test/files/temp/export.ifc"

Scenario: Export IFC - with basic contents and saving as IfcJSON where import is not supported
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc')"
    When I press "bim.save_project(filepath='{cwd}/test/files/temp/export.ifcjson', should_save_as=True)"
    Then "scene.BIMProperties.ifc_file" is "{cwd}/test/files/basic.ifc"

Scenario: Export IFC - with basic contents and round-tripping an IfcZip
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc')"
    When I press "bim.save_project(filepath='{cwd}/test/files/temp/export.ifczip', should_save_as=True)"
    Then "scene.BIMProperties.ifc_file" is "{cwd}/test/files/basic.ifc"
    When an empty Blender session is started
    And I press "bim.load_project(filepath='{cwd}/test/files/temp/export.ifczip')"
    Then the object "IfcProject/My Project" is an "IfcProject"

Scenario: Export IFC - with basic contents and saving as a relative path
    Given an empty Blender session
    And I press "bim.load_project(filepath='{cwd}/test/files/basic.ifc')"
    When I press "wm.save_mainfile(filepath='{cwd}/test/files/temp/export.blend')"
    And I press "bim.save_project(filepath='{cwd}/test/files/temp/export.ifc', use_relative_path=True, save_as_invoked=True)"
    Then "scene.BIMProperties.ifc_file" is "export.ifc"

Scenario: Export IFC - with deleted objects synchronised
    Given an empty IFC project
    When the object "IfcBuildingStorey/My Storey" is selected
    And I delete the selected objects
    And I press "bim.save_project(filepath='{cwd}/test/files/temp/export.ifc')"
    And an empty Blender session is started
    And I press "bim.load_project(filepath='{cwd}/test/files/temp/export.ifc')"
    Then the object "IfcBuildingStorey/My Storey" does not exist

Scenario: Export IFC - with moved object location synchronised
    Given an empty IFC project
    When the object "IfcBuildingStorey/My Storey" is moved to "0,0,1"
    And I press "bim.save_project(filepath='{cwd}/test/files/temp/export.ifc')"
    And an empty Blender session is started
    And I press "bim.load_project(filepath='{cwd}/test/files/temp/export.ifc')"
    Then the object "IfcBuildingStorey/My Storey" is at "0,0,1"

Scenario: Export IFC - with moved grid axis location synchronised
    Given an empty IFC project
    And I press "mesh.add_grid"
    When the object "IfcGridAxis/01" is moved to "1,0,0"
    And I press "bim.save_project(filepath='{cwd}/test/files/temp/export.ifc')"
    And an empty Blender session is started
    And I press "bim.load_project(filepath='{cwd}/test/files/temp/export.ifc')"
    Then the object "IfcGridAxis/01" bottom left corner is at "1,-2,0"

Scenario: Export IFC - with changed object scale synchronised
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When the object "IfcWall/Cube" is scaled to "2"
    And I press "bim.save_project(filepath='{cwd}/test/files/temp/export.ifc')"
    And an empty Blender session is started
    And I press "bim.load_project(filepath='{cwd}/test/files/temp/export.ifc')"
    Then the object "IfcWall/Cube" dimensions are "4,4,4"
